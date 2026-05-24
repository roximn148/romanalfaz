.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

.. include:: <isonum.txt>

RomanAlfaz (رومن الفاظ) documentation
#####################################

`RomanAlfaz` is a dictionary-based, predictive transliterator that
converts roman-script Urdu words into their arabic-script equivalents.
The tool automatically ranks and prioritizes matching suggestions
based on their real-world usage frequency.

How it Works
************
The tool processes text using a specialized two-layer transformation workflow:

1. **Intermediate Representation**: It leverages the rule-based transliteration algorithm
proposed by Tafseer Ahmed [#]_.
This converts the user's Roman Urdu input into an intermediate format
designed to bridge the phonetic and structural spelling gaps between the two scripts.

2. **Dictionary Lookup**: The engine passes this intermediate form to
SymSpellPy_ to execute
an optimized dictionary search against a precompiled vocabulary list.

Baseline Vocabulary
*******************

The baseline included dictionary is built upon the CLE Urdu 5000 dataset [#]_,
which captures the most frequently used words in the Urdu language.

Core Workflow
*************

.. _romanalfaz-workflow:

.. figure:: romanalfaz.png
   :alt: RomanAlfaz workflow chart
   :align: center
   :figwidth: 100%

   The internal workflow of the RomanAlfaz.

   **(1)** Load a dictionary,
   **(2)** ask for suggestion(s) with a word in roman script, and
   **(3)** get the suggestions(s) in arabic script.

   **Blue** arrows represent *Arabic* script and **Red** arrows represent *Roman* script.

..  [#] Roman to Urdu Transliteration using word list. (2009)
    https://cle.org.pk/clt09/download/ahmed_translit.pdf
..  [#] Urdu 5000 most Frequently Used Words
    https://www.cle.org.pk/software/ling_resources/UrduHighFreqWords.htm
..  _SymSpellPy: https://github.com/mammothb/symspellpy


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   algorithm
   engine
   utils


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`