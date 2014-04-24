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

import unittest
import sre_yield

class UnicodeTest(unittest.TestCase):
    def test_literal(self):
        v = sre_yield.AllStrings(u'\u1234')
        self.assertEquals(1, len(v))
        self.assertEquals(u'\u1234', v[0])
    def test_range(self):
        v = sre_yield.AllStrings(u'[\u1234-\u1250]')
        print list(v)
        self.assertEquals(29, len(v))
        self.assertEquals(u'\u1234', v[0])
        self.assertEquals(u'\u1250', v[-1])

