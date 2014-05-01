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

class UnicodeTest(unittest.TestCase):
    def testUnicodeCharset(self):
        v = sre_yield.AllStrings('.', charset=sre_yield.UNICODE_BMP_CHARSET,
                                 want_unicode=True)
        self.assertEquals(65535, len(v)) # No \n
        v = sre_yield.AllStrings('.', flags=re.DOTALL,
                                 charset=sre_yield.UNICODE_BMP_CHARSET,
                                 want_unicode=True)
        self.assertEquals(65536, len(v)) # With \n

    def testCategories(self):
        self.maxDiff = None
        cat_chars = 'wWdDsS'
        all_unicode = map(unichr, xrange(65536))
        for c in cat_chars:
            r = re.compile('\\' + c, re.U)
            print "Checking", c
            matching = [i for i in all_unicode if r.match(i)]
            self.assertGreater(len(matching), 5)
            parsed = sre_yield.AllStrings('\\' + c, flags=re.U,
                                          want_unicode=True,
                                          charset=sre_yield.UNICODE_BMP_CHARSET)
            p = set(parsed[:])
            m = set(matching)
            for i in m:
                if i not in p:
                    print "Missing", ord(i), unicodedata.category(i)

            for i in p:
                if i not in m:
                    print "Extra", ord(i), unicodedata.category(i)
            self.assertEquals(sorted(matching), sorted(parsed[:]))

    def testMixedRange(self):
        parsed = sre_yield.AllStrings('[\d ]', flags=re.U, want_unicode=True,
                                      charset=sre_yield.UNICODE_BMP_CHARSET)
        l = list(parsed)
        print l
        self.assertGreater(len(l), 11)
        self.assertEquals(u'0', l[0])
        self.assertEquals(u'9', l[9])
        self.assertEquals(u'\u0660', l[10])
        # ...
        self.assertEquals(u'\uff19', l[-2])
        self.assertEquals(u' ', l[-1])

if __name__ == '__main__':
    unittest.main()

