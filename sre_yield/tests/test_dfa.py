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

    def test_prune_dotstar(self):
        d = dfa.dot_star_dfa()
        dfa.knockout(d, 'foo')
        d.recursive_prune()
        import re
        print d.to_regex()
        r = re.compile(d.to_regex() + '$')
        self.assertTrue(r.match('a' * 20))
        self.assertFalse(r.match('foo-bar'))

    def test_prune2(self):
        d = dfa.dot_star_dfa()
        dfa.knockout(d, 'aa')
        dfa.knockout(d, 'bb')
        import re
        d.recursive_prune()
        print d.to_regex()
        r = re.compile(d.to_regex() + '$')
        self.assertTrue(r.match('c' * 20))
        self.assertFalse(r.match('a' * 20))
        self.assertFalse(r.match('b' * 20))

class TestKnockout(TestCase):
    def test_complex_knockout(self):
        d = dfa.dot_star_dfa(al=dfa.DOTALL_ALPHABET)
        dfa.knockout(d, 'abc')
        d.recursive_prune()
        # (?:[^a]+|a(?:[^b]+|b[^c]*|)|) is wrong.  first [^a] should not have +
        self.assertEqual('(?:[^a].*|a(?:[^b].*+|b[^c].*|)|)', d.to_regex())

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

    def test_add_empty(self):
        d = dfa.dot_plus_dfa()
        self.assertEqual(
            [(None, 2, False),
             (None, 2, True)],
            dfa._debug_numbers(d, map(ord, '\na')))
        dfa.add(d, '')
        self.assertEqual(
            [(None, 2, True),
             (None, 2, True)],
            dfa._debug_numbers(d, map(ord, '\na')))


class TestBuild(TestCase):
    def test_choices(self):
        d = dfa.build_dfa_from_choices(('abc', 'def'))
        self.assertEqual('(?:abc|def)', d.to_regex())

class TestDebugFuncs(TestCase):
    def test_debug_numbers(self):
        d = dfa.dot_plus_dfa()
        keys = map(ord, '\nabc')
        n = dfa._debug_numbers(d, keys)
        self.assertEqual(2, len(n))
        self.assertEqual((None, 2, 2, 2, False), n[0])
        self.assertEqual((None, 2, 2, 2, True), n[1])

    def test_debug_table(self):
        d = dfa.dot_plus_dfa()
        keys = map(ord, '\nabc')
        n = dfa._debug_table(d, keys)
        self.assertMultiLineEqual("""\
        \\n    a    b    c
0001: ____ 0002 0002 0002
0002: ____ 0002 0002 0002 A""", n)
