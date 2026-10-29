# ******************************************************************************
#    Copyright (c) 2026 RoXimn <roximn148@gmail.com>
#    This source code is licensed under the MIT license found in the
#    LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""
The :py:mod:`romanalfaz.cli` module is the command line interface for
SymSpell vocabulary files.

A vocabulary file stores one ``word$frequency`` entry per line. The commands
operate on such files through a selected normalization method (see
:py:mod:`romanalfaz.normalization`):

- ``validate`` checks a file for malformed lines, non-canonical spellings,
  words that normalize to empty or cannot be romanized, and duplicate
  canonical forms.
- ``normalize`` rewrites a file in canonical form, summing the frequencies of
  entries that normalize to the same word.
- ``words`` exports the canonical words of a file, sorted, without
  frequencies.
- ``merge`` unions two files, summing the frequencies of shared words.
- ``subtract`` removes the words of a second file from a first one.
- ``list`` describes the available normalization methods.

Commands never write in place unless asked to: the target of a rewrite is an
output path, and ``normalize`` accepts ``--in-place`` or ``--preview`` as
explicit alternatives.
"""

import argparse
import sys
from pathlib import Path
from typing import NamedTuple

from .algorithm import tafseerUrduAr2Rm
from .normalization import NORMALIZATION_METHODS, NormalizationMethod

SEPARATOR = "$"


# ******************************************************************************
class SymEntry(NamedTuple):
    """One parsed ``word$frequency`` entry of a vocabulary file."""

    lineno: int
    """(int): The 1-based line number the entry was read from."""
    word: str
    """(str): The word exactly as written in the file."""
    frequency: int
    """(int): The entry's frequency, always positive."""


# ******************************************************************************
class Issue(NamedTuple):
    """A problem found in a vocabulary file."""

    lineno: int
    """(int): The 1-based line number the problem was found on."""
    message: str
    """(str): A human-readable description of the problem."""


# ******************************************************************************
#                                  PARSING
# ******************************************************************************
def parseSymFile(symPath: Path) -> tuple[list[SymEntry], list[Issue]]:
    """
    Parses a SymSpell vocabulary file.

    Blank lines are reported as issues rather than skipped. Every other line
    is stripped and split at its last ``$``: the part before it is the word and
    the part after it is the frequency. A malformed line is recorded as an
    :py:class:`Issue` and skipped, so one bad line never hides the rest of the
    file.

    Args:
        symPath (Path): The vocabulary file to read.

    Returns:
        tuple[list[SymEntry], list[Issue]]: The parsed entries and the
        problems found while parsing.

    Raises:
        OSError: If the file cannot be read.
        UnicodeDecodeError: If the file is not valid UTF-8.

    Example:
        >>> from pathlib import Path
        >>> entries, issues = parseSymFile(Path("words.sym"))
        >>> [(entry.word, entry.frequency) for entry in entries]
        [('کتاب', 4643)]
    """
    text = symPath.read_text(encoding="utf-8")
    entries: list[SymEntry] = []
    issues: list[Issue] = []

    for lineno, rawLine in enumerate(text.splitlines(), start=1):
        line = rawLine.strip()
        if not line:
            issues.append(Issue(lineno, "blank line (expected word$frequency)"))
            continue
        if SEPARATOR not in line:
            issues.append(Issue(lineno, "missing separator (expected word$frequency)"))
            continue

        word, _, frequencyText = line.rpartition(SEPARATOR)
        if not word:
            issues.append(Issue(lineno, "empty word before separator"))
            continue

        try:
            frequency = int(frequencyText)
        except ValueError:
            issues.append(
                Issue(lineno, f"frequency is not an integer: {frequencyText!r}")
            )
            continue

        if frequency < 1:
            issues.append(Issue(lineno, f"frequency must be positive: {frequency}"))
            continue

        entries.append(SymEntry(lineno, word, frequency))

    return entries, issues


