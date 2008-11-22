from __future__ import division
import sys
import os
import re

# XXX couldn't get relative imports working so adjust the path
#currentDir = os.path.abspath(os.path.dirname(__file__))
#if currentDir not in sys.path:
#    sys.path.insert(0, currentDir)
#parentDir = os.path.join(currentDir, os.path.pardir)
#if parentDir not in sys.path:
#    sys.path.insert(0, parentDir)



def sortDict(d, reverse=False):
    """Sort dictionary keys by their values

    >>> sortDict({"Richard": 23, "Andrew": 21, "James": 15})
    ['James', 'Andrew', 'Richard']
    """
    e = d.keys()
    e.sort(cmp=lambda a,b: cmp(d[a],d[b]))
    if reverse:
        e.reverse()
    return e


def anyIn(l1, l2):
    """Return values in l1 that exist in l2

    >>> anyIn([1,2], [2,3])
    2
    >>> anyIn([1,2], [3])
    
    """
    for v1 in l1:
        if v1 in l2:
            return v1
    return None
def allIn(l1, l2):
    """Return true if all of first list is in second list

    >>> allIn([1,2], [2,3])
    False
    >>> allIn([1,2], [1,2])
    True
    """
    for v1 in l1:
        if v1 not in l2:
            return False
    return True


def difference(l1, l2):
    """Return indices in list that differ

    >>> difference([1,2,2,4], [1,2,3,4])
    [2]
    """
    indices = []
    for i, (v1, v2) in enumerate(zip(l1, l2)):
        if v1 != v2:
            indices.append(i)
    return indices

def unique(l):
    """Return unique elements of list

    >>> unique([1, 2, 3, 2, 2, 4])
    [1, 2, 3, 4]
    """
    seen = {}
    result = []
    for item in l:
        if item in seen: continue
        seen[item] = 1
        result.append(item)
    return result


def average(l):
    """The list average value

    >>> average([1, 2, 3, 4, 0])
    2.0
    """
    if l:
        return sum(l) / len(l)
    else:
        return 0


def flatten(l):
    """Expand all sublists into a single list

    >>> flatten([1, [2, 3, 4], 5])
    [1, 2, 3, 4, 5]
    """
    if isinstance(l,list):
        return sum(map(flatten, l),[])
    else:
        return [l]


def extractInt(s):
    """Extract integer from string

    >>> extractInt('hello 99!')
    99
    """
    return int('0' + ''.join(c for c in s if c in '1234567890'))


def normalizeStr(s):
    """Remove characters that make string comparison difficult from copied text"""
    #s = s.decode('utf-8')
    return re.sub('\s+', ' ', re.sub('[\n\r\t]', '', s)).strip()


def pretty(var, depth=0):
    """
    >>> pretty([1, 2, 3])
    '1\\n2\\n3'
    >>> pretty({'a': 1, 'b': 2, 'c': 3})
    'a: 1\\nc: 3\\nb: 2'
    """
    if type(var) == type([]):
        return '\n'.join(depth*' ' + pretty(item, depth+1) for item in var)
    elif type(var) == type(()):
        return ', '.join(pretty(item, depth+1) for item in var)
    elif type(var) == type({}):
        return '\n'.join(depth*' ' + '%s: %s' % (pretty(k, depth+1), pretty(v, depth+1)) for (k, v) in var.items())
    else:
        return str(var)


def buildUrlRE(urls):
    """create a regular expression to match all given urls

    >>> print buildUrlRE(['http://www.google.com.au/search?q=gelati&ie=utf-8', 'http://www.google.com.au/search?q=pasta&ie=utf-8', 'http://www.google.com.au/search?q=pizza&ie=utf-8'])
    http\\:\\/\\/www\\.google\\.com\\.au\\/search\\?q\\=.*\\&ie\\=utf\\-8
    """
    # find common start and end of urls
    start_i = commonStart(urls)
    # escape url
    urlRE = re.escape(urls[0][:start_i]) + '.*'
    end_i = -commonStart([strReverse(url) for url in urls])
    if end_i < 0:
        # found matching end part
        urlRE += re.escape(urls[0][end_i:])

    p = re.compile(urlRE)
    for url in urls:
        if not p.match(url):
            raise Exception("url (%s) does not match regular expression (%s)" % (url, urlRE))
    return urlRE


def commonStart(ss):
    """Takes a list of strings and returns first index where strings differ

    >>> commonStart(['happy birthday', 'happy holiday'])
    6
    >>> commonStart(['happy', 'happy'])
    5
    """
    try:
        first_s = ss[0]
        for i, ch in enumerate(first_s):
            for s in ss:
                if ch != s[i]:
                    raise IndexError
    except IndexError:
        # mismatch so finish loop and return current index
        pass 
    else:
        # whole string matches, so move index past end
        i += 1
    return i

# reverse a string efficiently
strReverse = lambda s: ''.join([s[-1 - i] for i in xrange(len(s))])
