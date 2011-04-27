"""
    pyneck.py  input.txt   output.pdf
"""

"""
    X Y movement in input is weird because X Y is happening on output

    the Chart could draw during input instead...

    let's go with:  either the charts are all placed or none are.
"""

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


# change naming conventions for globals?

pageSize=(8.5*inch,11*inch)
margins = Bunch(left=1, right=1, top=1, bottom=1)

# init function for cases where any of these globals are changed

startX = margins.left * inch
startY = pageSize[1] - margins.top * inch
X = startX
Y = startY
nRows = 5
nCols = 5

chartWidth = (pageSize[0] - (margins.left+margins.right)*inch) / nCols
chartHeight = (pageSize[1] - (margins.top+margins.bottom)*inch) / nRows

lineWidth = inch/144    # fine lines
cellWidth = chartWidth / 8.
cellHeight = cellWidth * 1.4

dotRadius = cellWidth / 3.
fontName="Times-Roman"
fontSize=9

Charts = []

def main(argv):
    global X,Y
    if len(argv) != 2:
        print __doc__
        sys.exit(2);
    c = Canvas(argv[1], pagesize=pageSize, pageCompression=0)
    c.setFont(fontName, fontSize)

    X = 0
    Y = 0
    execfile(argv[0])
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

    #chart = Chart(title="D Major");
    #chart.marks += [ (6,0,'x'), (5,0,'x'), (4,0,'o'), (3,2,'1'), (2,3,'3'), (1, 2, '2')]
    #chart.draw(c, startX, startY)
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
    def __init__(self, title="", frets=4):
        global X, Y
        Charts.append(self)
        self.frets = frets
        self.title = title
        self.dots = []
        self.circles = []
        self.marks = []
        self.fx = X
        self.fy = Y

    def frame(self):
        c = self.canvas
        x = self.fx
        y = self.fy
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
        c.circle(x, y, dotRadius, 0, 1)

    def draw_circle(self, string, fret):
        c = self.canvas
        x = self.fx + (6-string) * cellWidth
        y = self.fy - (fret) * cellHeight + cellHeight/2
        c.circle(x, y, dotRadius, 1, 1)

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

    def draw(self, c, fx, fy):
        self.canvas = c
        self.fx = fx;
        self.fy = fy
        self.frame()
        if self.title:
            c.drawCentredString(fx+cellWidth*2.5, fy+fontSize, self.title)
        c.setFillColorRGB(0,0,0)
        for string,fret in self.dots:
            self.draw_dot(string, fret)
        c.setFillColorRGB(1,1,1)
        for string,fret in self.circles:
            self.draw_circle(string, fret)
        c.setFillColorRGB(0,0,0)
        for string, fret, mark in self.marks:
            self.draw_mark(string, fret, mark)

if __name__ == '__main__':
    main(sys.argv[1:])

