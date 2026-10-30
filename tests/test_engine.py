# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
from unittest.mock import mock_open, patch

import pytest

from romanalfaz.engine import RomanAlfaz, Suggestion, Vocabulary


# ******************************************************************************
class TestVocabulary:
    @pytest.fixture
    def populatedVocabulary(self):
        """Custom fixture for generating a reusable Vocabulary instance with mixed characters (لاطینی and اردو)."""
        data = {"کتاب": 15, "library": 25, "مکس!data": 5}
        v = Vocabulary(data)
        v.setCompleted("کتاب", True)
        v.setCompleted("library", True)
        return v

    def testFixtureIntegrity(self, populatedVocabulary):
        """Validates the structure and metrics coverage of the custom populated vocabulary fixture."""
        assert populatedVocabulary.counter["library"] == 25
        assert "کتاب" in populatedVocabulary.completed
        assert "مکس!data" not in populatedVocabulary.completed

    @pytest.fixture
    def mockFileData(self):
        """Custom fixture providing raw file storage data mimicking a saved SymSpell configuration file."""
        return "ٹیسٹ$50\ntest_word$100\n"

    def testInitEmpty(self):
        """Initializes empty vocabulary using empty input."""
        v = Vocabulary()
        assert len(v.counter) == 0
        assert len(v.completed) == 0

    def testInitWithData(self):
        """Initializes vocabulary directly with a dictionary holding mixed characters (کتاب, data!)."""
        initData = {"کتاب": 5, "computer": 12, "punctuation!": 1}
        v = Vocabulary(initData)
        assert v.counter["کتاب"] == 5
        assert v.counter["computer"] == 12
        assert v.counter["punctuation!"] == 1

    def testAddValidWords(self):
        """Adds valid words to check standard frequency accumulation with mixed characters like 'اردو'."""
        v = Vocabulary()
        v.add("python")
        v.add("اردو", 3)
        v.add("python", 2)
        assert v.counter["python"] == 3
        assert v.counter["اردو"] == 3

    def testAddInvalidInputs(self):
        """Checks assertion errors for invalid inputs during initialization or adding (خالی str, negative integers)."""
        v = Vocabulary()
        with pytest.raises(AssertionError):
            v.add("")  # Empty str handle نہیں ہوتی
        with pytest.raises(AssertionError):
            v.add("urdu", 0)  # Count zero is invalid
        with pytest.raises(AssertionError):
            v.add("latin", -5)  # Negative entry handle نہیں ہوتی

    def testAddRejectsNormalizeToEmpty(self):
        """Rejects words whose normalized form is empty (tatweel-only, diacritic-only strings)."""
        v = Vocabulary()
        with pytest.raises(AssertionError):
            v.add("\u0640")  # ARABIC TATWEEL only
        with pytest.raises(AssertionError):
            v.add("\u064e")  # ARABIC FATHA only
        assert len(v.counter) == 0

    def testInitRejectsNormalizeToEmpty(self):
        """The data dict is fenced like add: keys that normalize to empty are rejected."""
        with pytest.raises(AssertionError):
            Vocabulary({"\u0640": 1})  # ARABIC TATWEEL only

    def testRemoveWord(self):
        """Removes a word from both counter tracking and the completion status set."""
        v = Vocabulary({"لفظ": 2, "word": 4})
        v.setCompleted("لفظ", True)

        v.remove("لفظ")
        assert "لفظ" not in v.counter
        assert "لفظ" not in v.completed

        # Removing missing values safely does nothing
        v.remove("missing_ورڈ")

    def testReplaceWord(self):
        """Swaps an old entry with a new terminology preserving frequency and completion setup ('غلطی' to 'درست')."""
        v = Vocabulary({"غلطی": 10, "correct": 5})
        v.setCompleted("غلطی", True)

        v.replace("غلطی", "درست")
        assert "غلطی" not in v.counter
        assert "غلطی" not in v.completed
        assert v.counter["درست"] == 10
        assert "درست" in v.completed

    def testSetCompletedToggle(self):
        """Toggles completion status flag using set status mechanism."""
        v = Vocabulary({"ٹیسٹ": 1})
        v.setCompleted("ٹیسٹ", True)
        assert "ٹیسٹ" in v.completed

        v.setCompleted("ٹیسٹ", False)
        assert "ٹیسٹ" not in v.completed

    def testSaveAndLoad(self, tmp_path):
        """Saves and loads data utilizing custom separator characters ($) to handle file operations safely."""
        filepath = tmp_path / "SaveAndLoadVocab.txt"
        v = Vocabulary()
        v.add("سلام", 5)
        v.add("hello", 10)
        v.add("mix!یا", 3)

        # Only completed markers are saved
        v.setCompleted("سلام", True)
        v.setCompleted("hello", True)

        v.save(str(filepath), sep="$")

        # Load again for parsing evaluation
        loadedV = Vocabulary.load(str(filepath), sep="$")
        assert loadedV.counter["hello"] == 10
        assert loadedV.counter["سلام"] == 5
        assert "mix!یا" not in loadedV.counter
        assert "hello" in loadedV.completed

    def testSaveSortingOrder(self, tmp_path):
        """Verifies that items saved to the storage file are ordered accurately from high to low counts."""
        filepath = tmp_path / "SaveSortingOrder.txt"
        v = Vocabulary()
        v.add("کم", 2)
        v.add("زیادہ", 20)
        v.setCompleted("کم", True)
        v.setCompleted("زیادہ", True)

        v.save(str(filepath), sep="#")

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert "زیادہ#20" in lines[0]
        assert "کم#2" in lines[1]

    @patch("builtins.open", new_callable=mock_open)
    def testSaveFileIoError(self, mockFile, populatedVocabulary):
        """Mocks file open behavior to simulate OS write faults and exceptions during file export operations."""
        mockFile.side_effect = OSError("Disk Full Error")

        with pytest.raises(IOError) as excInfo:
            populatedVocabulary.save("dummy.txt")

        assert "Disk Full Error" in str(excInfo.value)
        mockFile.assert_called_once_with("dummy.txt", "w", encoding="utf-8")

    @patch("builtins.open")
    def testLoadMissingFileException(self, mockFile):
        """Mocks file reading to verify that FileNotFoundError behavior functions normally when loading records."""
        mockFile.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError):
            Vocabulary.load("unknown.txt")

    def testBoundarySeparatorsAndCoverage(self, populatedVocabulary, tmp_path):
        """Increases coverage metrics by evaluating multi-character words containing edge case punctuation markers."""
        filepath = tmp_path / "edgeCase.txt"

        # Edge cases: words containing structural delimiter components inside the string sequence
        populatedVocabulary.add("نام$غلط", 4)
        populatedVocabulary.setCompleted("نام$غلط", True)

        # Use a different visual anchor symbol to completely insulate the right split execution path
        populatedVocabulary.save(str(filepath), sep="|")
        loadedV = Vocabulary.load(str(filepath), sep="|")
        assert loadedV.counter["نام$غلط"] == 4
        assert "نام$غلط" in loadedV.completed

        # Use a same symbol to check the right split execution path
        populatedVocabulary.save(str(filepath), sep="$")
        loadedV = Vocabulary.load(str(filepath), sep="$")
        assert loadedV.counter["نام$غلط"] == 4
        assert "نام$غلط" in loadedV.completed

    def testIsModifiedInitialStates(self):
        """A freshly built vocabulary reports unmodified, with or without initial data."""
        assert Vocabulary().isModified() is False
        assert Vocabulary({"کتاب": 5}).isModified() is False

    def testAddMarksModified(self):
        """Adding a word marks the vocabulary as modified."""
        v = Vocabulary()
        v.add("python")
        assert v.isModified() is True

    def testRemoveMarksModifiedOnlyWhenWordPresent(self):
        """Removing a present word marks modified; removing an absent word does not."""
        v = Vocabulary({"لفظ": 2})
        v.remove("missing_ورڈ")
        assert v.isModified() is False
        v.remove("لفظ")
        assert v.isModified() is True

    def testReplaceMarksModifiedOnlyWhenReplacementOccurs(self):
        """Replacing a present word marks modified; replacing an absent word does not."""
        v = Vocabulary({"غلطی": 10})
        v.replace("absent_ورڈ", "درست")
        assert v.isModified() is False
        v.replace("غلطی", "درست")
        assert v.isModified() is True

    def testSetCompletedNoOpLeavesVocabularyUnmodified(self):
        """A no-op completion toggle neither marks modified nor fires callbacks."""
        v = Vocabulary({"ٹیسٹ": 1})
        calls = []
        v.onChangeCallbacks.append(lambda: calls.append(1))

        v.setCompleted("ٹیسٹ", False)  # No-op: not yet completed, un-completing
        assert v.isModified() is False
        assert len(calls) == 0

        v.setCompleted("ٹیسٹ", True)
        assert v.isModified() is True
        assert len(calls) == 1

        calls.clear()
        v.setCompleted("ٹیسٹ", True)  # No-op: already completed
        assert v.isModified() is True
        assert len(calls) == 0

    def testSaveClearsModifiedFlag(self, tmp_path):
        """Saving a modified vocabulary marks it as unmodified."""
        filepath = tmp_path / "SaveClearsModified.txt"
        v = Vocabulary()
        v.add("سلام", 5)
        v.setCompleted("سلام", True)
        assert v.isModified() is True
        v.save(str(filepath))
        assert v.isModified() is False

    def testLoadClearsModifiedFlag(self, tmp_path):
        """A loaded vocabulary reports unmodified with its data and status intact."""
        filepath = tmp_path / "LoadClearsModified.txt"
        v = Vocabulary()
        v.add("hello", 10)
        v.setCompleted("hello", True)
        v.save(str(filepath))

        loadedV = Vocabulary.load(str(filepath))
        assert loadedV.isModified() is False
        assert loadedV.counter["hello"] == 10
        assert "hello" in loadedV.completed

    def testAddIsCompletedTrueCompletesWord(self):
        """Adding a word with isCompleted=True marks it completed in the same mutation."""
        v = Vocabulary()
        v.add("اردو", 3, isCompleted=True)
        assert v.counter["اردو"] == 3
        assert "اردو" in v.completed

    def testAddIsCompletedDefaultFalseNeverTouchesCompleted(self):
        """Adding with the default isCompleted=False neither completes nor un-completes."""
        v = Vocabulary()
        v.add("اردو", 1, isCompleted=True)
        v.add("اردو", 2)  # Default: completion status is preserved
        assert v.counter["اردو"] == 3
        assert "اردو" in v.completed

        v.add("python", 1)  # Default: a fresh word stays uncompleted
        assert "python" not in v.completed

    def testAddIsCompletedFiresExactlyOneNotification(self):
        """Introducing a completed word is a single mutation with a single notification."""
        v = Vocabulary()
        calls = []
        v.onChangeCallbacks.append(lambda: calls.append(1))
        v.add("اردو", 3, isCompleted=True)
        assert len(calls) == 1
        assert "اردو" in v.completed

    def testReplaceFiresExactlyOneNotification(self):
        """Replacing a completed word fires exactly one notification."""
        v = Vocabulary({"غلطی": 10})
        v.setCompleted("غلطی", True)
        calls = []
        v.onChangeCallbacks.append(lambda: calls.append(1))
        v.replace("غلطی", "درست")
        assert len(calls) == 1
        assert v.counter["درست"] == 10
        assert "درست" in v.completed

    def testNotifyChangesPrivateAndSetsDirty(self):
        """notifyChanges is private, and _notifyChanges commits the modified flag."""
        v = Vocabulary()
        assert not hasattr(v, "notifyChanges")
        v._notifyChanges()
        assert v.isModified() is True

