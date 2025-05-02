class Color:
    def __init__(self, r=0, g=0, b=0):

        self._r = r  # Red component
        self._g = g  # Green component
        self._b = b  # Blue component

    def getRed(self):

        return self._r

    def getGreen(self):

        return self._g

    def getBlue(self):

        return self._b

    def __str__(self):


        return '(' + str(self._r) + ', ' + str(self._g) + ', ' + \
            str(self._b) + ')'

WHITE      = Color(255, 255, 255)
BLACK      = Color(  0,   0,   0)

RED        = Color(255,   0,   0)
GREEN      = Color(  0, 255,   0)
BLUE       = Color(  0,   0, 255)

CYAN       = Color(  0, 255, 255)
MAGENTA    = Color(255,   0, 255)
YELLOW     = Color(255, 255,   0)

DARK_RED   = Color(128,   0,   0)
DARK_GREEN = Color(  0, 128,   0)
DARK_BLUE  = Color(  0,   0, 128)

GRAY       = Color(128, 128, 128)
DARK_GRAY  = Color( 64,  64,  64)
LIGHT_GRAY = Color(192, 192, 192)

ORANGE     = Color(255, 200,   0)
VIOLET     = Color(238, 130, 238)
PINK       = Color(255, 175, 175)

BOOK_BLUE  = Color(  9,  90, 166)
BOOK_LIGHT_BLUE = Color(103, 198, 243)

BOOK_RED   = Color(150,  35,  31)
def _main():

    c1 = Color(0, 128, 255)
    print(c1)
    print(c1.getRed())
    print(c1.getGreen())
    print(c1.getBlue())

if __name__ == '__main__':
    _main()