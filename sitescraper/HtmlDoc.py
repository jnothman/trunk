import os
import re
import urllib2
from StringIO import StringIO
from collections import defaultdict
from difflib import SequenceMatcher
from lxml import html as lxmlHtml
from HtmlXpath import HtmlXpath
from common import normalizeStr, unique



class HtmlDoc:
    """Encapsulates the Xpaths of an XML document

    >>> doc = HtmlDoc('../testdata/yahoo_search/1.html', [])
    >>> xpaths = doc.extractXpaths(doc.tree().getroot())
    >>> len(xpaths)
    294
    >>> [(xpath.get(), count) for (xpath, count) in doc.matchXpaths("Bargain prices on Digital Cameras, store variety for Digital Cameras. Compare prices and buy online at Shopzilla.")]
    [('/html[1]/body[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/ol[1]/li[1]/div[1]/div[2]', -113)]
    """

    # ignore content from these tags
    IGNORE_TAGS = 'style', 'script', 'meta', 'link'
    # user agent to use in fetching webpages
    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9a9pre) Gecko/2007100205 Minefield/3.0a9pre'
    #___________________________________________________________________________

    def __init__(self, input, output, xpaths=None):
        """Create an ElementTree of the parsed input. Input can be a url, filepath, or html"""
        self._url = None
        if not input:
            # empty input
            fp = None
        elif re.match('http://.*\..*', input):
            # input is a url
            self._url = input
            fp = urllib2.urlopen(urllib2.Request(input, None, {'User-agent': HtmlDoc.USER_AGENT}))
        elif len(input) < 1000 and os.path.exists(input):
            # input is a local file
            self._url = input
            fp = open(input)
        else:
            # try treating input as HTML
            fp = StringIO(input)
        self._tree = lxmlHtml.parse(fp) if fp else None
        # Remove tags that are not useful
        for tag in HtmlDoc.IGNORE_TAGS:
            for item in self._tree.findall('.//' + tag):
                item.drop_tree()
        
        if not xpaths:
            xpaths = self.extractXpaths(self._tree.getroot())
        self._xpaths = xpaths
        self._output = output
        self._sequence = SequenceMatcher()
    #___________________________________________________________________________

    def __len__(self):
        return len(self._xpaths)
    #___________________________________________________________________________

    def __str__(self):
        return lxmlHtml.tostring(self._tree)
    #___________________________________________________________________________

    def url(self): 
        return self._url
    #___________________________________________________________________________

    def tree(self): 
        return self._tree
    #___________________________________________________________________________

    def xpaths(self):
        return self._xpaths
    #___________________________________________________________________________

    def output(self):
        return self._output
    #___________________________________________________________________________

    def extractXpaths(self, e):
        """Return a hashtable of the xpath to each text element"""
        xpaths = defaultdict(list)
        self._extractXpaths(e, xpaths)
        return xpaths
    #___________________________________________________________________________

    def _extractXpaths(self, e, xpaths):
        """Recursively find the xpaths"""
        text = self.getElementText(e)
        xpath = HtmlXpath(self._tree.getpath(e)).normalize()
        if text:
            xpaths[text].append(xpath)

        # extract text for each group of tags
        childTags = defaultdict(int)
        for child in e:
            if type(child.tag) == str:
                self._extractXpaths(child, xpaths)
                childTags[child.tag] += 1
        for childTag, count in childTags.items():
            if count >= 2:
                # add text content for this tag
                childXpath = HtmlXpath('%s/%s' % (xpath, childTag), HtmlXpath.COLLAPSE_MODE)
                childText = ' '.join(self.getElementsText(e.xpath(childXpath.get())))
                if childText:
                    xpaths[childText].append(childXpath)
    #___________________________________________________________________________

    def getElementText(self, e):
        """Extract text under this HtmlElement"""
        return normalizeStr(e.text_content().strip())
    #___________________________________________________________________________

    def getElementsText(self, es):
        return [text for text in [self.getElementText(e) for e in es]]
    #___________________________________________________________________________

    def getElementHTML(self, e):
        """Extract HTML under this element"""
        return  (e.text if e.text else '') + \
                ''.join([lxmlHtml.tostring(c) for c in e.getchildren()]) + \
                (e.tail if e.tail else '')
    #___________________________________________________________________________

    def getElementsHTML(self, es):
        return [html for html in [self.getElementHTML(e) for e in es]]
    #___________________________________________________________________________

    def matchXpaths(self, output):
        """Return the amount of overlap at xpath with the desired output""" 
        if output in self._xpaths:
            # exact match so can return xpaths directly with a perfect match
            return [(xpath, self.similarity(output, output)) for xpath in self._xpaths[output]]
        else:
            # no exact match so return similarities of xpaths
            result = []
            for (text, xpaths) in self._xpaths.items():
                score = self.similarity(output, text)
                result.extend((xpath, score) for xpath in xpaths)
            return result
    #___________________________________________________________________________

    def similarity(self, s1, s2):
        """
        >>> s = 'hello world'
        >>> matches = {'I say now, hello world!': 1, 'ello orld': 2, 'hello': 3, 'hello world': 4, '': 5}
        >>> sorted([(HtmlDoc('<html></html>', [], True).similarity(s, k), v) for (k, v) in matches.items()])
        [(-11, 4), (-7, 2), (1, 1), (1, 3), (11, 5)]
        """
        margin = 5
        power = 1
        if len(s1)/margin < len(s2) < len(s1)*margin: 
            s = self._sequence
            if s.a != s1:
                s.set_seq1(s1)
            if s.b != s2:
                s.set_seq2(s2)
            score = 0
            for tag, i1, i2, j1, j2 in s.get_opcodes():
                thisScore = max(i2 - i1, j2 - j1)**power
                if tag == 'equal':
                    score -= thisScore
                else:
                    score += thisScore
        else:
            # don't bother calculating if string lengths are too far off, just give maximum difference
            score = abs(len(s1) - len(s2))**power
        return score
    #___________________________________________________________________________
