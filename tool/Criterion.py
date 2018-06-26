#!/usr/bin/python
# -*- coding: utf-8 -*-

from tool import Operator


class Criterion:
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value
