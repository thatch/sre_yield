=========
sre_yield
=========

Quick Start
===========

The goal of ``sre_yield`` is to efficiently generate all values that can match a
given regular expression, or count possible matches efficiently.  It uses the
parsed regular expression, so you get a much more accurate result than trying
to just split strings.

.. code-block:: pycon

    >>> s = 'foo|ba[rz]'
    >>> s.split('|')  # bad
    ['foo', 'ba[rz]']

    >>> import sre_yield
    >>> list(sre_yield.Values(s))  # better
    ['foo', 'bar', 'baz']

It does this by walking the tree as constructed by ``sre_parse`` (same thing
used internally by the ``re`` module), and constructing chained/repeating
iterators as appropriate.  There may be duplicate results, depending on your
input string though -- these are cases that ``sre_parse`` did not optimize.

.. code-block:: pycon

    >>> import sre_yield
    >>> list(sre_yield.Values('.|a', charset='ab'))
    ['a', 'b', 'a']

...and happens in simpler cases too:

.. code-block:: pycon

    >>> list(sre_yield.Values('a|a'))
    ['a', 'a']
    >>> list(sre_yield.Values('[aa]'))
    ['a', 'a']


Quirks
======

The membership check, ``'abc' in values_obj`` is by necessity fullmatch -- it
must cover the entire string.  Imagine that it has ``^(...)$`` around it.
Because ``re.search`` can match anywhere in an arbitrarily string, emulating
this would produce a large number of junk matches -- probably not what you
want.  (If that is what you want, add a ``.*`` on either side.)

Here's a quick example, using the presidents regex from http://xkcd.com/1313/

.. code-block:: pycon

    >>> s = 'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls'

    >>> import re
    >>> re.search(s, 'kennedy') is not None  # note .search
    True
    >>> v = sre_yield.Values(s)
    >>> v.__len__()
    23
    >>> 'bu' in v
    True
    >>> v[:5]
    ['bu', 'rt', 'nt', 'ce', 'oe']

If you do want to emulate search, you end up with a large number of matches
quickly.  Limiting the repetition a bit helps, but it's still a very large
number.

.. code-block:: pycon

    >>> v2 = sre_yield.Values('.{,30}(' + s + ').{,30}')
    >>> v2.__len__()  # too big for int
    57220492262913872576843611006974799576789176661653180757625052079917448874638816841926032487457234703154759402702651149752815320219511292208238103L
    >>> 'kennedy' in v2
    True



Reporting Bugs, etc.
====================

We welcome bug reports -- see our issue tracker on `Google Code
<https://code.google.com/p/sre-yield/>`_ to see if it's been reported before.
If you'd like to discuss anything, we have a `Google Group
<https://groups.google.com/group/sre_yield>`_ as well.


Related Modules
===============

We're aware of three similar modules, but each has a different goal.


xeger
-----

Xeger was originally written `in Java <https://code.google.com/p/xeger/>`_ and
ported `to Python <https://bitbucket.org/leapfrogdevelopment/rstr>`_.  This
generates random entries, which may suffice if you want to get just a few
matching values.  This module and ``xeger`` differ statistically in the way
they handle repetitions:

.. code-block:: pycon

    >>> import random
    >>> v = sre_yield.Values('[abc]{1,4}')
    >>> len(v)
    120

    # Now random.choice(v) has a 3/120 chance of choosing a single letter.
    >>> random.seed(1)
    >>> sum([1 if len(random.choice(v)) == 1 else 0 for _ in range(120)])
    3

    # xeger(v) has ~25% chance of choosing a single letter, because the length
    and match are chosen independently.
    > from rstr import xeger
    > sum([1 if len(xeger('[abc]{1,4}')) == 1 else 0 for _ in range(120)])
    26

In addition, ``xeger`` differs in the default matching of ``'.'`` is for
printable characters (which you can get by setting ``charset=string.printable``
in ``sre_yield``, if desired).


sre_dump
--------

Another module that walks ``sre_parse``'s tree is ``sre_dump``, although it
does not generate matches, only reconstructs the string pattern (useful
primarily if you hand-generate a tree).  If you're interested in the space,
it's a good read.  http://www.dalkescientific.com/Python/sre_dump.html


jpetkau1
--------

Can find matches by using randomization, so sort of handles anchors.  Not
guaranteed though, but another good look at internals.
http://web.archive.org/web/20071024164712/http://www.uselesspython.com/jpetkau1.py
(and slightly older version in the announcement on `python-list
<https://mail.python.org/pipermail/python-list/2001-August/104757.html>`_).


Differences between sre_yield and the re module
===============================================

There are certainly valid regular expressions which ``sre_yield`` does not
handle.  These include things like lookarounds, backreferences, but also a few
other exceptions:

- The maximum value for repeats is system-dependant -- CPython's ``sre`` module
  there's a special value which is treated as infinite (either 2**16-1 or
  2**32-1 depending on build).  In sre_yield, this is taken as a literal,
  rather than infinite, thus (on a 2**16-1 platform):

  .. code-block:: pycon

      >>> len(sre_yield.Values('a*')[-1])
      65535
      >>> import re
      >>> len(re.match('.*', 'a' * 100000).group(0))
      100000

- The ``re`` `module docs <http://docs.python.org/2/library/re.html#regular-expression-syntax>`_
  say "Regular expression pattern strings may not contain null bytes"
  yet this appears to work fine.
- Order does not depend on greediness.
- The regex is treated as fullmatch.
- ``sre_yield`` is confused by even the simplest of anchors:

  .. code-block:: pycon

      >>> list(sre_yield.Values('foo\\b'))
      Traceback (most recent call last):
      ...
      ParseError: Anchor 'at_boundary' found after nonzero width
