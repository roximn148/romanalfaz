# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
import os
import subprocess
import sys
from pathlib import Path

import pytest

from romanalfaz.cli import main, parseSymFile


# ******************************************************************************
class SymFileFixture:
    """Shared fixture: writes SymSpell content to a temporary .sym file."""

    @pytest.fixture
    def symFile(self, tmp_path):
        def make(content: str, name: str = "words.sym") -> Path:
            path = tmp_path / name
            path.write_text(content, encoding="utf-8")
            return path

        return make


# ******************************************************************************
class TestParseSymFile(SymFileFixture):
    def testReadsEntriesAndLineNumbers(self, symFile):
        """Parses word$frequency lines and records their 1-based line numbers."""
        entries, issues = parseSymFile(symFile("\u0628$3\n\u062a$7\n"))
        assert [(e.word, e.frequency, e.lineno) for e in entries] == [
            ("\u0628", 3, 1),
            ("\u062a", 7, 2),
        ]
        assert issues == []

    def testReportsBlankLines(self, symFile):
        """Blank lines are reported rather than silently skipped."""
        entries, issues = parseSymFile(symFile("\u0628$3\n\n\u062a$7\n"))
        assert [(e.word, e.lineno) for e in entries] == [("\u0628", 1), ("\u062a", 3)]
        assert [issue.lineno for issue in issues] == [2]
        assert "blank" in issues[0].message

    def testStripsSurroundingWhitespace(self, symFile):
        """Leading and trailing whitespace on a line is ignored."""
        entries, _ = parseSymFile(symFile("  \u0628$3  \n"))
        assert [(e.word, e.frequency) for e in entries] == [("\u0628", 3)]

    def testWordMayContainSeparator(self, symFile):
        """Splits at the last separator, matching the Vocabulary.load parser."""
        entries, _ = parseSymFile(symFile("a$b$5\n"))
        assert [(e.word, e.frequency) for e in entries] == [("a$b", 5)]

    def testReportsMissingSeparator(self, symFile):
        """A line without a separator is reported and skipped."""
        entries, issues = parseSymFile(symFile("\u0628\n"))
        assert entries == []
        assert "separator" in issues[0].message

    def testReportsNonIntegerFrequency(self, symFile):
        """A frequency that is not an integer is reported and skipped."""
        entries, issues = parseSymFile(symFile("\u0628$abc\n"))
        assert entries == []
        assert "integer" in issues[0].message

    def testReportsNonPositiveFrequency(self, symFile):
        """Zero or negative frequencies are rejected like Vocabulary.add does."""
        entries, issues = parseSymFile(symFile("\u0628$0\n"))
        assert entries == []
        assert "positive" in issues[0].message

    def testReportsEmptyWord(self, symFile):
        """A missing word before the separator is reported."""
        entries, issues = parseSymFile(symFile("$5\n"))
        assert entries == []
        assert "empty word" in issues[0].message


# ******************************************************************************
class TestValidateCommand(SymFileFixture):
    def testCleanFileExitsZero(self, symFile, capsys):
        """A canonical file reports no issues and exits 0."""
        assert main(["validate", str(symFile("\u0628$3\n\u062a$7\n"))]) == 0
        assert "no issues" in capsys.readouterr().out

    def testReportsEmptyNormalization(self, symFile, capsys):
        """A word that normalizes to empty is reported (the Vocabulary fence)."""
        assert main(["validate", str(symFile("\u0640$5\n"))]) == 1
        out = capsys.readouterr().out
        assert "line 1" in out and "empty" in out

    def testReportsUnmappedCharacters(self, symFile, capsys):
        """Characters outside the Arabic->Roman map are reported."""
        assert main(["validate", str(symFile("abc$5\n"))]) == 1
        assert "unmapped" in capsys.readouterr().out

    def testReportsDuplicateCanonicalForms(self, symFile, capsys):
        """A presentation form and its base form collide after normalization."""
        assert main(["validate", str(symFile("\u0628$2\n\ufe8f$3\n"))]) == 1
        out = capsys.readouterr().out
        assert "duplicate" in out and "line 1" in out

    def testReportsMalformedLines(self, symFile, capsys):
        """Malformed lines are part of the validation report."""
        assert main(["validate", str(symFile("\u0628\n"))]) == 1
        assert "separator" in capsys.readouterr().out

    def testReportsBlankLines(self, symFile, capsys):
        """Blank lines make a file invalid instead of being skipped."""
        assert main(["validate", str(symFile("\u0628$3\n\n\u062a$7\n"))]) == 1
        out = capsys.readouterr().out
        assert "line 2" in out and "blank" in out

    def testMissingFileExitsOne(self, tmp_path, capsys):
        """A missing input file produces a clean error, not a traceback."""
        assert main(["validate", str(tmp_path / "nope.sym")]) == 1
        assert "nope.sym" in capsys.readouterr().err


