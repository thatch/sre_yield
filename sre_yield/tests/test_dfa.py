from sre_yield import dfa
from unittest import TestCase

class TestHelpers(TestCase):
    def test_esc(self):
        self.assertEqual('a', dfa.esc(ord('a')))
        self.assertEqual('\\x00', dfa.esc(0))
    def test_charclass1(self):
        self.assertEqual('\\x00', dfa.charclass([0]))
    def test_charclass2(self):
        self.assertEqual('[a-z]', dfa.charclass(range(ord('a'), ord('z')+1)))
    def test_charclass3(self):
        self.assertEqual('[\\x00A-Za-z]', dfa.charclass(
            sorted([0] + range(ord('a'), ord('z') + 1) + range(ord('A'), ord('Z') + 1))))

class TestSimpleRegex(TestCase):
    def test_build_dotstar(self):
        self.assertEqual('a*', dfa.dot_star_dfa([ord('a')]).to_regex())
    def test_build_dotplus(self):
        self.assertEqual('aa*', dfa.dot_plus_dfa([ord('a')]).to_regex())

class TestReachability(TestCase):
    def test_reachable_base(self):
        d1 = dfa.DFA()
        self.assertFalse(d1.reachable())
        d1.accepting = True
        self.assertTrue(d1.reachable())

    def test_reachable_interesting(self):
        d1 = dfa.DFA()
        d2 = dfa.DFA()
        d3 = dfa.DFA()
        d4 = dfa.DFA()
        d1.tab[0] = d2
        d2.tab[1] = d3
        d2.tab[2] = d4
        self.assertFalse(d1.reachable())
        d4.accepting = True
        self.assertTrue(d1.reachable())

class TestPrune(TestCase):
    def test_basic_prune(self):
        d1 = dfa.DFA()
        d2 = dfa.DFA()
        d3 = dfa.DFA()
        d4 = dfa.DFA()
        d1.tab[0] = d2
        d2.tab[1] = d3
        d2.tab[2] = d4
        d4.accepting = True
        self.assertEqual(d2.tab[1], d3)
        d1.recursive_prune()
        self.assertEqual(d2.tab[1], None)

class TestAdd(TestCase):
    def test_simple(self):
        d = dfa.DFA()
        dfa.add(d, 'foo')
        self.assertEqual('foo', d.to_regex())
        dfa.add(d, 'fab')
        self.assertEqual('f(?:ab|oo)', d.to_regex())
        dfa.add(d, 'fob')
        self.assertEqual('f(?:ab|o(?:b|o))', d.to_regex())
        dfa.add(d, 'food')
        dfa.knockout(d, 'fob')
        d.recursive_prune()
        self.assertEqual('f(?:ab|oo(?:d|))', d.to_regex())

    def test_alternation(self):
        d = dfa.DFA()
        dfa.add(d, 'f')
        dfa.add(d, 'fa')
        dfa.add(d, 'fb')
        self.assertEqual('f(?:a|b|)', d.to_regex())

class TestBuild(TestCase):
    def test_choices(self):
        d = dfa.build_dfa_from_choices(('abc', 'def'))
        self.assertEqual('(?:abc|def)', d.to_regex())
