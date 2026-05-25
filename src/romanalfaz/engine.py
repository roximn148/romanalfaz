# -*- coding: utf-8 -*-
# ******************************************************************************
#    Copyright (c) 2026 RoXimn <roximn148@gmail.com>
#    This source code is licensed under the MIT license found in the
#    LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""
This module contains the transliteration implementation logic for the romanalfaz
package.
"""
# ******************************************************************************
from collections import Counter, defaultdict
from itertools import chain
from pathlib import Path
from typing import NamedTuple

from symspellpy import SymSpell, Verbosity
from symspellpy.suggest_item import SuggestItem

from .algorithm import tafseerUrduRm2Rm, tafseerUrduAr2Rm
from .exceptions import DictionaryNotFoundError

# ******************************************************************************
def getDefaultWordsFilename() -> str:
    """Resolves the absolute path to the bundled 'UrduWords5k.sym' file."""

    # Construct the relative path to the words file, assuming it resides
    # in the same directory as this module.
    wordsFilePath = Path(__file__).parent / "UrduWords5k.sym"

    # Resolve any symbolic links or relative components and convert back to a string.
    return str(wordsFilePath.resolve())


# ******************************************************************************
class Vocabulary:
    """Manages a collection of words with their frequencies and completion status."""

    # --------------------------------------------------------------------------
    def __init__(self, data: dict[str, int] | None = None):
        """Initialize vocabulary with optional preloaded word counts.

        Args:
            data (dict[str, int], optional): Dictionary mapping words to their initial counts.
        """
        self.counter = Counter(data) if data else Counter()
        self.completed = set()

    # --------------------------------------------------------------------------
    def add(self, word: str, count: int = 1):
        """Accumulate the count for a specific word.

        If the word exists, its current count increases by `count`.
        Otherwise, it is added with the specified count.

        Args:
            word (str): The word to add or update.
            count (int): Number of times to increment the word's frequency. Defaults to 1.
        """
        assert isinstance(word, str)
        assert len(word) > 0
        assert isinstance(count, int)
        assert count >= 1

        self.counter[word] += count

    # --------------------------------------------------------------------------
    def remove(self, word: str):
        """Remove a word from both the counter and completed set if present."""
        assert isinstance(word, str)
        assert len(word) > 0

        # Remove from frequency tracker only if it exists
        if word in self.counter:
            del self.counter[word]

        # Remove from completion status only if marked as complete
        if word in self.completed:
            self.completed.remove(word)

    # --------------------------------------------------------------------------
    def replace(self, oldWord: str, newWord: str):
        """Swap an existing word with a new one while preserving its frequency and status.

        This is useful for correcting typos or updating terminology without losing data.

        Args:
            oldWord (str): The current word to be replaced.
            newWord (str): The replacement word.
        """
        assert isinstance(oldWord, str)
        assert isinstance(newWord, str)

        if oldWord in self.counter:
            # Retrieve the frequency of the old word before removal
            oldFreq = self.counter.pop(oldWord)

            # Add the same frequency to the new word
            self.add(newWord, oldFreq)

            # Update completion status accordingly
            if oldWord in self.completed:
                self.completed.remove(oldWord)
                self.completed.add(newWord)

    # --------------------------------------------------------------------------
    def setCompleted(self, word: str, isCompleted: bool):
        """Toggle a word's completion status.

        Args:
            word (str): The word to update.
            isCompleted (bool): True to mark as completed, False otherwise.
        """
        assert isinstance(word, str)
        assert len(word) > 0

        if isCompleted:
            self.completed.add(word)
        else:
            # discard() prevents KeyError if the word wasn't in the set
            self.completed.discard(word)

    # --------------------------------------------------------------------------
    def save(self, filename: str, sep: str = '$'):
        """Persist completed words and their frequencies to a file.

        Writes only words that have been marked as completed, sorted by frequency (highest first).

        Args:
            filename (str): Path where the SymSpell-compatible file will be saved.
            sep (str): Separator character between word and count (default is '$').
        """
        assert isinstance(filename, str)
        assert len(filename) > 0
        assert isinstance(sep, str)
        assert len(sep) == 1
        assert not sep.isdigit(), "Seperator cannot be a digit"

        with open(filename, "w", encoding="utf-8") as sym:
            # Iterate through most common words to ensure high-frequency items come first
            for i, (w, f) in enumerate(self.counter.most_common()):
                if w in self.completed:
                    sym.write(f"{w}{sep}{f}\n")

    # --------------------------------------------------------------------------
    @classmethod
    def load(cls, filename: str, sep: str='$') -> 'Vocabulary':
        """Reconstruct a Vocabulary instance from a saved SymSpell file.

        Args:
            filename (str): Path to the source file.
            sep (str): Separator character used in the file (default is '$').

        Returns:
            Vocabulary: A new Vocabulary object populated with loaded data.
        """
        assert isinstance(filename, str)
        assert len(filename) > 0
        assert isinstance(sep, str)
        assert len(sep) == 1
        assert not sep.isdigit(), "Seperator cannot be a digit"

        newVocab = cls()
        with open(filename, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    # Split from the right to handle cases where word might contain separators
                    parts = line.rsplit(sep, 1)
                    if len(parts) == 2:
                        word, freq = parts
                        newVocab.add(word, int(freq))
                        newVocab.setCompleted(word, True)
        return newVocab


# ******************************************************************************
class Suggestion(NamedTuple):
    """Urdu transliteration suggestion pairing Arabic script to encoded Roman."""
    arabic: str
    """(str): The original word in Arabic script."""
    encodedRoman: str
    """(str): The intermediate encoded Roman representation."""
    frequency: int
    """(int): The usage count of this specific word."""

    def __str__(self) -> str:
        return f"{self.arabic}:{self.encodedRoman} [{self.frequency:}]"

    def __repr__(self) -> str:
        return (f"Suggestion(arabic={self.arabic!r}, "
                f"encodedRoman={self.encodedRoman!r}, "
                f"frequency={self.frequency!r})")


# ******************************************************************************
class RomanAlfaz:
    """
    `RomanAlfaz` facilitates fuzzy matching between input roman-script
    Urdu transliteration and arabic-script Urdu words. It utilizes a
    SymSpell engine loaded with a custom vocabulary to suggest corrections
    based on edit distance.

    Attributes:
        symSpell (SymSpell): The underlying spell-checking instance.
        reverseMapping (dict[str, set[tuple]]): A mapping between arabic-script words
            and their roman-script counterparts and frequencies.
        dictFilename (str | None): Path to the dictionary file for initialization.
    """

    def __init__(self, dictFilename: str | None = None):
        """
        Initializes the RomanAlfaz instance by setting up the SymSpell engine
        and loading the appropriate vocabulary dictionary.

        Args:
            dictFilename (str | None): Optional path to a custom .sym file.
                If not provided, defaults to the standard Urdu word list.
        """
        self.symSpell = SymSpell()

        # Create a many-to-many mapping structure (specifically, a dictionary of sets)
        # designed to handle cases where multiple arabic-script words might share
        # the same roman-script spelling.  This code stores a set (an unordered
        # collection of unique items) for every key automatically. If
        # the key doesn't exist, it creates an empty set set() automatically
        # when you try to access it or add to it. This allows
        # multiple (ArabicWord, Frequency) tuples to be stored under
        # a single Roman word key without overwriting each other.
        self.reverseMapping: defaultdict = defaultdict(set)

        # Resolve filename: use custom one if given, otherwise default
        self.dictFilename = dictFilename or getDefaultWordsFilename()

        # Load the vocabulary data into memory and initialize mappings
        self.loadDictionary()

    # **************************************************************************
    def loadDictionary(self) -> None:
        """
        Loads frequency data from a SymSpell dictionary file.

        This method reads the .sym file, converts Roman-script words to their
        Arabic-script equivalents using `tafseerUrduAr2Rm`, and populates both
        the SymSpell instance for fast lookup and a reverse mapping for result
        enrichment.

        Raises:
            DictionaryNotFoundError: If the specified dictionary file is missing or invalid.
        """
        try:
            # Load vocabulary object from the .sym file
            vocab = Vocabulary.load(self.dictFilename)
        except Exception as e:
            raise DictionaryNotFoundError(e)

        # Re-initialize SymSpell to ensure a clean state before adding entries
        self.symSpell = SymSpell()
        self.reverseMapping.clear()

        # Iterate through the most frequent words in the loaded vocabulary
        for normArabicWord, freq in vocab.counter.most_common():
            # Convert Roman input word to Arabic-script representation
            encRomanWord, undef = tafseerUrduAr2Rm(normArabicWord)

            # Ensure conversion was successful (no undefined mappings)
            assert undef == 0

            # Register the encoded roman-script word in SymSpell with its frequency count
            self.symSpell.create_dictionary_entry(encRomanWord, freq)

            # ------------------------------------------------------------------
            ##########################  DO NOT REMOVE  #########################
            # ------------------------------------------------------------------
            # This is an explanation of the use of the defaultdict
            # (50, 'hello', 'hallo'),
            # (20, 'hello', 'hallo'),
            # (10, 'world', 'alard')
            #
            # mapping = defaultdict(set)
            # for f, w, r in wordsList:
            #     mapping[r].add((w, f))
            #
            # The resulting 'mapping' looks like this:
            # {
            #     'hello': {('hallo', 50), ('hallo', 20)},
            #     'world': {('alard', 10)}
            # }
            # ------------------------------------------------------------------

            # Store the mapping: encRomanWord -> Set of (ArabicWord, Frequency) tuples
            self.reverseMapping[encRomanWord].add((normArabicWord, freq))

    # **************************************************************************
    def dictLookup(self, encRomanWord: str, *, distance: int) -> tuple[list[SuggestItem],
                                                                       list[SuggestItem],
                                                                       list[SuggestItem]]:
        """
        Performs a fuzzy lookup in the dictionary based on edit distance.

        This method queries SymSpell for words similar to the provided roman-script
        input and separates results by their exact match (distance 0) or edit distance
        (1 or 2).

        Args:
            encRomanWord (str): The Roman-script word to search for.
            distance (int): Maximum allowed edit distance (must be 0, 1, or 2).

        Returns:
            tuple[list, list, list]: A tuple containing three lists corresponding
            to exact matches (index 0), one-edit-distance matches (index 1), and two-
            edit-distance matches (index 2). Empty lists are returned if no matches
            exist for a specific distance tier.

        Raises:
            AssertionError: If the provided `distance` is outside the valid range [0, 2].
        """
        assert 0 <= distance <= 2

        # Query SymSpell with specified edit distance constraints
        suggestions = self.symSpell.lookup(
            encRomanWord, Verbosity.CLOSEST,
            max_edit_distance=distance,
            include_unknown=False)

        if distance == 0:
            # Filter strictly for exact matches (edit distance 0)
            s0 = list(filter(lambda item: item.distance == 0, suggestions))
            return s0, [], []

        elif distance == 1:
            # Separate results into exact matches and one-edit-distance matches
            s0 = list(filter(lambda item: item.distance == 0, suggestions))
            s1 = list(filter(lambda item: item.distance == 1, suggestions))
            return s0, s1, []

        else:
            # Handle distance of 2 by separating all three tiers
            s0 = list(filter(lambda item: item.distance == 0, suggestions))
            s1 = list(filter(lambda item: item.distance == 1, suggestions))
            s2 = list(filter(lambda item: item.distance == 2, suggestions))
            return s0, s1, s2

    # **************************************************************************
    def suggest(self, romanWord: str, distance: int = 1, maxPredictions: int | None = 5) -> tuple[list[Suggestion], list[Suggestion], list[Suggestion]]:
        """
        Generates a ranked list of suggested arabic-script Urdu words based on
        roman-script input. This method performs the fuzzy lookup and returns
        the encoded roman spellings, arabic-script representation and
        corresponding word usage frequencies for further processing.


        Args:
            romanWord (str): The roman-script word to transliterate.
            distance (int): Maximum edit distance to consider (default is 1).
            maxPredictions (int): Maximum number of unique suggestions per tier
                before truncating the list (default is 5). Use ``None`` to get
                all suggestions.

        Returns:
            tuple[list[Suggestion], list[Suggestion], list[Suggestion]]: A tuple
            containing three lists (in index order) exact matches, one-edit-distance
            matches, and two-edit-distance matches. Each list in turn is a list
            of :py:class:`Suggestion` items sorted in decreasing order
            of frequency.

        Raises:
            AssertionError: If `romanWord` is not a string.
        """
        assert isinstance(romanWord, str)

        # Return empty lists immediately if input is invalid or missing
        if not romanWord:
            return [], [], []

        # Convert the Roman input into all possible Arabic-script permutations
        encRomanWords = tafseerUrduRm2Rm(romanWord)

        # If no valid conversions exist, return empty results
        if len(encRomanWords) == 0:
            return [], [], []

        # ------------------------------------------------------------------
        def getSuggestionsTier(suggestions:list[tuple[list[SuggestItem],
                                                      list[SuggestItem],
                                                      list[SuggestItem]]],
                               tier: int, atmost: int | None = None):
            """
            Helper function to extract a specific edit distance tier of suggestions,
            then flatten them into a single list and remove any duplicates.

            Args:
                suggestions (list[tuple]): List of tuples from `dictLookup` results.
                tier (int): The edit distance tier (0, 1, or 2) to process.
                atmost (int, optional): Maximum number of unique suggestions to return.
                    If ``None``, returns all available unique matches for the tier.

            Returns:
                list: A sorted list of unique matches ranked by frequency count.
            """
            # Flatten the nested suggestion lists for the current tier into a single stream
            matches = chain.from_iterable([s[tier] for s in suggestions])

            # Deduplicate based on the term (Arabic word) while preserving one instance per term
            matches = list({match.term: match for match in matches}.values())

            # Return only the top N unique suggestions
            return matches[:atmost]
        # ------------------------------------------------------------------

        # Perform lookup for each Arabic permutation of the input word
        suggestionsList = [self.dictLookup(word, distance=distance) for word in encRomanWords]

        # Process Exact Matches (Distance 0)
        s0 = getSuggestionsTier(suggestionsList, tier=0, atmost=maxPredictions)
        if s0:
            # Enrich results with original Roman spellings and frequencies from reverse mapping
            s0 = [Suggestion(wd, sg.term, fr) for sg in s0
                  for (wd, fr) in self.reverseMapping.get(sg.term, set())]
            # Final sort by frequency to ensure highest usage words appear first
            s0 = sorted(s0, key=lambda item: item.frequency, reverse=True)

        # Process One-Edit Matches (Distance 1)
        s1 = getSuggestionsTier(suggestionsList, tier=1, atmost=maxPredictions)
        if s1:
            s1 = [Suggestion(wd, sg.term, fr) for sg in s1
                  for (wd, fr) in self.reverseMapping.get(sg.term, set())]
            s1 = sorted(s1, key=lambda item: item.frequency, reverse=True)

        # Process Two-Edit Matches (Distance 2)
        s2 = getSuggestionsTier(suggestionsList, tier=2, atmost=maxPredictions)
        if s2:
            s2 = [Suggestion(wd, sg.term, fr) for sg in s2
                  for (wd, fr) in self.reverseMapping.get(sg.term, set())]
            s2 = sorted(s2, key=lambda item: item.frequency, reverse=True)

        return s0, s1, s2

# ******************************************************************************
