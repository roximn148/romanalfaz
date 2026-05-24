# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
from unittest.mock import mock_open, patch

import pytest

from romanalfaz.engine import Vocabulary


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
        mockFile.side_effect = IOError("Disk Full Error")

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

# ******************************************************************************
