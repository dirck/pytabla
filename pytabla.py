"""
    pytabla.py - python pdf guitar tablature

At the moment the input format is a Python list,
this probably will change to a more friendly format.

"""
#doing some parsing
import string

# Using reportlabs

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch

# using non-homogenous lists
from types import *

# page metrics, layout info
# negative y issues

pageSize=(8.5*inch,11*inch)

startX, startY = inch, pageSize[1] - inch

lineSpacing = inch/12   #inter-line spacing
nLines = 6              # most naturally
lineWidth = inch/144    # fine lines

tabSpacing = inch/2      #inter-tab spacing
tabWidth = (pageSize[0] - startX*2)
nTabs = (pageSize[1] - inch*2) / ((nLines-1)*lineSpacing+tabSpacing)
cellsPerTab = 24
cellWidth = tabWidth / cellsPerTab

fontName="Times-Roman"
fontSize=9

# we'll need input and output files

def run(data, outfile):   
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
    
def notesOld(c, data):
    c.setFont(fontName, fontSize)
    n = len(data)
    max = nTabs * cellsPerTab
    left = []
    if n > max:
        n = max
        left = data[:n]
    
    x,y = startX, startY
    x += cellWidth/2
    
    for d in data:
        if type(d) is TupleType:
            if not d:
                pass    # empty spot
            elif type(d[0]) is TupleType:
                for n in d: #chord
                    if type(n) is TupleType:
                        lastString = fret(c, x,y, n)
                    else:
                        note(c, x,y, n)
            else:
                lastString = fret(c, x,y, d)
                
        elif type(d) is IntType:
            fret(c, x,y, (lastString,d))
        
        x,y = nexy(x, y)
        
def notes(c, data):
    c.setFont(fontName, fontSize)
    maxCell = nTabs * cellsPerTab
    
    x,y = startX, startY
    x += cellWidth/2
    
    cell = 0
    item = 0
    for d in data:
        item = item + 1
        if not d:
            continue
        if type(d) is StringType:
            c = d[0]
            d = d[1:]
            if c == '^':
                if len(d)==0:
                    pass    # skip cell
                elif len(d)==1:
                    x = startX+tabWidth # skip eol
                else:
                    break   # end of page
            else:
                if c == '+':
                    note(c, x,y, d, above=1)
                elif c == '-':
                    note(c, x,y, d, above=0)
                continue    # Don't skip cell
                
        elif type(d) is TupleType:
            if type(d[0]) is TupleType:
                for n in d: #chord
                    if type(n) is TupleType:
                        lastString = fret(c, x,y, n)
                    else:
                        note(c, x,y, n)
            else:
                lastString = fret(c, x,y, d)
                
        elif type(d) is IntType:
            fret(c, x,y, (lastString,d))
        
        x,y = nexy(x, y)
        cell = cell + 1
        if cell > maxCell:
            break
    return data[item:]
        
def fret(c, x,y, t):
    s,f = t[0],t[1]
    y = y - (s-1)*lineSpacing - lineSpacing/2
    f = str(f)
    c.drawCentredString(x, y, f)
    return s
    
def note(c, x,y, s, above=0):
    if above:
        y = y + lineSpacing
    else:
        y = y - 8*lineSpacing
    c.drawString(x, y, s)

def nexy(x,y):
    x = x+cellWidth
    if x > startX + tabWidth:
        x = startX + cellWidth/2
        y = y - (6*lineSpacing) - tabSpacing
    return x,y

# some test data
REST=()
S1=[(1,12,'(4)'),11,
    12,11,12,
    7,10,8,
    ((6,5),(1,5), 'Am'),(5,7),(4,7),
    (3,5),(2,5),(1,5),
    ((6,0),(1,7),'E'),(5,7),(4,6),
    (1,0)]

S2=[(1,4),(1,7),
    ((6,5),(1,8),'Am'), (5,7),(4,7),
    (1,0)]

S3=S1+[(1,8),7,
       ((6,5),(1,5),'Am'),(5,7),(4,7),
       (1,7),8,9,
       ((6,8),(1,12),'C'),(5,10),(4,10),
       (3,12),(1,13),12,
       ((6,7),(1,10),'G'),(5,10),(4,9),
       (3,10),(1,12),10,
       ((6,5),(1,8), 'Am'),(5,7),(4,7),
       (1,0),10,8,
       ((6,0),(1,7))
       ]

def Parse(data):
    """ converting a different format 
    
        #comment
        meta: key
        macro= value
        macro=[multiline]
        
    """
    lines = string.split(data, '\n')
    song = []
    meta = {}
    macros = {}
    macroName = ''
    macro = []
    
    for line in lines:
        if not line or line[0]=='#':
            continue
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
    
FurElise = [REST]+S1+S2+S3
            
run(FurElise,"t.pdf")

meta,macros,song= Parse(open("furelise.tab").read())
print
for m in meta.keys():
    print m,':',meta[m]
print

for m in macros.keys():
    print m, '=', macros[m]
print
print song

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
        macros[m] = string.strip(value)
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

cookmacros(macros)
song = Cooker(macros,song)()

for k in macros.keys():
    value = macros[k]
    macros[k] = []
    macros[k] = Cooker(macros, value)()

print
for m in macros.keys():
    macros[m] = string.join(macros[m],' ')
    print m, '=', macros[m]
print
print song

