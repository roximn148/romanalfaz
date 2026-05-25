.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

********************************************************************************
Quickstart
********************************************************************************
The `romanalfaz` package provides the :py:class:`~romanalfaz.engine.RomanAlfaz` class as a centralized,
easy-to-use interface for text transliterations.

You can simply import, instantiate the class and start using it.

>>> from romanalfaz import RomanAlfaz

>>> ra = RomanAlfaz()

>>> for w in 'kya haal he'.split():
...     d0, d1, d2 = ra.suggest(w, distance=2)
...     print(f"'{w}' ->")
...     print('  Exact matches: ', d0)
...     print('  One-Edit matches: ', d1)
...     print('  Two-Edit matches: ', d2)
...
'kya' ->
  Exact matches:  [('کیا', 'KYA', 108414)]
  One-Edit matches:  [('کی', 'KY', 575545), ('کہ', 'KH', 237419), ('یہ', 'YH', 128103), ('کیا', 'KYA', 108414), ('کئے', 'KYE', 14970), ('کیے', 'KYE', 4976)]
  Two-Edit matches:  []
'haal' ->
  Exact matches:  [('حال', 'HAL', 4893), ('ہال', 'HAL', 936), ('حائل', 'HAYL', 316)]
  One-Edit matches:  [('خیال', 'KHYAL', 10033), ('حال', 'HAL', 4893), ('حیات', 'HYAT', 2438), ('ہال', 'HAL', 936), ('سیال', 'SYAL', 321), ('حائل', 'HAYL', 316)]
  Two-Edit matches:  [('حاصل', 'HASL', 25881), ('حالات', 'HALAT', 6537), ('حال', 'HAL', 4893), ('حامل', 'HAML', 2227), ('آل', 'AAL', 1014), ('ہال', 'HAL', 936)]
'he' ->
  Exact matches:  [('ہے', 'HE', 466908)]
  One-Edit matches:  []
  Two-Edit matches:  []
