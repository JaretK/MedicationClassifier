#!/usr/bin/env python
# -*- coding: utf-8 -*-

# imports
from __future__ import absolute_import, print_function, division
import re

#abseil
from absl import app

class MedicationAbstract:
    CLASS = None
    SUBCLASS = None
    GENERIC = None
    def __str__(self):
        raise NotImplementedError
    def _class(self):
        return self.CLASS.lower()
    def _subclass(self):
        return self.SUBCLASS.lower()
    def _generic(self):
        return self.GENERIC.lower()


class Medication(MedicationAbstract):
    def __init__(self, superclass, subclass, generic):
        self.CLASS = superclass
        self.SUBCLASS = subclass
        self.GENERIC = generic
    def __str__(self):
        return '{}\t{}\t{}'.format(
            self.CLASS, self.SUBCLASS, self.GENERIC)

    def __repr__(self):
        return str(self)

# testing 
def main(argv):
    del argv
    pass

if __name__ == "__main__":
    app.run(main)


