.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

********************************************************************************
Usage
********************************************************************************

Core Concepts
================================================================================

Tafseer Encoding
----------------
Romanized Urdu features massive phonetic variation (e.g., "khair", "kher", "khayr").
The engine normalizes these spelling gaps into a strict structural intermediate
format before querying the dictionary. This drastically improves match accuracy.
The details of the :ref:`algorithm<TafseerAlgorithmDetailsSection>` and its
:ref:`implementation<AlgorithmImplementationSection>` can be seen in the relevant
sections.

SymSpellPy Backend
------------------
Instead of relying purely on complex linguistic rules, `romanalfaz` processes
the intermediate string through a symmetric delete spelling correction algorithm.
This enables ultra-fast predictive matching, even if the user introduces typos
or non-standard phonetic spellings.

Built-in Vocabulary
-------------------
Instantiating the class automatically loads the include baseline, 5000-word
vocabulary. You can also provide a bigger and more comprehensive or domain-
specific vocabulary to use.

Word-Level Inputs
-----------------
:py:meth:`~romanalfaz.engine.RomanAlfaz.suggest` function processes
*single words only*. It is your responsibility to tokenize sentences or
larger paragraphs into individual words before passing them to the function.

Outputs and Edit Distance
-------------------------
The :py:meth:`~romanalfaz.engine.RomanAlfaz.suggest` function always returns
a **3-tuple** representing three lists of :py:class:`~romanalfaz.engine.Suggestion`
in each of the following matching tiers:

1. Exact Matches,
2. One-Edit Distance Matches, and
3. Two-Edit Distance Matches

The ``distance`` parameter determines the maximum search depth. The function
will always include the lowest tiers as well and return results across
all matching levels up to your configured limit.


Detailed Usage Scenarios
================================================================================
Handling Predictive Suggestions
-------------------------------
When converting a word, you can request the top `N` closest vocabulary matches
instead of just a single result or a large number of results.

..  code-block:: python

    import romanalfaz

    ra = romanalfaz.RomanAlfaz()

    # Retrieve the top 3 best matching Arabic-script predictions
    suggestions, _, _ = ra.suggest("kam", maxPredictions=3)

    for item in suggestions:
        print(f"Word: {item.arabic} | Frequency: {item.frequency}")


Batch Transliteration
---------------------
.. todo:: Add batch processing instructions


Configuration and Customization
================================================================================
You can override or supplement the default dictionary with your own specialized
precompiled vocabulary list or frequency dictionary.

.. todo:: Add instructions on how manage multiple vocabularies.

Common Errors & Troubleshooting
================================================================================

* **DictionaryNotFoundError**: The precompiled vocabulary asset failed to load.

  Reinstall the package or explicitly pass a valid path

* **Word lookup fails**: The word does not exist in the SymSpell vocabulary list.

  Add the target word and its relative frequency to your dictionary file.
