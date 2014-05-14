#!/usr/bin/env python2
#
# Copyright 2011-2014 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import unittest

import sre_yield

class SpecificLengthTest(unittest.TestCase):
    def test_basic(self):
        v = sre_yield.AllStrings('a*', specific_count=[1,2,3])
        self.assertEquals(['a', 'aa', 'aaa'], list(v))

    def test_combined_with_charclass(self):
        v = sre_yield.AllStrings('[ab]*', specific_count=[1,2,3])
        self.assertEquals(['a', 'b', 'aa', 'ab', 'ba', 'bb',
                           'aaa', 'aab', 'aba', 'abb', 'baa', 'bab', 'bba',
                           'bbb'], list(v))

    def test_combined_with_alternation_outside(self):
        v = sre_yield.AllStrings('(?:a{5,10}|b{5,10})', specific_count=[1,5,8,100])
        self.assertEquals(['a'*5, 'a'*8, 'b'*5, 'b'*8], list(v))

    def test_combined_with_alternation_inside(self):
        v = sre_yield.AllStrings('(?:a|bb)+', specific_count=[0, 2, 5])
        self.assertEquals(['aa', 'abb', 'bba', 'bbbb', 'aaaaa',
                           'aaaabb', 'aaabba', 'aaabbbb', 'aabbaa', 'aabbabb',
                           'aabbbba', 'aabbbbbb', 'abbaaa', 'abbaabb',
                           'abbabba', 'abbabbbb', 'abbbbaa', 'abbbbabb',
                           'abbbbbba', 'abbbbbbbb', 'bbaaaa', 'bbaaabb',
                           'bbaabba', 'bbaabbbb', 'bbabbaa', 'bbabbabb',
                           'bbabbbba', 'bbabbbbbb', 'bbbbaaa', 'bbbbaabb',
                           'bbbbabba', 'bbbbabbbb', 'bbbbbbaa',
                           'bbbbbbabb', 'bbbbbbbba', 'bbbbbbbbbb'], list(v))

    def test_non_sequential(self):
        v = sre_yield.AllStrings('a*', specific_count=[1,10,100])
        self.assertEquals(['a', 'a'*10, 'a'*100], list(v))