# ******************************************************************************
#                                CANONICALIZATION
# ******************************************************************************
def findIssues(entries: list[SymEntry], method: NormalizationMethod) -> list[Issue]:
    """
    Finds the words of a parsed file that the chosen method cannot accept.

    A word is reported when it normalizes to empty, when its spelling is not
    already canonical, when it contains characters that cannot be romanized,
    or when it collides with an earlier word after normalization.

    Args:
        entries (list[SymEntry]): The parsed entries to check.
        method (NormalizationMethod): The normalization method to check with.

    Returns:
        list[Issue]: Every problem found, in line order.

    Example:
        >>> issues = findIssues(entries, NORMALIZATION_METHODS["urdu-spell"])
    """
    issues: list[Issue] = []
    firstSeen: dict[str, int] = {}

    for entry in entries:
        canonical = method.normalize(entry.word)
        if not canonical:
            issues.append(Issue(entry.lineno, "word normalizes to empty"))
            continue

        if canonical != entry.word:
            issues.append(
                Issue(
                    entry.lineno,
                    f"word is not canonical: {entry.word!r} -> {canonical!r}",
                )
            )

        _, undefined = tafseerUrduAr2Rm(entry.word, keep=False)
        if undefined:
            issues.append(
                Issue(
                    entry.lineno,
                    f"word has {undefined} unmapped character(s) for romanization",
                )
            )

        if canonical in firstSeen:
            issues.append(
                Issue(
                    entry.lineno,
                    f"duplicate canonical form {canonical!r} "
                    f"(first seen at line {firstSeen[canonical]})",
                )
            )
        else:
            firstSeen[canonical] = entry.lineno

    return issues


# ******************************************************************************
def canonicalize(
    entries: list[SymEntry], method: NormalizationMethod
) -> tuple[
    list[SymEntry],
    list[tuple[int, str, str]],
    list[tuple[int, str, str, int]],
    list[SymEntry],
]:
    """
    Rewrites entries in the canonical form of the chosen method.

    Entries that normalize to the same word are merged into one, keeping the
    line number of the first occurrence and summing the frequencies. Entries
    that normalize to empty are dropped: they cannot be words.

    Args:
        entries (list[SymEntry]): The parsed entries to canonicalize.
        method (NormalizationMethod): The normalization method to apply.

    Returns:
        tuple: A 4-tuple of:

        - list[SymEntry]: The canonical entries, in first-occurrence order.
        - list[tuple[int, str, str]]: ``(lineno, word, canonical)`` for every
          entry whose spelling changed.
        - list[tuple[int, str, str, int]]: ``(lineno, word, canonical,
          summed_frequency)`` for every entry merged into an earlier one.
        - list[SymEntry]: The entries dropped because they normalized to empty.

    Example:
        >>> entries = [SymEntry(1, "ﺏ", 2), SymEntry(2, "ب", 3)]
        >>> normalized, _, _, _ = canonicalize(entries, NORMALIZATION_METHODS["urdu-spell"])
        >>> [(entry.word, entry.frequency) for entry in normalized]
        [('ب', 5)]
    """
    normalized: list[SymEntry] = []
    index: dict[str, int] = {}
    changed: list[tuple[int, str, str]] = []
    merged: list[tuple[int, str, str, int]] = []
    dropped: list[SymEntry] = []

    for entry in entries:
        canonical = method.normalize(entry.word)
        if not canonical:
            dropped.append(entry)
            continue

        position = index.get(canonical)
        if position is None:
            index[canonical] = len(normalized)
            normalized.append(SymEntry(entry.lineno, canonical, entry.frequency))
            if canonical != entry.word:
                changed.append((entry.lineno, entry.word, canonical))
            continue

        previous = normalized[position]
        total = previous.frequency + entry.frequency
        normalized[position] = SymEntry(previous.lineno, canonical, total)
        merged.append((entry.lineno, entry.word, canonical, total))

    return normalized, changed, merged, dropped


