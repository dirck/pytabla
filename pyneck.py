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
gray = (.5,.5,.5)
lightGray = (.75,.75,.75)
darkGray = (.25,.25,.25)

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
        self.frets = frets
        self.title = title
        self.dots = []
        self.circles = []
        self.marks = []
        #self.annots = []
        self.colorDots = {}
        self.fx = X
        self.fy = Y

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
        self.visit(self.double1)

    def roll1(self, dots, down):
        r = []
        for dot in dots:
            r.append((dot[0], ( (dot[1]-down) % 24)))
        return r

    def chop1(self, dots):
        r = []
        for dot in dots:
            if dot[1] <= self.frets:
                r.append(dot)
        return r

    def chop(self):
        self.visit(self.chop1)

    def visit(self, f, *p):
        self.dots = f(self.dots, *p)
        self.circles = f(self.circles, *p)
        colors = self.colorDots.keys()
        for color in colors:
            self.colorDots[color] = f(self.colorDots[color], *p)

    def roll(self, up):
        self.double()
        self.visit(self.roll1, up)
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
        self.dots.append( (string, fret) )
    def circle(self, string, fret):
        self.circles.append( (string, fret) )
    def mark(self, string, fret, s):
        self.marks.append( (string, fret, s) )

    def draw_dot(self, string, fret):
        c = self.canvas
        x = self.fx + (6-string) * cellWidth
        y = self.fy - (fret) * cellHeight + cellHeight/2
        dr = dotRadius
        if fret < 1:
            y -= dr
            dr = dr/2
        c.circle(x, y, dr, 0, 1)

    def draw_circle(self, string, fret):
        c = self.canvas
        x = self.fx + (6-string) * cellWidth
        y = self.fy - (fret) * cellHeight + cellHeight/2
        dr = dotRadius
        if fret < 1:
            y -= dr
            dr = dr/2
        c.circle(x, y, dr, 1, 1)

    def draw_mark(self, string, fret, mark):
        c = self.canvas
        x = self.fx + (6-string) * cellWidth
        if fret == 0:
            y = self.fy + fontSize * .2
        else:
            y = self.fy - (fret) * cellHeight + cellHeight / 2 - fontSize / 3
            c.setFillColorRGB(1,1,1)
            if string > 0 and string < 7 and mark[0] != '(':    #OPT
                self.draw_circle(string, fret)
            c.setFillColorRGB(0,0,0)
        c.drawCentredString(x, y, mark)

    def draw_color(self, string, fret, color):
        self.canvas.setFillColorRGB(*color)
        self.draw_circle(string, fret)

    def draw(self, c, fx, fy):
        self.canvas = c
        self.fx = fx;
        self.fy = fy
        self.frame()
        c.setFillColorRGB(*black)
        if self.title:
            c.drawCentredString(fx+cellWidth*2.5, fy+fontSize, self.title)
        for string,fret in self.dots:
            self.draw_dot(string, fret)
        c.setFillColorRGB(*white)
        for string,fret in self.circles:
            self.draw_circle(string, fret)
        c.setFillColorRGB(*black)
        for string, fret, mark in self.marks:
            self.draw_mark(string, fret, mark)
        colors = self.colorDots.keys()
        for color in colors:
            marks = self.colorDots[color]
            for string,fret in marks:
                self.draw_color(string, fret, color)

    def color_note(self, note, color):
        offset = self.noteMap[note]
        # what's the idiom for this?
        dots = self.colorDots.get(color, [])
        self.colorDots[color] = dots
        for string in range(1,7):
            openNote = self.standardTuning[string]
            # brute force
            for fret in range(0, self.frets+1):
                if (openNote+fret)%12 == offset:
                    dots.append((string,fret))

    def mark_note(self, note, mark):
        offset = self.noteMap[note]
        dots = self.marks
        for string in range(1,7):
            openNote = self.standardTuning[string]
            # brute force
            for fret in range(0, self.frets+1):
                if (openNote+fret)%12 == offset:
                    dots.append((string,fret,mark))

if __name__ == '__main__':
    main(sys.argv[1:])

