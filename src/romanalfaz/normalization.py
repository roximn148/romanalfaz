# ******************************************************************************
#    Copyright (c) 2026 RoXimn <roximn148@gmail.com>
#    This source code is licensed under the MIT license found in the
#    LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""
The :py:mod:`romanalfaz.normalization` module is the registry of the
normalization methods available in the package.

Each normalization method defines one canonical form of Urdu arabic-script
text for a specific processing scope, and lives in its own module (see
:py:mod:`romanalfaz.urduspell`). The registry maps a method's public label,
such as ``urdu-spell``, to its implementation, scope description, and
pipeline stages, so tools can select a method by name and present what it
does.

Adding a method means writing its module and adding one entry to
:data:`romanalfaz.normalization.NORMALIZATION_METHODS`.
"""
from collections.abc import Callable
from typing import NamedTuple

from . import urduspell


# ******************************************************************************
class NormalizationMethod(NamedTuple):
    """A named normalization method and the processing scope it is built for."""

    name: str
    """(str): The public label of the method, e.g. ``urdu-spell``."""
    description: str
    """(str): What the method guarantees and for which scope."""
    stages: tuple[str, ...]
    """(tuple[str, ...]): The pipeline stages the method applies, in order, as
    short human-readable phrases."""
    function: Callable[[str], str]
    """(Callable[[str], str]): The normalization function, mapping an input
    string to its canonical form."""


NORMALIZATION_METHODS: dict[str, NormalizationMethod] = {
    "urdu-spell": NormalizationMethod(
        name="urdu-spell",
        description=(
            "Canonical spelling for word lookup in Urdu dictionaries and "
            "word lists: folds variant and positional forms, removes marks "
            "and non-letter residue, and leaves a single lookup key per word."
        ),
        stages=(
            "decompose lam-alef ligatures into base characters",
            "fold positional and presentation forms to base characters",
            "fold cross-dialect base characters (e.g. U+0624 to U+0648) to Urdu forms",
            "strip tatweel (U+0640)",
            "remove combining marks, preserving U+0653 (madda) and U+0654 (hamza above)",
            "remove digits, punctuation, symbols, and control characters",
            "collapse whitespace runs to single spaces",
        ),
        function=urduspell.normalize,
    ),
}
"""
The normalization methods available in the package, keyed by their public
label. The insertion order is the order presented by the CLI.
"""
