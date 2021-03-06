
### Utilities

import functools

def cached(oldMethod):
    """Decorator for making a method with no arguments cache its result"""
    storageName = f'_cached_{oldMethod.__name__}'
    @functools.wraps(oldMethod)
    def newMethod(self):
        if not hasattr(self, storageName):
            setattr(self, storageName, oldMethod(self))
        return getattr(self, storageName)
    return newMethod

def argsToString(args):
    names = (f'{a[0]}={a[1]}' if isinstance(a, tuple) else str(a) for a in args)
    joinedArgs = ', '.join(names)
    return f'({joinedArgs})'

def areEquivalent(a, b):
    """Whether two objects are equivalent, i.e. have the same properties.

    This is only used for debugging, e.g. to check that a Distribution is the
    same before and after pickling. We don't want to define __eq__ for such
    objects since for example two values sampled with the same distribution are
    equivalent but not semantically identical: the code
        X = (0, 1)
        Y = (0, 1)
    does not make X and Y always have equal values!"""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if not areEquivalent(x, y):
                return False
        return True
    elif isinstance(a, (set, frozenset)) and isinstance(b, (set, frozenset)):
        if len(a) != len(b):
            return False
        mb = set(b)
        for x in a:
            found = False
            for y in mb:
                if areEquivalent(x, y):
                    mb.remove(y)
                    found = True
                    break
            if not found:
                return False
        return True
    elif isinstance(a, dict) and isinstance(b, dict):
        if len(a) != len(b):
            return False
        for x, v in a.items():
            found = False
            for y, w in b.items():
                if areEquivalent(x, y) and areEquivalent(v, w):
                    del b[y]
                    found = True
                    break
            if not found:
                return False
        return True
    elif hasattr(a, 'isEquivalentTo'):
        return a.isEquivalentTo(b)
    elif hasattr(b, 'isEquivalentTo'):
        return b.isEquivalentTo(a)
    else:
        return a == b

class ParseError(Exception):
    """An error produced by attempting to parse an invalid Scenic program."""
    pass

class RuntimeParseError(ParseError):
    """A Scenic parse error generated during execution of the translated Python."""
    pass

class InvalidScenarioError(Exception):
    """Error raised for syntactically-valid but otherwise problematic Scenic programs."""
    pass

class InconsistentScenarioError(InvalidScenarioError):
    """Error for scenarios with inconsistent requirements."""
    def __init__(self, line, message):
        self.lineno = line
        super().__init__('Inconsistent requirement on line ' + str(line) + ': ' + message)
