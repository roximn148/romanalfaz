.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

Tafseer Algorithm
================================================================================
This section consists of two parts,

- The Algorithm_ internal details with explanations of each step, and
- its Implementation_ in the `RomanAlfaz` package.

--------------------------------------------------------------------------------

Algorithm
+++++++++
.. include:: ../src/romanalfaz/tafseer.ipynb
   :parser: myst_nb.docutils_

--------------------------------------------------------------------------------

Implementation
++++++++++++++
.. automodule:: romanalfaz.algorithm
   :members:
   :undoc-members:  # includes objects without docstrings
   :show-inheritance: # shows base classes
   :exclude-members: URDU_ARABIC2ROMAN_ENCODING_MAP

.. autodata:: romanalfaz.algorithm.URDU_ARABIC2ROMAN_ENCODING_MAP
   :no-value:

.. literalinclude:: ../src/romanalfaz/algorithm.py
   :language: python
   :start-after: # URDU ARABIC2ROMAN ENCODING MAP START
   :end-before: # URDU ARABIC2ROMAN ENCODING MAP END
