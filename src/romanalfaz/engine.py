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
from typing import NamedTuple, Callable

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
        self.onChangeCallbacks: list[Callable[[], None]] = []

    # --------------------------------------------------------------------------
    def notifyChanges(self):
        """Triggers attached callbacks when internal state changes."""
        for callback in self.onChangeCallbacks:
            callback()

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
        self.notifyChanges()

    # --------------------------------------------------------------------------
    def remove(self, word: str):
        """Remove a word from both the counter and completed set if present."""
        assert isinstance(word, str)
        assert len(word) > 0

        changed = False
        # Remove from frequency tracker only if it exists
        if word in self.counter:
            del self.counter[word]
            changed = True

        # Remove from completion status only if marked as complete
        if word in self.completed:
            self.completed.remove(word)
            changed = True

        if changed:
            self.notifyChanges()

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

            self.notifyChanges()

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

        self.notifyChanges()

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
    Urdu transliteration and arabic-script Urdu words.It aggregates data from multiple source
    'Vocabulary' instances at runtime, resolving cross-dictionary collisions
    by summing word frequencies.

    Using the Observer Pattern, it automatically listens for mutations (additions,
    removals, modifications) within any registered Vocabulary and dynamically
    recompiles its internal lookup indices to guarantee a live, accurate system state.

    Attributes:
        symSpell (SymSpell): The underlying SymSpell engine instance used to perform
            efficient, high-performance edit-distance lookups and spelling corrections.
        reverseMapping (defaultdict[str, set[tuple[str, int]]]): A lookup table mapping
            encoded Roman words to a set of their original native script Arabic variants
            along with their aggregate frequencies. Used to resolve homonyms during queries.
        vocabularies (list[Vocabulary]): A collection holding references to all
            currently attached and monitored Vocabulary instances active in the system.
    """
    def __init__(self, vocabularies: list[Vocabulary] | None = None):
        """
        Initializes the RomanAlfaz coordinator with optional starter vocabularies.

        Sets up the underlying SymSpell fuzzy logic core, initializes the
        structural reverse-mapping lookup, and hooks into any provided source
        vocabularies to kick off the baseline index compilation.

        Args:
            vocabularies (list[Vocabulary] | None): An optional collection of
                Vocabulary instances to populate the search matrix immediately.
        """
        # Initialize the underlying SymSpell engine used for edit-distance algorithms.
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

        # Holds references to all monitored Vocabulary instances active in the system.
        self.vocabularies: list[Vocabulary] = []

        # Process and link incoming starter vocabularies if they are provided.
        if vocabularies:
            for vocab in vocabularies:
                # addVocabulary handles tracking, callback attachments,
                # and triggers the initial state compilation.
                self.addVocabulary(vocab)
        else:
            # Fallback behavior when no specific vocabularies are passed:
            # attempt to resolve and initialize using the default wordlist source.
            try:
                vocab = Vocabulary.load(getDefaultWordsFilename())
            except Exception as e:
                raise DictionaryNotFoundError(e)
            else:
                self.addVocabulary(vocab)
            self.recompileLookup()

    # **************************************************************************
    def addVocabulary(self, vocab: Vocabulary) -> None:
        """
        Registers a new Vocabulary instance to be tracked by RomanAlfaz.

        This method attaches the RomanAlfaz compilation manager as a listener
        to the target vocabulary. Any future mutations to that vocabulary
        will automatically trigger a lookup engine rebuild.

        Args:
            vocab (Vocabulary): The vocabulary instance to start monitoring.
        """
        # Guard clause: Prevent duplicate registrations which would cause
        # identical data to be counted twice during aggregation.
        if vocab not in self.vocabularies:
            self.vocabularies.append(vocab)
            # Register the internal recompile method as a change listener callback.
            # When the vocabulary changes, it calls this function automatically.
            vocab.onChangeCallbacks.append(self.recompileLookup)
            # Instantly rebuild the engines to reflect the newly injected dataset.
            self.recompileLookup()

    # **************************************************************************
    def removeVocabulary(self, vocab: Vocabulary) -> None:
        """
        Unregisters a monitored Vocabulary instance from RomanAlfaz.

        This method detaches the callback listener, stops tracking the object,
        and strips its entries out of the active runtime search engine.

        Args:
            vocab (Vocabulary): The vocabulary instance to stop monitoring.
        """
        # Guard clause: Ensure the vocabulary is currently tracked before
        # attempting to remove it to avoid unexpected value errors.
        if vocab in self.vocabularies:
            self.vocabularies.remove(vocab)
            # Detach the callback function to prevent ghost notifications
            # and allow proper garbage collection of the vocabulary object.
            if self.recompileLookup in vocab.onChangeCallbacks:
                vocab.onChangeCallbacks.remove(self.recompileLookup)
            # Recompile immediately to completely purge the unlinked
            # vocabulary's words from the system.
            self.recompileLookup()

    # **************************************************************************
    def recompileLookup(self) -> None:
        """
        Recompiles the unified lookup indices from all attached Vocabularies.

        This method acts as a central data processor. It resets the internal
        engines, flattens all attached source vocabularies, resolves multi-source
        word collisions by summing their frequencies, and fully rebuilds both
        the SymSpell fuzzy-search index and the Arabic reverse mapping.

        Complexity:
            O(N) where N is the total number of unique words across all tracked
            Vocabulary instances.
        """
        # STAGE 1: Reset Internal Search Engines -------------------------------
        # Re-initialize SymSpell to ensure a clean state before adding entries
        # Wiping previous data structures ensures dead records (e.g., deleted words)
        # do not linger in memory after a vocabulary mutation.
        self.symSpell = SymSpell()
        self.reverseMapping.clear()

        # STAGE 2: Flatten & Sum Arabic script Word Frequencies ----------------
        # Multiple dictionaries might contain the exact same Arabic word.
        # Using Counter.update() merges them, automatically summing up their counts.
        aggregateCounter: Counter[str] = Counter()
        for vocab in self.vocabularies:
            aggregateCounter.update(vocab.counter)

        # STAGE 3: Romanization & Homonym Mapping ------------------------------
        # Different Arabic words can resolve to the exact same Romanized string.
        # We track total Roman string frequency (critical for SymSpell ranking) and
        # preserve individual Arabic origin variants inside a nested dictionary structure.
        romanFreqCounter: Counter[str] = Counter()
        rm2arMapping: defaultdict[str, dict[str, int]] = defaultdict(dict)

        for arWord, freq in aggregateCounter.items():
            # Convert native script to Romanized representation
            encRomanWord, undef = tafseerUrduAr2Rm(arWord)
            assert undef == 0

            # Accumulate weight for the Roman word entry (used by SymSpell)
            romanFreqCounter[encRomanWord] += freq

            # Record or increment the specific Arabic variant bound to this Roman word
            if arWord not in rm2arMapping[encRomanWord]:
                rm2arMapping[encRomanWord][arWord] = 0
            rm2arMapping[encRomanWord][arWord] += freq

        # STAGE 4: Populate Operational Lookup Engines -------------------------
        # Commit the computed structural matrices back into operational states.
        for encRomanWord, combinedFreq in romanFreqCounter.items():
            # Populate SymSpell dictionary with the total aggregated string frequency
            self.symSpell.create_dictionary_entry(encRomanWord, combinedFreq)

            # Hydrate the reverse mapping set for native script ranking inside suggest()
            for arWord, freq in rm2arMapping[encRomanWord].items():
                self.reverseMapping[encRomanWord].add((arWord, freq))

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

        # Process the three tiers
        results = []
        for tier in (0, 1, 2):
            tierSuggestions = getSuggestionsTier(suggestionsList,
                                                 tier=tier,
                                                 atmost=maxPredictions)
            if tierSuggestions:
                tierSuggestions = [
                    Suggestion(wd, sg.term, fr)
                    for sg in tierSuggestions
                    for (wd, fr) in self.reverseMapping.get(sg.term, set())
                ]
                tierSuggestions = sorted(tierSuggestions,
                                         key=lambda item: item.frequency,
                                         reverse=True)
            results.append(tierSuggestions)

        return results[0], results[1], results[2]

    # **************************************************************************
    def getExactMatches(self, romanWord: str, maxPredictions: int | None = 5) -> list[Suggestion]:
        """
       Generates of suggested arabic-script Urdu words which match exactly with the
       roman-script input.

       Args:
           romanWord (str): The roman-script word to transliterate.
           maxPredictions (int): Maximum number of unique suggestions
               to provide (default is 5). Use ``None`` to get
               all suggestions.

       Returns:
           list[Suggestion]: A list of :py:class:`Suggestion` exact matching items
           in order of word frequency.

       Raises:
           AssertionError: If `romanWord` is not a string.
       """
        suggestions, _, _ = self.suggest(romanWord, distance=1, maxPredictions=maxPredictions)
        return suggestions


    # **************************************************************************
    def getBestMatch(self, romanWord: str) -> Suggestion | None:
        """
        Get single best arabic-script Urdu word suggestion for the roman-script input.

        Args:
           romanWord (str): The roman-script word to transliterate.

        Returns:
           Suggestion | None: Exact matching :py:class:`Suggestion` item
           with the highest frequency. ``None`` is returned if no exact match is found.

        Raises:
           AssertionError: If `romanWord` is not a string.
        """
        suggestions = self.getExactMatches(romanWord, maxPredictions=None)
        return suggestions[0] if suggestions else None


# ******************************************************************************
