.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

********************************************************************************
Normalization Methods
********************************************************************************
The :py:mod:`romanalfaz.normalization` module is the registry of the
normalization methods available in the package. A method defines one canonical
form of Urdu arabic-script text for a specific processing scope, and lives in
its own module. The CLI selects a method by its label with ``--normalize`` and
describes the registered methods with ``romanalfaz list``.

Adding a method means writing its module and registering one entry in
:py:data:`romanalfaz.normalization.NORMALIZATION_METHODS`; the label, scope,
and pipeline stages are then available to every tool with no further change.

.. automodule:: romanalfaz.normalization
   :members:
   :undoc-members:  # includes objects without docstrings
   :show-inheritance: # shows base classes