# ******************************************************************************
class TestNormalizeCommand(SymFileFixture):
    def testWritesCanonicalFile(self, symFile, tmp_path):
        """Non-canonical spellings are written in canonical form."""
        out = tmp_path / "out.sym"
        assert main(["normalize", str(symFile("\ufe8f$2\n")), "-o", str(out)]) == 0
        assert out.read_text(encoding="utf-8") == "\u0628$2\n"

    def testSumsDuplicateFrequencies(self, symFile, tmp_path):
        """Lines that normalize to the same word merge into one summed entry."""
        out = tmp_path / "out.sym"
        main(["normalize", str(symFile("\ufe8f$2\n\u0628$3\n")), "-o", str(out)])
        assert out.read_text(encoding="utf-8") == "\u0628$5\n"

    def testInPlaceRewritesInput(self, symFile):
        """--in-place rewrites the input file itself."""
        source = symFile("\ufe8f$2\n")
        assert main(["normalize", str(source), "--in-place"]) == 0
        assert source.read_text(encoding="utf-8") == "\u0628$2\n"

    def testPreviewDoesNotWrite(self, symFile, capsys):
        """--preview reports the changes and leaves the file untouched."""
        source = symFile("\ufe8f$2\n\ufe8f$3\n")
        before = source.read_text(encoding="utf-8")
        assert main(["normalize", str(source), "--preview"]) == 0
        assert source.read_text(encoding="utf-8") == before
        out = capsys.readouterr().out
        assert "changed" in out and "merged" in out

    def testDropsEmptyNormalization(self, symFile, tmp_path):
        """Lines that normalize to empty cannot be words and are dropped."""
        out = tmp_path / "out.sym"
        main(["normalize", str(symFile("\u0640$5\n\u0628$2\n")), "-o", str(out)])
        assert out.read_text(encoding="utf-8") == "\u0628$2\n"

    def testRequiresTargetOrPreview(self, symFile):
        """Without a target and without --preview the command is a usage error."""
        with pytest.raises(SystemExit) as excinfo:
            main(["normalize", str(symFile("\u0628$2\n"))])
        assert excinfo.value.code == 2

    def testRejectsPreviewWithTarget(self, symFile, tmp_path):
        """--preview cannot be combined with a write target."""
        with pytest.raises(SystemExit) as excinfo:
            main(["normalize", str(symFile("\u0628$2\n")), "-o", str(tmp_path / "o.sym"), "--preview"])
        assert excinfo.value.code == 2


# ******************************************************************************
class TestWordsCommand(SymFileFixture):
    def testPrintsSortedWords(self, symFile, capsys):
        """Words are printed in code point order without frequencies."""
        source = symFile("\u06a9\u062a\u0627\u0628$5\n\u0627\u0628$2\n")
        assert main(["words", str(source)]) == 0
        assert capsys.readouterr().out.splitlines() == ["\u0627\u0628", "\u06a9\u062a\u0627\u0628"]

    def testDeduplicatesCanonicalForms(self, symFile, capsys):
        """Surface variants of one word produce a single exported word."""
        main(["words", str(symFile("\u0628$2\n\ufe8f$3\n"))])
        assert capsys.readouterr().out.splitlines() == ["\u0628"]

    def testWritesWordsFile(self, symFile, tmp_path):
        """-o writes the word list to a file instead of stdout."""
        out = tmp_path / "words.txt"
        assert main(["words", str(symFile("\u0628$2\n")), "-o", str(out)]) == 0
        assert out.read_text(encoding="utf-8") == "\u0628\n"


