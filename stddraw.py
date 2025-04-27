
import time
import os
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import pygame.gfxdraw
import pygame.font

import tkinter as Tkinter
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog

try:
    from lib.color import WHITE
    from lib.color import BLACK
    from lib.color import RED
    from lib.color import GREEN
    from lib.color import BLUE
    from lib.color import CYAN
    from lib.color import MAGENTA
    from lib.color import YELLOW
    from lib.color import DARK_RED
    from lib.color import DARK_GREEN
    from lib.color import DARK_BLUE
    from lib.color import GRAY
    from lib.color import DARK_GRAY
    from lib.color import LIGHT_GRAY
    from lib.color import ORANGE
    from lib.color import VIOLET
    from lib.color import PINK
    from lib.color import BOOK_BLUE
    from lib.color import BOOK_LIGHT_BLUE
    from lib.color import BOOK_RED
except ModuleNotFoundError:
    from color import WHITE
    from color import BLACK
    from color import RED
    from color import GREEN
    from color import BLUE
    from color import CYAN
    from color import MAGENTA
    from color import YELLOW
    from color import DARK_RED
    from color import DARK_GREEN
    from color import DARK_BLUE
    from color import GRAY
    from color import DARK_GRAY
    from color import LIGHT_GRAY
    from color import ORANGE
    from color import VIOLET
    from color import PINK
    from color import BOOK_BLUE
    from color import BOOK_LIGHT_BLUE
    from color import BOOK_RED

_BORDER = 0.0
#_BORDER = 0.05
_DEFAULT_XMIN = 0.0
_DEFAULT_XMAX = 1.0
_DEFAULT_YMIN = 0.0
_DEFAULT_YMAX = 1.0
_DEFAULT_CANVAS_SIZE = 512
_DEFAULT_PEN_RADIUS = .005  # Maybe change this to 0.0 in the future.
_DEFAULT_PEN_COLOR = BLACK

_DEFAULT_FONT_FAMILY = 'Helvetica'
_DEFAULT_FONT_SIZE = 12

_xmin = None
_ymin = None
_xmax = None
_ymax = None

_fontFamily = _DEFAULT_FONT_FAMILY
_fontSize = _DEFAULT_FONT_SIZE

_canvasWidth = float(_DEFAULT_CANVAS_SIZE)
_canvasHeight = float(_DEFAULT_CANVAS_SIZE)
_penRadius = None
_penColor = _DEFAULT_PEN_COLOR
_keysTyped = []

# Has the window been created?
_windowCreated = False

_mousePressed = False

_mousePos = None

def _pygameColor(c):

    r = c.getRed()
    g = c.getGreen()
    b = c.getBlue()
    return pygame.Color(r, g, b)

def _scaleX(x):
    return _canvasWidth * (x - _xmin) / (_xmax - _xmin)

def _scaleY(y):
    return _canvasHeight * (_ymax - y) / (_ymax - _ymin)

def _factorX(w):
    return w * _canvasWidth / abs(_xmax - _xmin)

def _factorY(h):
    return h * _canvasHeight / abs(_ymax - _ymin)

def _userX(x):
    return _xmin + x * (_xmax - _xmin) / _canvasWidth

def _userY(y):
    return _ymax - y * (_ymax - _ymin) / _canvasHeight


def setCanvasSize(w=_DEFAULT_CANVAS_SIZE, h=_DEFAULT_CANVAS_SIZE):

    global _background
    global _surface
    global _canvasWidth
    global _canvasHeight
    global _windowCreated

    if _windowCreated:
        raise Exception('The stddraw window already was created')

    if (w < 1) or (h < 1):
        raise Exception('width and height must be positive')

    _canvasWidth = w
    _canvasHeight = h
    _background = pygame.display.set_mode([w, h])
    pygame.display.set_caption('stddraw window (r-click to save)')
    _surface = pygame.Surface((w, h))
    _surface.fill(_pygameColor(WHITE))
    _windowCreated = True

def setXscale(min=_DEFAULT_XMIN, max=_DEFAULT_XMAX):

    global _xmin
    global _xmax
    min = float(min)
    max = float(max)
    if min >= max:
        raise Exception('min must be less than max')
    size = max - min
    _xmin = min - _BORDER * size
    _xmax = max + _BORDER * size

def setYscale(min=_DEFAULT_YMIN, max=_DEFAULT_YMAX):

    global _ymin
    global _ymax
    min = float(min)
    max = float(max)
    if min >= max:
        raise Exception('min must be less than max')
    size = max - min
    _ymin = min - _BORDER * size
    _ymax = max + _BORDER * size

def setPenRadius(r=_DEFAULT_PEN_RADIUS):

    global _penRadius
    r = float(r)
    if r < 0.0:
        raise Exception('Argument to setPenRadius() must be non-neg')
    _penRadius = r * float(_DEFAULT_CANVAS_SIZE)

def setPenColor(c=_DEFAULT_PEN_COLOR):

    global _penColor
    _penColor = c

def setFontFamily(f=_DEFAULT_FONT_FAMILY):

    global _fontFamily
    _fontFamily = f

def setFontSize(s=_DEFAULT_FONT_SIZE):

    global _fontSize
    _fontSize = s



def _makeSureWindowCreated():
    global _windowCreated
    if not _windowCreated:
        setCanvasSize()
        _windowCreated = True



def _pixel(x, y):

    _makeSureWindowCreated()
    xs = _scaleX(x)
    xy = _scaleY(y)
    pygame.gfxdraw.pixel(
        _surface,
        int(round(xs)),
        int(round(xy)),
        _pygameColor(_penColor))

def point(x, y):

    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    # If the radius is too small, then simply draw a pixel.
    if _penRadius <= 1.0:
        _pixel(x, y)
    else:
        xs = _scaleX(x)
        ys = _scaleY(y)
        pygame.draw.ellipse(
            _surface,
            _pygameColor(_penColor),
            pygame.Rect(
                xs-_penRadius,
                ys-_penRadius,
                _penRadius*2.0,
                _penRadius*2.0),
            0)

def line(x0, y0, x1, y1):
    
    _makeSureWindowCreated()

    x0 = float(x0)
    y0 = float(y0)
    x1 = float(x1)
    y1 = float(y1)

    lineWidth = _penRadius
    if lineWidth == 0.0: lineWidth = 1.0
    x0s = _scaleX(x0)
    y0s = _scaleY(y0)
    x1s = _scaleX(x1)
    y1s = _scaleY(y1)
    pygame.draw.line(
       _surface,
       _pygameColor(_penColor),
       (x0s, y0s),
       (x1s, y1s),
       int(round(lineWidth)))

def circle(x, y, r):

    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    r = float(r)
    ws = _factorX(2.0*r)
    hs = _factorY(2.0*r)
    # If the radius is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scaleX(x)
        ys = _scaleY(y)
        pygame.draw.ellipse(
            _surface,
            _pygameColor(_penColor),
            pygame.Rect(xs-ws/2.0, ys-hs/2.0, ws, hs),
            int(round(_penRadius)))

def filledCircle(x, y, r):
    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    r = float(r)
    ws = _factorX(2.0*r)
    hs = _factorY(2.0*r)
    # If the radius is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scaleX(x)
        ys = _scaleY(y)
        pygame.draw.ellipse(
            _surface,
            _pygameColor(_penColor),
            pygame.Rect(xs-ws/2.0, ys-hs/2.0, ws, hs),
            0)

def rectangle(x, y, w, h):
    global _surface
    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    w = float(w)
    h = float(h)
    ws = _factorX(w)
    hs = _factorY(h)
    # If the rectangle is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scaleX(x)
        ys = _scaleY(y)
        pygame.draw.rect(
            _surface,
            _pygameColor(_penColor),
            pygame.Rect(xs, ys-hs, ws, hs),
            int(round(_penRadius)))

def filledRectangle(x, y, w, h):
    global _surface
    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    w = float(w)
    h = float(h)
    ws = _factorX(w)
    hs = _factorY(h)
    # If the rectangle is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scaleX(x)
        ys = _scaleY(y)
        pygame.draw.rect(
            _surface,
            _pygameColor(_penColor),
            pygame.Rect(xs, ys-hs, ws, hs),
            0)

def square(x, y, r):
    _makeSureWindowCreated()
    rectangle(x-r, y-r, 2.0*r, 2.0*r)

def filledSquare(x, y, r):
    _makeSureWindowCreated()
    filledRectangle(x-r, y-r, 2.0*r, 2.0*r)

def polygon(x, y):
    global _surface
    _makeSureWindowCreated()
    # Scale X and Y values.
    xScaled = []
    for xi in x:
        xScaled.append(_scaleX(float(xi)))
    yScaled = []
    for yi in y:
        yScaled.append(_scaleY(float(yi)))
    points = []
    for i in range(len(x)):
        points.append((xScaled[i], yScaled[i]))
    points.append((xScaled[0], yScaled[0]))
    pygame.draw.polygon(
        _surface,
        _pygameColor(_penColor),
        points,
        int(round(_penRadius)))

def filledPolygon(x, y):
    global _surface
    _makeSureWindowCreated()
    # Scale X and Y values.
    xScaled = []
    for xi in x:
        xScaled.append(_scaleX(float(xi)))
    yScaled = []
    for yi in y:
        yScaled.append(_scaleY(float(yi)))
    points = []
    for i in range(len(x)):
        points.append((xScaled[i], yScaled[i]))
    points.append((xScaled[0], yScaled[0]))
    pygame.draw.polygon(_surface, _pygameColor(_penColor), points, 0)

def text(x, y, s):
    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    xs = _scaleX(x)
    ys = _scaleY(y)
    font = pygame.font.SysFont(_fontFamily, _fontSize)
    text = font.render(s, 1, _pygameColor(_penColor))
    textpos = text.get_rect(center=(xs, ys))
    _surface.blit(text, textpos)

def boldText(x, y, s):
    _makeSureWindowCreated()
    x = float(x)
    y = float(y)
    xs = _scaleX(x)
    ys = _scaleY(y)
    font = pygame.font.SysFont(_fontFamily, _fontSize, True)
    text = font.render(s, 1, _pygameColor(_penColor))
    textpos = text.get_rect(center=(xs, ys))
    _surface.blit(text, textpos)

def picture(pic, x=None, y=None):
    global _surface
    _makeSureWindowCreated()
    # By default, draw pic at the middle of the surface.
    if x is None:
        x = (_xmax + _xmin) / 2.0
    if y is None:
        y = (_ymax + _ymin) / 2.0
    x = float(x)
    y = float(y)
    xs = _scaleX(x)
    ys = _scaleY(y)
    ws = pic.width()
    hs = pic.height()
    picSurface = pic._surface # violates encapsulation
    _surface.blit(picSurface, [xs-ws/2.0, ys-hs/2.0, ws, hs])

def clear(c=WHITE):
    _makeSureWindowCreated()
    _surface.fill(_pygameColor(c))

def save(f):
    _makeSureWindowCreated()

    pygame.image.save(_surface, f)


def _show():
    _background.blit(_surface, (0, 0))
    pygame.display.flip()
    _checkForEvents()

def _showAndWaitForever():

    _makeSureWindowCreated()
    _show()
    QUANTUM = .1
    while True:
        time.sleep(QUANTUM)
        _checkForEvents()

def show(msec=float('inf')):
    if msec == float('inf'):
        _showAndWaitForever()

    _makeSureWindowCreated()
    _show()
    _checkForEvents()

    QUANTUM = .01
    sec = msec / 1000.0
    if sec < QUANTUM:
        time.sleep(sec)
        return
    secondsWaited = 0.0
    while secondsWaited < sec:
        time.sleep(QUANTUM)
        secondsWaited += QUANTUM
        _checkForEvents()

#-----------------------------------------------------------------------

def _saveToFile():
    import subprocess
    _makeSureWindowCreated()

    stddrawPath = os.path.realpath(__file__)

    childProcess = subprocess.Popen(
        [sys.executable, stddrawPath, 'getFileName'],
        stdout=subprocess.PIPE)
    so, se = childProcess.communicate()
    fileName = so.strip()

    if sys.hexversion >= 0x03000000:
        fileName = fileName.decode('utf-8')

    if fileName == '':
        return

    if not fileName.endswith(('.jpg', '.png')):
        childProcess = subprocess.Popen(
            [sys.executable, stddrawPath, 'reportFileSaveError',
            'File name must end with ".jpg" or ".png".'])
        return

    try:
        save(fileName)
        childProcess = subprocess.Popen(
            [sys.executable, stddrawPath, 'confirmFileSave'])
    except (pygame.error) as e:
        childProcess = subprocess.Popen(
            [sys.executable, stddrawPath, 'reportFileSaveError', str(e)])

def _checkForEvents():
    global _surface
    global _keysTyped

    global _mousePos
    global _mousePressed
    _makeSureWindowCreated()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            _keysTyped = [pygame.key.name(event.key)] + _keysTyped
        elif (event.type == pygame.MOUSEBUTTONUP) and \
            (event.button == 3):
            _saveToFile()
        elif (event.type == pygame.MOUSEBUTTONDOWN) and \
            (event.button == 1): 
            _mousePressed = True
            _mousePos = event.pos                      

def hasNextKeyTyped():
    global _keysTyped
    return _keysTyped != []

def nextKeyTyped():
    global _keysTyped
    return _keysTyped.pop()

def clearKeysTyped():
    global _keysTyped
    _keysTyped = []

def mousePressed():
    global _mousePressed
    if _mousePressed:
        _mousePressed = False
        return True
    return False
    
def mouseX():
    global _mousePos
    if _mousePos:
        return _userX(_mousePos[0])      
    raise Exception(
        "Can't determine mouse position if a click hasn't happened")
    
def mouseY():
    global _mousePos
    if _mousePos:
        return _userY(_mousePos[1]) 
    raise Exception(
        "Can't determine mouse position if a click hasn't happened")

setXscale()
setYscale()
setPenRadius()
pygame.font.init()

def _getFileName():
    root = Tkinter.Tk()
    root.withdraw()
    reply = tkFileDialog.asksaveasfilename(initialdir='.')
    sys.stdout.write(reply)
    sys.stdout.flush()
    sys.exit()

def _confirmFileSave():
    root = Tkinter.Tk()
    root.withdraw()
    tkMessageBox.showinfo(title='File Save Confirmation',
        message='The drawing was saved to the file.')
    sys.exit()

def _reportFileSaveError(msg):
    root = Tkinter.Tk()
    root.withdraw()
    tkMessageBox.showerror(title='File Save Error', message=msg)
    sys.exit()



def _regressionTest():


    clear()

    setPenRadius(.5)
    setPenColor(ORANGE)
    point(0.5, 0.5)
    show(0.0)

    setPenRadius(.25)
    setPenColor(BLUE)
    point(0.5, 0.5)
    show(0.0)

    setPenRadius(.02)
    setPenColor(RED)
    point(0.25, 0.25)
    show(0.0)

    setPenRadius(.01)
    setPenColor(GREEN)
    point(0.25, 0.25)
    show(0.0)

    setPenRadius(0)
    setPenColor(BLACK)
    point(0.25, 0.25)
    show(0.0)

    setPenRadius(.1)
    setPenColor(RED)
    point(0.75, 0.75)
    show(0.0)

    setPenRadius(0)
    setPenColor(CYAN)
    for i in range(0, 100):
        point(i / 512.0, .5)
        point(.5, i / 512.0)
    show(0.0)

    setPenRadius(0)
    setPenColor(MAGENTA)
    line(.1, .1, .3, .3)
    line(.1, .2, .3, .2)
    line(.2, .1, .2, .3)
    show(0.0)

    setPenRadius(.05)
    setPenColor(MAGENTA)
    line(.7, .5, .8, .9)
    show(0.0)

    setPenRadius(.01)
    setPenColor(YELLOW)
    circle(.75, .25, .2)
    show(0.0)

    setPenRadius(.01)
    setPenColor(YELLOW)
    filledCircle(.75, .25, .1)
    show(0.0)

    setPenRadius(.01)
    setPenColor(PINK)
    rectangle(.25, .75, .1, .2)
    show(0.0)

    setPenRadius(.01)
    setPenColor(PINK)
    filledRectangle(.25, .75, .05, .1)
    show(0.0)

    setPenRadius(.01)
    setPenColor(DARK_RED)
    square(.5, .5, .1)
    show(0.0)

    setPenRadius(.01)
    setPenColor(DARK_RED)
    filledSquare(.5, .5, .05)
    show(0.0)

    setPenRadius(.01)
    setPenColor(DARK_BLUE)
    polygon([.4, .5, .6], [.7, .8, .7])
    show(0.0)

    setPenRadius(.01)
    setPenColor(DARK_GREEN)
    setFontSize(24)
    text(.2, .4, 'hello, world')
    show(0.0)



    setPenColor(BLACK)
    print('Left click with the mouse or type a key')
    while True:
        if mousePressed():
            filledCircle(mouseX(), mouseY(), .02)
        if hasNextKeyTyped():
            print(nextKeyTyped())
        show(0.0)
    show()

def _main():

    import sys
    if len(sys.argv) == 1:
        _regressionTest()
    elif sys.argv[1] == 'getFileName':
        _getFileName()
    elif sys.argv[1] == 'confirmFileSave':
        _confirmFileSave()
    elif sys.argv[1] == 'reportFileSaveError':
        _reportFileSaveError(sys.argv[2])

if __name__ == '__main__':
    _main()
