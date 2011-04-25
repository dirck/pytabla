"""
    pyneck.py  input.txt   output.pdf
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


pageSize=(8.5*inch,11*inch)
margins = Bunch(left=1, right=1, top=1, bottom=1)

startX, startY = margins.left * inch, pageSize[1] - margins.top * inch
nRows = 5
nCols = 5
lineWidth = inch/144    # fine lines
cellWidth = inch / 5.
cellHeight = inch / 4.
dotRadius = cellWidth / 3.
fontName="Times-Roman"
fontSize=9

def main(argv):
    if len(argv) != 2:
        print __doc__
        sys.exit(2);
    c = Canvas(argv[1], pagesize=pageSize, pageCompression=0)
    c.setFont(fontName, fontSize)
    chart = Chart(title="D Major");
    chart.marks += [ (6,0,'x'), (5,0,'x'), (4,0,'o'), (3,2,'1'), (2,3,'3'), (1, 2, '2')]
    chart.draw(c, startX, startY)
    c.showPage()
    c.save()

class Chart:
    def __init__(self, frets=4, title=""):
        self.frets = frets
        self.title = title
        self.dots = []
        self.circles = []
        self.marks = []

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
        if fret != 0:
            self.circles.append( (string, fret) )

    def draw(self, c, fx, fy):
        self.canvas = c
        self.fx = fx;
        self.fy = fy
        self.frame()
        if self.title:
            c.drawCentredString(fx+cellWidth*2.5, fy+fontSize, self.title)
        c.setFillColorRGB(0,0,0)
        for string,fret in self.dots:
            x = fx + (6-string) * cellWidth
            y = fy - (fret) * cellHeight + cellHeight/2
            c.circle(x, y, dotRadius, 0, 1)
        c.setFillColorRGB(1,1,1)
        for string,fret in self.circles:
            x = fx + (6-string) * cellWidth
            y = fy - (fret) * cellHeight + cellHeight/2
            c.circle(x, y, dotRadius, 1, 1)
        c.setFillColorRGB(0,0,0)
        for string, fret, s in self.marks:
            x = fx + (6-string) * cellWidth
            y = fy - (fret) * cellHeight + fontSize * .65
            c.drawCentredString(x, y, s)


if __name__ == '__main__':
    main(sys.argv[1:])

