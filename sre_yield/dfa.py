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
        t.accepting = self.accepting
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
            elif k is not self:
                k.recursive_prune()

    def walk(self, s):
        buf = [self]
        for c in map(ord, s):
            if not buf[-1]: return
            buf.append(buf[-1].tab[c])
        return buf


def esc(i):
    if ord('a') <= i <= ord('z') or \
       ord('A') <= i <= ord('Z') or \
       ord('0') <= i <= ord('9'):
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
    return '[' + prefix + ''.join(x) + ']'

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
    d.tab = [None] * 256

def add(root_dfa, s):
    d = root_dfa
    for c in map(ord, s):
        if not d.tab[c]:
            d.tab[c] = DFA()
        d = d.tab[c]
    d.accepting = True

def _debug_table(root, alphabet):
    cell_width = 4
    buf = []
    idx = {root: 1}
    next_idx = 2
    queue = [root]
    # output header
    buf.append(' ' * (cell_width+2) + ' '.join('%*s' % (cell_width, esc(c)) for c in sorted(alphabet)))
    while queue:
        n = queue.pop(0)
        t = []
        t.append('%0*x:' % (cell_width, idx[n]))
        for i, x in enumerate(n.tab):
            if i in alphabet:
                if x is None:
                    t.append('_' * cell_width)
                else:
                    if x not in idx:
                        idx[x] = next_idx
                        next_idx += 1
                        queue.append(x)
                    t.append('%0*x' % (cell_width, idx[x]))
        if n.accepting:
            t.append('A')
        buf.append(' '.join(t))

    return '\n'.join(buf)