# ******************************************************************************
class TestSuggestion:

    def testBlankConstructionWithDefaults(self):
        """Verify that Suggestion() constructs the blank suggestion with default field values."""
        blank = Suggestion()
        assert blank.arabic == ""
        assert blank.encodedRoman == ""
        assert blank.frequency == 0
        assert blank.isUndefined()

    def testPartialConstructionFillsRemainingDefaults(self):
        """Verify that constructing with a single field leaves the remaining fields at their defaults."""
        s = Suggestion(arabic="کتاب")
        assert s.encodedRoman == ""
        assert s.frequency == 0

    def testIsUndefinedWhenArabicEmptyOrFrequencyZero(self):
        """Verify isUndefined is True when arabic is empty or frequency is zero, and False only when both are set."""
        assert Suggestion().isUndefined()
        assert Suggestion(arabic="کتاب").isUndefined()
        assert Suggestion(frequency=1).isUndefined()
        assert not Suggestion(arabic="کتاب", frequency=1).isUndefined()

    def testExplicitFullConstructionUnchanged(self):
        """Verify that the existing three-argument construction still works."""
        s = Suggestion("کتاب", "KTAB", 4643)
        assert s == Suggestion(arabic="کتاب", encodedRoman="KTAB", frequency=4643)
        assert not s.isUndefined()

