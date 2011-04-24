"""
    pytabla.py - python pdf guitar tablature

usage:
    pytabla input.tab output.pdf
"""
"""
At the moment the input format is a Python list,
this probably will change to a more friendly format.

the new format is better but not bulletproof.
it's possible to feed it data that will cause an exception.
"""
#doing some parsing
import string
import sys

# Using reportlabs

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch

# using non-homogenous lists
from types import *

# page metrics, layout info
# negative y issues

pageSize=(8.5*inch,11*inch)

startX, startY = inch, pageSize[1] - inch

lineSpacing = inch/10   #inter-line spacing
nLines = 6              # most naturally
fatLineWidth = 1.5
lineWidth = inch/144    # fine lines

tabSpacing = inch/3*2      #inter-tab spacing
tabWidth = (pageSize[0] - startX*2)
nTabs = int((pageSize[1] - inch*2) / ((nLines-1)*lineSpacing+tabSpacing))
cellsPerTab = 24
cellWidth = tabWidth / cellsPerTab

fontName="Times-Roman"
fontSize=9

# we'll need input and output files

def run(infile, outfile):
    data = compile(infile)
    c = Canvas(outfile,pagesize=pageSize,pageCompression=0)
    lines(c)
    left = notes(c, data)
    c.showPage()
    c.save()

def lines(c):
    c.setLineWidth(lineWidth)
    x1,y1 = startX, startY
    x2,y2 = startX+tabWidth,y1
    for tab in range(nTabs):
        for line in range(nLines):
            c.line(x1,y1, x2,y2)
            y1 = y1 - lineSpacing
            y2 = y1
        y1 = y1 - tabSpacing
        y2 = y1

def notes(canvas, data):
    canvas.setFont(fontName, fontSize)
    maxCell = nTabs * cellsPerTab

    x,y = startX, startY
    x += cellWidth/2
    lx,ly = x,y
    cell = 0
    item = 0
    for d in data:
        item = item + 1
        if type(d) is StringType:
            if not d:
                continue
            c = d[0]
            d = d[1:]
            if c == '^':    # break directive
                if len(d)==0:
                    pass    # skip cell
                elif len(d)==1:
                    x = startX+tabWidth # skip eol
                else:
                    break   # end of page
            else:
                if c == '{':  # repeat mark
                    repeat(canvas, x,y)
                elif c == '}':  # end repeat mark
                    endrepeat(canvas, lx,ly)
                elif c == '+':
                    note(canvas, x,y, d, above=1)
                elif c == '-':
                    note(canvas, x,y, d, above=0)
                continue    # Don't skip cell

        elif type(d) is TupleType:
            if type(d[0]) is TupleType:
                for n in d: #chord
                    if type(n) is TupleType:
                        lastString = fret(canvas, x,y, n)
                    else:   # implied 'next string'
                        lastString = fret(canvas, x,y, (lastString-1,n))
            else:
                lastString = fret(canvas, x,y, d)

        elif type(d) is IntType:
            fret(canvas, x,y, (lastString,d))

        # next cell
        lx,ly = x,y
        x,y = nexy(x, y)
        cell = cell + 1
        if cell > maxCell:
            break

    # next page
    return data[item:]

def fret(c, x,y, t):
    s,f = t[0],t[1]
    y = y - (s-1)*lineSpacing - lineSpacing/3
    f = str(f)
    c.drawCentredString(x, y, f)
    return s

def note(c, x,y, s, above=0):
    s = string.replace(s, '\t', ' ')    # quoted
    if above:
        y = y + lineSpacing *1.5
        c.drawCentredString(x, y, s)
    else:
        y = y - 7.5*lineSpacing
        c.drawString(x, y, s)

def repeat(c, x,y):
    x -= cellWidth/2
    c.setLineWidth(fatLineWidth)
    c.line(x,y, x,y-5*lineSpacing)
    c.setLineWidth(lineWidth)
    x = x + fatLineWidth*2
    c.line(x,y, x,y-5*lineSpacing)

