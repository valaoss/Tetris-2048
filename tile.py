import stddraw
from color import Color

_COLOR = {
    2:   Color(238, 228, 218),
    4:   Color(237, 224, 200),
    8:   Color(242, 177, 121),
    16:  Color(245, 149, 99),
    32:  Color(246, 124, 95),
    64:  Color(246, 94, 59),
    128: Color(237, 207, 114),
    256: Color(237, 204, 97),
    512: Color(237, 200, 80),
    1024:Color(237, 197, 63),
    2048:Color(237, 194, 46)
}

_TEXT_COLOR = {
    2:   Color(119, 110, 101),
    4:   Color(119, 110, 101),
    8:   Color(255, 255, 255), 16: Color(255, 255, 255),
    32:  Color(255, 255, 255), 64: Color(255, 255, 255),
    128: Color(255, 255, 255),256: Color(255, 255, 255),
    512: Color(255, 255, 255),1024: Color(255, 255, 255),
    2048:Color(255, 255, 255)
}

class Tile:
    def __init__(self, number=2):
        self.number = number

    def draw(self, pos, size=1):
        # Kare yarıçapı
        r = size/2 * 0.95
        # Arka plan rengi
        stddraw.setPenColor(_COLOR.get(self.number, Color(204, 192, 179)))
        stddraw.filledSquare(pos.x, pos.y, r)
        # Yazı rengi ve gösterim
        stddraw.setPenColor(_TEXT_COLOR.get(self.number, Color(119, 110, 101)))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(20)
        stddraw.text(pos.x, pos.y, str(self.number))
