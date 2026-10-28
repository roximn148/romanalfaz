.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

********************************************************************************
Vocabulary File CLI
********************************************************************************
The ``romanalfaz`` command inspects and rewrites SymSpell vocabulary files.
A vocabulary file stores one ``word$frequency`` entry per line.

Every file command applies a normalization method, ``urdu-spell`` by default,
so that comparisons and rewrites are made between canonical forms of words
rather than between the spellings written in the file. Rewrites never touch
the input file unless ``--in-place`` is passed explicitly.

Command Overview
================================================================================

``validate FILE``
   Reports malformed lines, non-canonical spellings, words that normalize to
   empty or cannot be romanized, and duplicate canonical forms.

``normalize FILE``
   Rewrites the file in canonical form, summing the frequencies of entries that
   normalize to the same word. Requires one of ``-o/--output``, ``--in-place``,
   or ``--preview``.

``words FILE``
   Prints the canonical words, sorted, without frequencies. ``-o`` writes them
   to a file instead.

``merge FIRST SECOND``
   Unions two files by canonical word. Shared words keep one entry whose
   frequency is the sum of both. Requires ``-o``.

``subtract FIRST SECOND``
   Removes the words of ``SECOND`` from ``FIRST``, matched by canonical form.
   Surviving words keep the frequency they had in ``FIRST``. Requires ``-o``.

``list``
   Describes every available normalization method, the scope it is built for,
   and its pipeline stages.

Examples
================================================================================
Check the bundled vocabulary:

.. code-block:: console

   $ romanalfaz validate src/romanalfaz/UrduWords5k.sym
   src/romanalfaz/UrduWords5k.sym: no issues found (4994 words)

Preview a rewrite without touching the file:

.. code-block:: console

   $ romanalfaz normalize src/romanalfaz/UrduWords5k.sym --preview

Write the canonical form to a new file:

.. code-block:: console

   $ romanalfaz normalize words.sym -o words.canonical.sym

Export the sorted word list:

.. code-block:: console

   $ romanalfaz words words.sym -o words.txt

Union two lists, then remove a blacklist:

.. code-block:: console

   $ romanalfaz merge words.sym extra.sym -o merged.sym
   $ romanalfaz subtract merged.sym blacklist.sym -o final.sym

Inspect the registered normalization methods:

.. code-block:: console

   $ romanalfaz list

The same commands are available as ``python -m romanalfaz``.

Selecting a Normalization Method
================================================================================
``--normalize METHOD`` selects the method by its label. ``urdu-spell`` is the
only method currently registered; the label is accepted by ``validate``,
``normalize``, ``words``, ``merge``, and ``subtract``.

New methods are added by writing their module and registering one entry in
:py:data:`romanalfaz.normalization.NORMALIZATION_METHODS`; ``list`` and
``--normalize`` then pick them up with no other change.

Output and Exit Codes
================================================================================
Reports and exported data are written to standard output, while status
messages and warnings go to standard error.

- ``0``: the command succeeded (``validate`` found no issues).
- ``1``: ``validate`` found issues, or the command hit an I/O error such as an
  unreadable file.
- ``2``: usage error, such as an unknown method or a missing write target.

API Reference
================================================================================
.. automodule:: romanalfaz.cli
   :members:
   :undoc-members:  # includes objects without docstrings
   :show-inheritance: # shows base classes