def endrepeat(c, x,y):
    x += cellWidth/2
    c.setLineWidth(fatLineWidth)
    c.line(x,y, x,y-5*lineSpacing)
    c.setLineWidth(lineWidth)
    x = x - fatLineWidth*2
    c.line(x,y, x,y-5*lineSpacing)

def nexy(x,y):
    x = x+cellWidth
    if x > startX + tabWidth:
        x = startX + cellWidth/2
        y = y - (6*lineSpacing) - tabSpacing
    return x,y

def Parse(data):
    """ converting a different format

        #comment
        meta: key
        macro= value
        macro=[multiline]

        i'd like to handle quotes
    """
    data = string.replace(data, '\t', ' ') #no tabs
    lines = string.split(data, '\n')
    song = []
    meta = {}
    macros = {}
    macroName = ''
    macro = []

    for line in lines:
        comment = string.find(line, '#')
        if comment >= 0:
            line = line[:comment]
        if not line:
            continue
        q = string.find(line,'"')
        if q >= 0:  # handling quotes
            qe = string.find(line, '"', q+1)
            if qe > 0:
                #hack to replace spaces with something else
                s = string.replace(line[q+1:qe],' ','\t')
                line = line[:q] + s + line[qe+1:]
        if string.find(line,'=') > 0:
            name, value = string.split(line, '=', 1)
            macroName = string.strip(name)
            line = string.strip(value)
            start = string.find(line, '[')
            macro = []
            macros[macroName] = macro
            if start < 0:
                if line:
                    macro.append(line)
                macroName = ''
                continue
            line = string.replace(line, '[', '')    # just in case
        if macroName:
            end = string.find(line, ']')
            if end >= 0:
                line = line[:end]
                macroName = ''
            if line:
                macro.append(line)
        elif string.find(line,':') > 0:
            name, value = string.split(line, ':', 1)
            name = string.strip(name)
            value = string.strip(value)
            meta[name] = value
        else:
            song.append(line)
    return meta, macros, song

def compile(infile):
    data = open(infile).read()
    meta, macros, song = Parse(data)
    global cellsPerTab, cellWidth
    cellsPerTab = int(meta.get("Cells", cellsPerTab))
    cellWidth = tabWidth / cellsPerTab

    global nTabs, tabSpacing
    nTabs  = int(meta.get("Rows", nTabs))
    tabSpacing = ((pageSize[1] - inch*2) / nTabs) - (nLines-1)*lineSpacing
    cookmacros(macros)
    song = Cooker(macros,song)()
    return items2data(song)

"""
How to cook the macros
each macro is an arbitrary list of strings,

join them together and then split on white space
pass through the items and replace any matching a macro
with the contents of the macro
if no replacements occurred, done cooking that macro.
"""

def cookmacros(macros):
    keys = macros.keys()
    for k in keys:
        value = macros[k]
        value = string.join(value, ' ')
        value = string.strip(value)
        macros[k] = string.split(value, ' ')

class Cooker:
    def __init__(self, macros, stuff):
        self.macros = macros
        self.n = 0
        if not type(stuff) is ListType:
            stuff = [stuff]
        while 1:
            stuff = string.join(stuff)
            stuff = string.split(stuff, ' ')    # words
            stuff = filter(None, stuff) # lose emptys
            self.n = 0
            stuff = map(self.cook, stuff)
            if not self.n:
                break
        self.value = stuff

    def __call__(self):
        return self.value

    def cook(self, item):
        g = self.macros.get(item)
        if g:
            self.n = self.n + 1
            if type(g) is ListType:
                return string.join(g, ' ')
            return g
        return item

def pair(s):
    s,f = string.split(s,'.',1)
    return (int(s),int(f))

def onenote(s):
    if string.find(s, '.') > 0:
        return pair(s)
    return int(s)

def items2data(song):
    data = []
    inquote = []
    for s in song:
        c = s[0]
        if c in '+-^{}':
            data.append(s)
        else:
            if string.find(s, '&') > 0:
                notes = string.split(s, '&')
                s = tuple(map(onenote,notes))
            else:
                s = onenote(s)
            data.append(s)
    return data

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print __doc__
    else:
        run(sys.argv[1], sys.argv[2])

