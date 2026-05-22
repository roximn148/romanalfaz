#-*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
class RomanAlfazError(Exception):
    """Base exception for the RomanAlfaz package."""
    pass

class DictionaryNotFoundError(RomanAlfazError):
    """Raised when the specified SymSpell dictionary file cannot be found."""
    pass


# ******************************************************************************
