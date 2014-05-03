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

import re
import sys
import unittest
import unicodedata

import sre_yield

if sre_yield.CAN_REPRESENT_BARE_SURROGATES:
    ALL_UNICODE = map(unichr, xrange(65536))
else:
    ALL_UNICODE = [unichr(c) for c in xrange(65536) if c < 0xd800 or c >= 0xdc00]

class TestUnicode(unittest.TestCase):
    def testUnicodeCharset(self):
        v = sre_yield.AllStrings(u'.', flags=re.U)
        if sre_yield.CAN_REPRESENT_BARE_SURROGATES:
            self.assertEquals(0xffff, len(v)) # No \n
        else:
            self.assertEquals(0xffff-0x400, len(v)) # No \n or surrogates
        v = sre_yield.AllStrings(u'.', flags=re.DOTALL | re.U)
        if sre_yield.CAN_REPRESENT_BARE_SURROGATES:
            self.assertEquals(0x10000, len(v)) # With \n
        else:
            self.assertEquals(0x10000-0x400, len(v))

    def testMixedRange(self):
        parsed = sre_yield.AllStrings('[\d ]', flags=re.U)
        l = list(parsed)
        print l
        self.assertGreater(len(l), 11)
        self.assertEquals(u'0', l[0])
        self.assertEquals(u'9', l[9])
        self.assertEquals(u'\u0660', l[10])
        # ...
        self.assertEquals(u'\uff19', l[-2])
        self.assertEquals(u' ', l[-1])


def test_categories():
    """Ensure that `re` and `sre_yield` agree on the contents of a category."""
    cat_chars = 'wWdDsS'
    for c in cat_chars:
        yield category_runner, c


def category_runner(cat_char):
    r = re.compile('\\' + cat_char, re.U)
    print "Checking", cat_char
    matching = [i for i in ALL_UNICODE if r.match(i)]
    assert len(matching) > 5
    parsed = sre_yield.AllStrings('\\' + cat_char, flags=re.U)
    p = set(parsed[:])
    m = set(matching)
    for i in m:
        if i not in p:
            print "Missing", ord(i), unicodedata.category(i)

    for i in p:
        if i not in m:
            print "Extra", ord(i), unicodedata.category(i)

    assert sorted(matching) == sorted(parsed[:])


if __name__ == '__main__':
    unittest.main()