# ******************************************************************************
class TestMergeCommand(SymFileFixture):
    def testSumsSharedWords(self, symFile, tmp_path):
        """Words present in both files keep one entry with summed frequencies."""
        out = tmp_path / "merged.sym"
        first = symFile("\u0628$2\n\u062a$1\n", "a.sym")
        second = symFile("\u0628$3\n\u062b$4\n", "b.sym")
        assert main(["merge", str(first), str(second), "-o", str(out)]) == 0
        assert out.read_text(encoding="utf-8") == "\u0628$5\n\u062a$1\n\u062b$4\n"

    def testMatchesByCanonicalForm(self, symFile, tmp_path):
        """A surface variant and its base form are the same word for merging."""
        out = tmp_path / "merged.sym"
        first = symFile("\u0628$2\n", "a.sym")
        second = symFile("\ufe8f$3\n", "b.sym")
        main(["merge", str(first), str(second), "-o", str(out)])
        assert out.read_text(encoding="utf-8") == "\u0628$5\n"


# ******************************************************************************
class TestSubtractCommand(SymFileFixture):
    def testRemovesWordsPresentInSecond(self, symFile, tmp_path):
        """SECOND removes its words (by canonical form) from FIRST."""
        out = tmp_path / "diff.sym"
        first = symFile("\u0628$2\n\u062a$1\n", "a.sym")
        second = symFile("\ufe8f$3\n", "b.sym")
        assert main(["subtract", str(first), str(second), "-o", str(out)]) == 0
        assert out.read_text(encoding="utf-8") == "\u062a$1\n"

    def testKeepsFirstFileFrequencies(self, symFile, tmp_path):
        """Surviving words keep the frequencies from FIRST."""
        out = tmp_path / "diff.sym"
        first = symFile("\u0628$7\n", "a.sym")
        second = symFile("\u062a$3\n", "b.sym")
        main(["subtract", str(first), str(second), "-o", str(out)])
        assert out.read_text(encoding="utf-8") == "\u0628$7\n"


# ******************************************************************************
class TestListCommand:
    def testListsMethodsAndStages(self, capsys):
        """The list command renders every registered method with its stages."""
        assert main(["list"]) == 0
        out = capsys.readouterr().out
        assert "urdu-spell" in out
        assert "tatweel" in out


# ******************************************************************************
class TestMethodSelection(SymFileFixture):
    def testUnknownMethodIsUsageError(self, symFile):
        """An unknown method fails through argparse choices (exit code 2)."""
        with pytest.raises(SystemExit) as excinfo:
            main(["validate", str(symFile("\u0628$2\n")), "--normalize", "klingon"])
        assert excinfo.value.code == 2

    def testExplicitUrduSpellMethod(self, symFile):
        """An explicitly selected method behaves like the default."""
        assert main(["validate", str(symFile("\u0628$2\n")), "--normalize", "urdu-spell"]) == 0


# ******************************************************************************
class TestMain:
    def testModuleEntryPoint(self):
        """The package runs as ``python -m romanalfaz``."""
        result = subprocess.run(
            [sys.executable, "-m", "romanalfaz", "list"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0
        assert "urdu-spell" in result.stdout

    def testUrduOutputSurvivesNonUtf8ConsoleEncoding(self, tmp_path):
        """Urdu output is written as UTF-8 even when the console is not."""
        source = tmp_path / "words.sym"
        source.write_text("\u0628$2\n", encoding="utf-8")
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = subprocess.run(
            [sys.executable, "-m", "romanalfaz", "words", str(source)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout == "\u0628\n"