# ******************************************************************************
def mergeEntries(
    first: list[SymEntry], second: list[SymEntry], method: NormalizationMethod
) -> list[SymEntry]:
    """
    Unions two entry lists by canonical word.

    The result keeps the order of the first list, followed by the words that
    are new in the second list. Shared words get one entry whose frequency is
    the sum of both.

    Args:
        first (list[SymEntry]): The entries whose order is preserved first.
        second (list[SymEntry]): The entries added after the first list.
        method (NormalizationMethod): The normalization method to apply.

    Returns:
        list[SymEntry]: The merged canonical entries.

    Example:
        >>> merged = mergeEntries(first, second, NORMALIZATION_METHODS["urdu-spell"])
    """
    left, *_ = canonicalize(first, method)
    right, *_ = canonicalize(second, method)

    result = list(left)
    index = {entry.word: position for position, entry in enumerate(result)}
    for entry in right:
        position = index.get(entry.word)
        if position is None:
            index[entry.word] = len(result)
            result.append(entry)
            continue
        previous = result[position]
        result[position] = SymEntry(
            previous.lineno, previous.word, previous.frequency + entry.frequency
        )

    return result


# ******************************************************************************
def subtractEntries(
    first: list[SymEntry], second: list[SymEntry], method: NormalizationMethod
) -> list[SymEntry]:
    """
    Removes the words of the second list from the first one.

    Words are matched by canonical form, and survivors keep the frequency
    they had in the first list.

    Args:
        first (list[SymEntry]): The entries to keep from.
        second (list[SymEntry]): The entries to remove.
        method (NormalizationMethod): The normalization method to apply.

    Returns:
        list[SymEntry]: The canonical entries of the first list that are not
        in the second list.

    Example:
        >>> remaining = subtractEntries(first, second, NORMALIZATION_METHODS["urdu-spell"])
    """
    left, *_ = canonicalize(first, method)
    right, *_ = canonicalize(second, method)
    excluded = {entry.word for entry in right}

    return [entry for entry in left if entry.word not in excluded]


# ******************************************************************************
#                                  WRITING
# ******************************************************************************
def writeSymFile(path: Path, entries: list[SymEntry]) -> None:
    """
    Writes entries as a SymSpell vocabulary file.

    The file is UTF-8 with LF line endings, one ``word$frequency`` entry per
    line, regardless of the platform's native line ending.

    Args:
        path (Path): The file to write.
        entries (list[SymEntry]): The entries to write, in order.

    Raises:
        OSError: If the file cannot be written.

    Example:
        >>> writeSymFile(Path("out.sym"), entries)
    """
    content = "".join(
        f"{entry.word}{SEPARATOR}{entry.frequency}\n" for entry in entries
    )
    path.write_text(content, encoding="utf-8", newline="\n")


# ******************************************************************************
def writeLines(path: Path, lines: list[str]) -> None:
    """
    Writes lines as a UTF-8 text file with LF line endings.

    Args:
        path (Path): The file to write.
        lines (list[str]): The lines to write, in order.

    Raises:
        OSError: If the file cannot be written.

    Example:
        >>> writeLines(Path("words.txt"), ["ب"])
    """
    path.write_text(
        "".join(f"{line}\n" for line in lines), encoding="utf-8", newline="\n"
    )


# ******************************************************************************
#                                 COMMANDS
# ******************************************************************************
def commandValidate(args: argparse.Namespace) -> int:
    """
    Checks a vocabulary file and reports every problem it finds.

    Args:
        args (argparse.Namespace): The parsed command arguments.

    Returns:
        int: ``0`` when the file has no issues, ``1`` otherwise.
    """
    method = NORMALIZATION_METHODS[args.normalize]
    entries, issues = parseSymFile(args.input)
    issues.extend(findIssues(entries, method))
    issues.sort(key=lambda issue: issue.lineno)

    if not issues:
        print(f"{args.input}: no issues found ({len(entries)} words)")
        return 0

    for issue in issues:
        print(f"line {issue.lineno}: {issue.message}")
    print(f"{args.input}: {len(issues)} issue(s) in {len(entries)} words")
    return 1


# ******************************************************************************
def commandNormalize(args: argparse.Namespace) -> int:
    """
    Rewrites a vocabulary file in canonical form, or previews the rewrite.

    Args:
        args (argparse.Namespace): The parsed command arguments.

    Returns:
        int: ``0`` on success.
    """
    method = NORMALIZATION_METHODS[args.normalize]
    entries, issues = parseSymFile(args.input)
    _reportParseIssues(issues)

    normalized, changed, merged, dropped = canonicalize(entries, method)

    if args.preview:
        _printPreview(entries, normalized, changed, merged, dropped)
        return 0

    target = args.input if args.in_place else args.output
    writeSymFile(target, normalized)
    print(f"wrote {len(normalized)} words to {target}", file=sys.stderr)
    return 0


