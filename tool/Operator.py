#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum

Operator = Enum('Operator', ('EQ', 'IEQ', 'NE', 'LG', 'GE', 'LE', 'GT', 'LT',
                             'EQ_P', 'NE_P', 'LG_P', 'GE_P', 'LE_P', 'GT_P', 'LT_P',
                             'LIKE', 'LIKE_S', 'LIKE_E', 'ILIKE', 'ILIKE_S', 'ILIKE_E',
                             'IN', 'EXISTS', 'NOT_IN', 'IS_NULL', 'IS_NOT_NULL', 'IS_EMPTY', 'IS_NOT_EMPTY'))