# ******************************************************************************
class TestRomanAlfaz:

    def testDefaultVocabularyLoadsWhenNoneProvided(self):
        """Verify that RomanAlfaz loads the default dictionary if input is omitted."""
        ra = RomanAlfaz(vocabularies=None)
        assert len(ra.vocabularies) == 1
        assert "KY" in ra.symSpell.words
        assert ra.symSpell.words["KE"] == 743949

    def testAddVocabularyUpdatesStateAndSumsCollisions(self):
        """Verify that adding new vocabularies triggers compilation and combines frequencies."""
        v1 = Vocabulary({"دنیا": 10, "وزیر": 5})
        v2 = Vocabulary({"دنیا": 5, "ضرورت": 2})

        ra = RomanAlfaz([v1])

        # Assert initial states
        assert ra.symSpell.words["DNYA"] == 10
        assert "ZRORT" not in ra.symSpell.words

        # Dynamically inject second vocabulary
        ra.addVocabulary(v2)

        # Ensure dynamic compilation combined fields and solved word collisions by summing frequencies
        assert len(ra.vocabularies) == 2
        assert ra.symSpell.words["DNYA"] == 15  # 10 + 5
        assert ra.symSpell.words["WZYR"] == 5
        assert ra.symSpell.words["ZRORT"] == 2

    def testRecompileAssertionNamesUnmappedWord(self):
        """The recompile unmapped-character assertion names the offending word."""
        v = Vocabulary({"abc": 1})  # Latin chars are outside the Arabic->Roman map
        with pytest.raises(AssertionError) as excinfo:
            RomanAlfaz([v])
        assert "abc" in str(excinfo.value)

    def testRemoveVocabularyPurgesAndRecalculates(self):
        """Verify that removing a vocabulary drops its frequency weights immediately."""
        v1 = Vocabulary({"دنیا": 10, "وزیر": 5})
        v2 = Vocabulary({"دنیا": 5})

        ra = RomanAlfaz([v1, v2])
        assert ra.symSpell.words["DNYA"] == 15

        # Remove the second vocabulary
        ra.removeVocabulary(v2)

        assert len(ra.vocabularies) == 1
        assert ra.symSpell.words["DNYA"] == 10  # Reduced back down to v1's total
        assert "v2" not in ra.vocabularies

    def testVocabularyMutationsTriggerObserverUpdates(self):
        """Verify that direct mutations on Vocabulary instances notify listeners dynamically."""
        v1 = Vocabulary({"کتاب": 10})
        ra = RomanAlfaz([v1])

        assert ra.symSpell.words["KTAB"] == 10

        # 1. Test Dynamic Addition
        v1.add("کتاب", count=5)  # Increase frequency
        assert ra.symSpell.words["KTAB"] == 15

        v1.add("دنیا", count=3)   # Fresh item insertion
        assert ra.symSpell.words["DNYA"] == 3

        # 2. Test Dynamic Replacement
        v1.replace("کتاب", "کلام")
        assert "KTAB" not in ra.symSpell.words
        assert ra.symSpell.words["KLAM"] == 15

        # 3. Test Dynamic Removal
        v1.remove("کلام")
        assert "KLAM" not in ra.symSpell.words


    def testHomonymCollisionMergingInReverseMapping(self):
        """Verify that multiple different Arabic words resolving to the same Roman key merge correctly."""
        # Imagine 'wordA' and 'wordB' map to identical Roman stems via simulated function overrides
        v1 = Vocabulary({"کرون": 10})
        v2 = Vocabulary({"کروں": 20, "کرون": 5})

        ra = RomanAlfaz([v1, v2])

        # Core engine gets the global cumulative weight across both strings (10 + 20 + 5)
        assert ra.symSpell.words["KRON"] == 35

        # Reverse matrix splits them up into descriptive keys with summed internal counts
        reverseSet = ra.reverseMapping["KRON"]
        assert ("کرون", 15) in reverseSet
        assert ("کروں", 20) in reverseSet

    def testHasWordReturnsTrueForStoredWord(self):
        """Verify that hasWord reports True for a word stored in the dictionary."""
        ra = RomanAlfaz([Vocabulary({"کتاب": 10})])

        assert ra.hasWord("کتاب") is True

    def testHasWordReturnsFalseForAbsentWord(self):
        """Verify that hasWord reports False for a word that is not in the dictionary."""
        ra = RomanAlfaz([Vocabulary({"کتاب": 10})])

        assert ra.hasWord("قلم") is False

    def testHasWordMatchesPositionalVariantSpelling(self):
        """Verify that a stored word is still found when queried in positional variant forms."""
        # Stored in base KAF form; normalization folds it to the Urdu KEHEH base form.
        ra = RomanAlfaz([Vocabulary({"كتاب": 10})])

        # Base-form KEHEH query matches the normalized stored key
        assert ra.hasWord("کتاب") is True
        # KAF + final-form BEH (U+FE90) surface spelling still matches
        assert ra.hasWord("كتاﺐ") is True

    def testHasWordToleratesDiacriticsAndTatweel(self):
        """Verify that input differing from the stored word only in diacritics or tatweel is still present."""
        ra = RomanAlfaz([Vocabulary({"محمد": 10})])

        # Arabic vocalization marks are stripped during normalization
        assert ra.hasWord("مُحَمَّدٌ") is True
        # Tatweel (U+0640) is stripped during normalization
        assert ra.hasWord("مـحمد") is True

    def testHasWordReturnsFalseForEmptyInput(self):
        """Verify that an empty input string reports False without erroring."""
        ra = RomanAlfaz([Vocabulary({"کتاب": 10})])

        assert ra.hasWord("") is False

    def testHasWordFindsWordFromAnyAttachedVocabulary(self):
        """Verify that a word stored in any attached vocabulary is reported present."""
        v1 = Vocabulary({"کتاب": 10})
        v2 = Vocabulary({"دنیا": 5})

        ra = RomanAlfaz([v1, v2])

        assert ra.hasWord("کتاب") is True
        assert ra.hasWord("دنیا") is True

    def testHasWordFlipsFalseAfterRemoveVocabulary(self):
        """Verify that removing the vocabulary holding a word makes hasWord report False."""
        v1 = Vocabulary({"کتاب": 10})
        ra = RomanAlfaz([v1])

        assert ra.hasWord("کتاب") is True

        ra.removeVocabulary(v1)

        assert ra.hasWord("کتاب") is False


# ******************************************************************************