# ******************************************************************************
def commandWords(args: argparse.Namespace) -> int:
    """
    Exports the canonical words of a vocabulary file, sorted, without
    frequencies.

    Args:
        args (argparse.Namespace): The parsed command arguments.

    Returns:
        int: ``0`` on success.
    """
    method = NORMALIZATION_METHODS[args.normalize]
    entries, issues = parseSymFile(args.input)
    _reportParseIssues(issues)

    words = sorted({method.normalize(entry.word) for entry in entries} - {""})

    if args.output is None:
        sys.stdout.write("".join(f"{word}\n" for word in words))
    else:
        writeLines(args.output, words)
    return 0


# ******************************************************************************
def commandMerge(args: argparse.Namespace) -> int:
    """
    Unions two vocabulary files by canonical word.

    Args:
        args (argparse.Namespace): The parsed command arguments.

    Returns:
        int: ``0`` on success.
    """
    method = NORMALIZATION_METHODS[args.normalize]
    first, firstIssues = parseSymFile(args.first)
    second, secondIssues = parseSymFile(args.second)
    _reportParseIssues(firstIssues)
    _reportParseIssues(secondIssues)

    writeSymFile(args.output, mergeEntries(first, second, method))
    return 0


# ******************************************************************************
def commandSubtract(args: argparse.Namespace) -> int:
    """
    Removes the words of a second vocabulary file from a first one.

    Args:
        args (argparse.Namespace): The parsed command arguments.

    Returns:
        int: ``0`` on success.
    """
    method = NORMALIZATION_METHODS[args.normalize]
    first, firstIssues = parseSymFile(args.first)
    second, secondIssues = parseSymFile(args.second)
    _reportParseIssues(firstIssues)
    _reportParseIssues(secondIssues)

    writeSymFile(args.output, subtractEntries(first, second, method))
    return 0


# ******************************************************************************
def commandList(args: argparse.Namespace) -> int:
    """
    Describes every normalization method, its scope, and its pipeline.

    Args:
        args (argparse.Namespace): The parsed command arguments.

    Returns:
        int: ``0`` on success.
    """
    for method in NORMALIZATION_METHODS.values():
        print(method.name)
        print(f"  scope: {method.description}")
        print("  pipeline:")
        for step, stage in enumerate(method.stages, start=1):
            print(f"    {step}. {stage}")
    return 0


# ******************************************************************************
def _reportParseIssues(issues: list[Issue]) -> None:
    """Reports malformed lines on stderr without stopping the command."""
    for issue in issues:
        print(f"warning: line {issue.lineno}: {issue.message}", file=sys.stderr)


# ******************************************************************************
def _printPreview(
    source: list[SymEntry],
    normalized: list[SymEntry],
    changed: list[tuple[int, str, str]],
    merged: list[tuple[int, str, str, int]],
    dropped: list[SymEntry],
) -> None:
    """Prints what ``normalize`` would change, without writing anything."""
    for lineno, word, canonical in changed:
        print(f"line {lineno}: changed {word!r} -> {canonical!r}")
    for lineno, word, canonical, total in merged:
        if word == canonical:
            print(f"line {lineno}: merged {word!r} (frequency {total})")
        else:
            print(
                f"line {lineno}: merged {word!r} into {canonical!r} (frequency {total})"
            )
    for entry in dropped:
        print(f"line {entry.lineno}: dropped {entry.word!r} (normalizes to empty)")

    print(
        f"{len(source)} entries -> {len(normalized)} words: "
        f"{len(changed)} changed, {len(merged)} merged, {len(dropped)} dropped"
    )


# ******************************************************************************
#                              ARGUMENT PARSING
# ******************************************************************************
def _addMethodArgument(parser: argparse.ArgumentParser) -> None:
    """Adds the ``--normalize`` method selection to a file command."""
    parser.add_argument(
        "--normalize",
        choices=list(NORMALIZATION_METHODS),
        default="urdu-spell",
        help="normalization method to apply (default: %(default)s)",
    )


