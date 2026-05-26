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

>>> rmWord = "kitab"
>>> # As distance is 0, received empty one and two-edit tier lists can be discarded.
>>> suggestions, _, _ = ra.suggest(rmWord, distance=0)
>>> # Take the first suggestion (if any) and use its arabic scripted word
>>> arWord = suggestions[0].arabic if suggestions else ''
>>> arWord
'کتاب'

>>> for rmWord in 'kya haal he'.split():
...    d0, d1, d2 = ra.suggest(rmWord, distance=2)
...    # Formated dump of the suggestions
...    print(f"'{rmWord}' ->")
...    print('  Exact matches:')
...    for item in d0:
...        print(f"    {item!r}")
...    print('  One-Edit matches:')
...    for item in d1:
...        print(f"    {item!r}")
...    print('  Two-Edit matches:')
...    for item in d2:
...        print(f"    {item!r}")
...
'kya' ->
  Exact matches:
    Suggestion(arabic='کیا', encodedRoman='KYA', frequency=108414)
  One-Edit matches:
    Suggestion(arabic='کی', encodedRoman='KY', frequency=575545)
    Suggestion(arabic='کہ', encodedRoman='KH', frequency=237419)
    Suggestion(arabic='یہ', encodedRoman='YH', frequency=128103)
    Suggestion(arabic='کیا', encodedRoman='KYA', frequency=108414)
    Suggestion(arabic='کئے', encodedRoman='KYE', frequency=14970)
    Suggestion(arabic='کیے', encodedRoman='KYE', frequency=4976)
  Two-Edit matches:
'haal' ->
  Exact matches:
    Suggestion(arabic='حال', encodedRoman='HAL', frequency=4893)
    Suggestion(arabic='ہال', encodedRoman='HAL', frequency=936)
    Suggestion(arabic='حائل', encodedRoman='HAYL', frequency=316)
  One-Edit matches:
    Suggestion(arabic='حاصل', encodedRoman='HASL', frequency=25881)
    Suggestion(arabic='حال', encodedRoman='HAL', frequency=4893)
    Suggestion(arabic='حامل', encodedRoman='HAML', frequency=2227)
    Suggestion(arabic='آل', encodedRoman='AAL', frequency=1014)
    Suggestion(arabic='ہال', encodedRoman='HAL', frequency=936)
    Suggestion(arabic='فعال', encodedRoman='FAAL', frequency=718)
  Two-Edit matches:
    Suggestion(arabic='حاصل', encodedRoman='HASL', frequency=25881)
    Suggestion(arabic='حالات', encodedRoman='HALAT', frequency=6537)
    Suggestion(arabic='حال', encodedRoman='HAL', frequency=4893)
    Suggestion(arabic='حامل', encodedRoman='HAML', frequency=2227)
    Suggestion(arabic='آل', encodedRoman='AAL', frequency=1014)
    Suggestion(arabic='ہال', encodedRoman='HAL', frequency=936)
'he' ->
  Exact matches:
    Suggestion(arabic='ہے', encodedRoman='HE', frequency=466908)
  One-Edit matches:
  Two-Edit matches:
