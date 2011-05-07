"""
    pyneck.py  input.txt   output.pdf
"""

"""
    X Y movement in input is weird because X Y is happening on output

    the Chart could draw during input instead...

    let's go with:  either the charts are all placed or none are.
"""

import copy
import string
import sys

# Using reportlabs

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch

# using non-homogenous lists
from types import *

# page metrics, layout info
# negative y issues

class Bunch:
    """ from aspn cookbook """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

Copy = copy.deepcopy  #JIC

# change naming conventions for globals?

pageSize=(8.5*inch,11*inch)
margins = Bunch(left=0.75, right=0.75, top=1, bottom=1)

# init function for cases where any of these globals are changed

nRows = 5
nCols = 5

def init():
    global chartWidth, chartHeight, lineWidth, cellWidth, cellHeight, dotRadius
    global startX, startY, X, Y

    chartWidth = (pageSize[0] - (margins.left+margins.right)*inch) / nCols
    chartHeight = (pageSize[1] - (margins.top+margins.bottom)*inch) / nRows

    lineWidth = inch/144    # fine lines
    cellWidth = chartWidth / 8.
    cellHeight = cellWidth * 1.4
    dotRadius = cellWidth / 3.

    startX = margins.left * inch + (chartWidth - cellWidth*5)/2
    startY = pageSize[1] - margins.top * inch  - (cellHeight)
    X = startX
    Y = startY

fontName="Helvetica"
fontSize=9

white = (1,1,1)
black = (0,0,0)

# calibrate a little better
#gray = (.5,.5,.5)
#lightGray = (.75,.75,.75)
#darkGray = (.25,.25,.25)

gray = (.70,.70,.70)
lightGray = (.85,.85,.85)
darkGray = (.55,.55,.55)

# for printing
red = (1,0,0)
green = (0,1,0)
blue = (0,0,1)

darkRed = (0.5,0,0)
darkGreen = (0.5,1,0)
darkBlue = (0.5,0,1)

cyan = (0,1,1)
yellow = (1,0,1)
magenta = (0,0,1)

Charts = []
Title = ""

def main(argv):
    global X,Y,Title
    if len(argv) != 2:
        print __doc__
        sys.exit(2);
    c = Canvas(argv[1], pagesize=pageSize, pageCompression=0)
    c.setFont(fontName, fontSize)

    init()
    X = 0
    Y = 0
    execfile(argv[0], globals())
    init()
    if Title:
        print "title", Title
        c.drawCentredString(pageSize[0]/2, pageSize[1]-(margins.top*inch*.65), Title)
    X = startX
    Y = startY
    for chart in Charts:
        x = chart.fx
        y = chart.fy
        if not x and not y:
            x = X
            y = Y
        chart.draw(c, x, y)
        over()

    c.showPage()
    c.save()

# move the "cursor"
# back, down, right, bottom

def over():
    global X
    X = X + chartWidth
    if (pageSize[0] - X) < chartWidth:
        next()

def down():
    global X,Y
    #X = startX
    Y = Y - chartHeight

def next():
    down()
    left()

def left():
    global X
    X = startX

def top():
    global Y
    Y = startY

class Chart:
    """ marks and annotations:
        (string, fret, color, text)
    """
    # as offsets from C
    noteMap = {'C':0,
               'C#':1,'Db':1,
               'D':2,
               'D#':3, 'Eb':3,
               'E':4,
               'F':5,
               'F#':6,'Gb':6,
               'G':7,
               'G#':8,'Ab':8,
               'A':9,
               'A#':10, 'Bb':10,
               'B':11}

    standardTuning = {6:4,5:9,4:2,3:7,2:11,1:4}

    def __init__(self, title="", frets=4):
        global X, Y
        Charts.append(self)
        self.frets = frets  # nFrets
        self.title = title
        # split because notes move and annots don't
        self.notes = []
        self.annots = []
        self.fx = X
        self.fy = Y
        self.tuning = Chart.standardTuning

    def alternate_tuning(self, strings):
        v = strings.split(' ')
        v = map(lambda x: x.strip(), v)
        v = filter(None, v)
        if len(v) != 6:
            raise ValueError
        v = [self.noteMap[s] for s in v]
        t = {}
        for i in range(6):
            t[6-i] = v[i]
        self.tuning = t

    def copy(self):
        n = Copy(self)
        n.fx = X
        n.fy = Y
        Charts.append(n)
        return n

    def double1(self, dots):
        r = []
        for dot in dots:
            r.append((dot[0], (dot[1]+12)))
        return dots+r

    def double(self):
        r = []
        for note in self.notes:
            r.append((note[0], (note[1]+12), note[2], note[3]))
        self.notes += r

    def roll1(self, down):
        r = []
        for note in self.notes:
            r.append((note[0], (note[1]-down)%24, note[2], note[3]))
        self.notes = r

    def chop(self):
        self.notes = filter(lambda note: note[1] <= self.frets, self.notes)

    def roll_down(self, down):
        self.double()
        self.roll1(down)
        self.chop()

    def frame(self):
        c = self.canvas
        x = self.fx
        y = self.fy
        c.setStrokeColorRGB(*black)
        c.setLineWidth(lineWidth)
        for fret in range(self.frets+1):
            c.line(x, y-fret*cellHeight, x+cellWidth*5, y-fret*cellHeight)
        for string in range(6):
            c.line(x+string*cellWidth, y, x+string*cellWidth, y-cellHeight*self.frets)

    def dot(self, string, fret):
        self.notes.append( (string, fret, black, None) )
    def dots(self, a):
        for string, fret in a:
            self.dot(string, fret)

    def circle(self, string, fret):
        self.notes.append( (string, fret, white, None) )
    def circles(self, a):
        for string, fret in a:
            self.circle(string, fret)

    def mark(self, string, fret, s):
        self.annots.append( (string, fret, black, s) )
    def marks(self, a):
        for string, fret, text in a:
            self.mark(string, fret, text)

    def color_dot(self, color, string, fret):
        self.notes.append( (string, fret, color, None) )
    def color_dots(self, color, a):
        for string, fret in a:
            self.color_dot(color, string, fret)

    def draw_note(self, string, fret, color, mark):
        c = self.canvas
        cx = self.fx + (6-string) * cellWidth
        cy = self.fy - (fret) * cellHeight + cellHeight/2
        ty = self.fy - (fret) * cellHeight + cellHeight / 2 - fontSize / 3
        dr = dotRadius
        if fret < 1:
            ty = self.fy + fontSize * .2
            cy -= dr
            dr = dr/2
        if not mark:
            c.setFillColorRGB(*color)
            c.circle(cx, cy, dr, 1, 1)
            return
        if fret > 0 and string < 7 and mark[0] != '(':
            c.setFillColorRGB(*white)
            c.circle(cx, cy, dr, 1, 1)
        c.setFillColorRGB(*color)
        c.drawCentredString(cx, ty, mark)

    def draw(self, c, fx, fy):
        self.canvas = c
        self.fx = fx;
        self.fy = fy
        self.frame()
        c.setFillColorRGB(*black)
        if self.title:
            c.drawCentredString(fx+cellWidth*2.5, fy+fontSize, self.title)
        for string,fret,color,mark in self.notes:
            self.draw_note(string, fret, color, mark)
        for string,fret,color,mark in self.annots:
            self.draw_note(string, fret, color, mark)

    def color_note(self, color, note):
        offset = self.noteMap[note]
        for string in range(1,7):
            openNote = self.tuning[string]
            # brute force
            for fret in range(0, self.frets+1):
                if (openNote+fret)%12 == offset:
                    self.color_dot(color, string, fret)

    def color_notes(self, color, notes):
        for note in notes:
            self.color_note(color, note)

    def mark_note(self, mark, note):
        offset = self.noteMap[note]
        for string in range(1,7):
            openNote = self.tuning[string]
            # brute force
            for fret in range(0, self.frets+1):
                if (openNote+fret)%12 == offset:
                    self.mark(string, fret, mark)

    def mark_notes(self, mark, notes):
        for note in notes:
            self.mark_note(mark, note)

    def chop_marks(self):
        self.annots = filter(lambda note: note[1] <= self.frets, self.annots)

    def fret_numbers(self):
        self.marks([ (7,3,'3'),
                     (7,5,'5'),
                     (7,7,'7'),
                     (7,9,'9'),
                     (7,12,'12'),
                     (7,15,'15') ])
        self.chop_marks();

    def fret_marks(self):
        self.marks([ (7,3,'*'),
                     (7,5,'*'),
                     (7,7,'*'),
                     (7,9,'*'),
                     (7,12,'::'),
                     (7,15,'*') ])
        self.chop_marks();


if __name__ == '__main__':
    main(sys.argv[1:])

