class DFA(object):
    def __init__(self):
        self.tab = [None] * 256
        self.accepting = False
    def copy(self):
        t = DFA()
        t.tab = []
        for i in self.tab:
            if i is self:
                t.tab.append(t)
            else:
                t.tab.append(i)
        return t
    def to_regex(self):
        grouped = self._grouped()
        if not grouped:
            # This assmes we've already pruned for reachability.
            assert self.accepting
            return ''

        opts = []
        # stable sort on first character code matching
        for k, v in sorted(grouped.iteritems(), key=lambda (a, b): b):
            if k is self:
                # build charclass
                opts.append(charclass(v) + '+')
            else:
                opts.append(charclass(v) + k.to_regex())
        if self.accepting:
            if len(opts) == 1:
                if opts[0][-1] == '+':
                    return opts[0][:-1] + '*'
            opts.append('')
        if len(opts) == 1:
            return opts[0]
        return '(?:' + '|'.join(opts) + ')'

    def _grouped(self):
        grouped = {}
        for i, n in enumerate(self.tab):
            if n is not None:
                grouped.setdefault(n, []).append(i)
        return grouped

    def reachable(self):
        if self.accepting:
            return True
        for k, v in self._grouped().iteritems():
            if k is self:
                continue
            if k.reachable():
                return True
        return False
                
    def recursive_prune(self):
        for k, v in self._grouped().iteritems():
            if not k.reachable():
                for i in v:
                    self.tab[i] = None
            else:
                k.recursive_prune()


def esc(i):
    if ord('a') <= i <= ord('z') or \
       ord('A') <= i <= ord('Z'):
        return chr(i)
    else:
        return '\\x%02x' % i

def charclass(ords):
    # assumes that they're sorted.
    if len(ords) == 1:
        return esc(ords[0])
    prefix = ''
    if len(ords) > 200:
        ords = sorted(set(range(256)) - set(ords))
        prefix = '^'
    ranges = []
    for i in ords:
        if ranges and ranges[-1][1] == i - 1:
            ranges[-1][1] = i
        else:
            ranges.append([i, i])

    x = []
    for a, b in ranges:
        if a == b:
            x.append(esc(a))
        else:
            x.append(esc(a) + '-' + esc(b))
    return '[' + ''.join(x) + ']'

DOTALL_ALPHABET = list(range(256))
DOT_ALPHABET = [i for i in range(256) if i != 10]

def build_dfa(alphabet, next_state=None):
    # When alphabet is None, make it self.
    d = DFA()
    if next_state is None:
        next_state = d
    for i in alphabet:
        d.tab[i] = next_state
    return d

def build_dfa_from_choices(choices):
    d = DFA()
    for c in choices:
        add(d, c)
    return d

def dot_star_dfa(al=DOT_ALPHABET):
    d = build_dfa(al)
    d.accepting = True
    return d

def dot_plus_dfa(al=DOT_ALPHABET):
    d2 = build_dfa(al)
    d2.accepting = True
    d1 = build_dfa(al, d2)
    return d1

def knockout(root_dfa, s):
    d = root_dfa
    for c in map(ord, s):
        if not d.tab[c]: return
        # break repetitions, more generally this could use a refcount.
        if d.tab[c] is d:
            d.tab[c] = d.copy()
        d = d.tab[c]
    d.accepting = False

def add(root_dfa, s):
    d = root_dfa
    for c in map(ord, s):
        if not d.tab[c]:
            d.tab[c] = DFA()
        d = d.tab[c]
    d.accepting = True