# ******************************************************************************
def buildParser() -> argparse.ArgumentParser:
    """
    Builds the command line parser.

    Returns:
        argparse.ArgumentParser: The parser with every subcommand registered.

    Example:
        >>> buildParser().parse_args(["list"]).command
        'list'
    """
    parser = argparse.ArgumentParser(
        prog="romanalfaz",
        description="Inspect and rewrite SymSpell vocabulary files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate", help="check a vocabulary file for issues"
    )
    validate.add_argument("input", type=Path, help="vocabulary file to check")
    _addMethodArgument(validate)

    normalize = subparsers.add_parser(
        "normalize", help="rewrite a vocabulary file in canonical form"
    )
    normalize.add_argument("input", type=Path, help="vocabulary file to normalize")
    target = normalize.add_mutually_exclusive_group()
    target.add_argument(
        "-o", "--output", type=Path, help="write the result to this file"
    )
    target.add_argument(
        "--in-place", action="store_true", help="rewrite the input file itself"
    )
    target.add_argument(
        "--preview", action="store_true", help="report changes without writing"
    )
    _addMethodArgument(normalize)

    words = subparsers.add_parser("words", help="export the canonical words, sorted")
    words.add_argument("input", type=Path, help="vocabulary file to read")
    words.add_argument("-o", "--output", type=Path, help="write the words to this file")
    _addMethodArgument(words)

    merge = subparsers.add_parser(
        "merge", help="union two files, summing shared frequencies"
    )
    merge.add_argument("first", type=Path, help="file whose order is preserved first")
    merge.add_argument("second", type=Path, help="file whose new words are appended")
    merge.add_argument(
        "-o", "--output", type=Path, required=True, help="write the result here"
    )
    _addMethodArgument(merge)

    subtract = subparsers.add_parser(
        "subtract", help="remove the words of a second file"
    )
    subtract.add_argument("first", type=Path, help="file to keep words from")
    subtract.add_argument("second", type=Path, help="file whose words are removed")
    subtract.add_argument(
        "-o", "--output", type=Path, required=True, help="write the result here"
    )
    _addMethodArgument(subtract)

    subparsers.add_parser("list", help="describe the available normalization methods")

    return parser


# ******************************************************************************
_HANDLERS = {
    "validate": commandValidate,
    "normalize": commandNormalize,
    "words": commandWords,
    "merge": commandMerge,
    "subtract": commandSubtract,
    "list": commandList,
}


# ******************************************************************************
#                                    MAIN
# ******************************************************************************
def _configureIoEncoding() -> None:
    """
    Makes the CLI write UTF-8 to standard output and standard error.

    The console's encoding, or a redirected stream's locale encoding, may not
    represent Urdu characters (cp1252 is a common example on Windows). CLI
    text is UTF-8 by contract, so the standard streams are switched to UTF-8
    when their encoding is something else.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        encoding = getattr(stream, "encoding", None) or ""
        if encoding.lower().replace("-", "") == "utf8":
            continue
        reconfigure(encoding="utf-8")


# ******************************************************************************
def main(argv: list[str] | None = None) -> int:
    """
    Runs the command line interface.

    Args:
        argv (list[str] | None): The arguments to parse, or ``None`` to read
            ``sys.argv``.

    Returns:
        int: The process exit code: ``0`` on success, ``1`` for an issue or an
        I/O error, and ``2`` for a usage error (through argparse).

    Example:
        >>> main(["list"])  # doctest: +SKIP
        0
    """
    _configureIoEncoding()
    parser = buildParser()
    args = parser.parse_args(argv)

    if args.command == "normalize" and not (
        args.output or args.in_place or args.preview
    ):
        parser.error("normalize requires one of -o/--output, --in-place, or --preview")

    try:
        return _HANDLERS[args.command](args)
    except (OSError, UnicodeDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


# ******************************************************************************
if __name__ == "__main__":
    sys.exit(main())


# ******************************************************************************
