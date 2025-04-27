
import random, copy
from point import Point
from tile import Tile

_SHAPES = {
    'I': [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    'O': [[0,1,1,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]],
    'T': [[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
    'S': [[0,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]],
    'Z': [[1,1,0,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]],
    'J': [[1,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
    'L': [[0,0,1,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]
}

class Tetromino:
    grid_height = None
    grid_width  = None


    def __init__(self, shape=None):
        self.type = shape or random.choice(list(_SHAPES))
        # Tile matrisi oluştur
        self.matrix = [
            [Tile(random.choice([2,4])) if cell else None for cell in row]
            for row in _SHAPES[self.type]
        ]
        # spawn pozisyonu
        self.bottom_left_cell = Point(
            random.randint(0, Tetromino.grid_width - 4),
            Tetromino.grid_height - 4
        )

    def _rot90(self, ccw=False):
        m = self.matrix
        self.matrix = [list(row) for row in zip(*m[::-1])] if ccw else \
                      [list(row[::-1]) for row in zip(*m)]
    def rotate(self):     self._rot90()
    def rotate_ccw(self): self._rot90(True)


    def get_cell_position(self, row, col):
        n = len(self.matrix)
        return Point(
            self.bottom_left_cell.x + col,
            self.bottom_left_cell.y + (n - 1 - row)
        )

    def get_cells(self):

        cells = []
        for r in range(4):
            for c in range(4):
                if self.matrix[r][c]:
                    p = self.get_cell_position(r, c)
                    cells.append((p.x, p.y, self.matrix[r][c]))
        return cells


    def can_be_moved(self, direction, grid):
        n = len(self.matrix)

        if direction in ("left", "right"):
            step = -1 if direction == "left" else 1
            for r in range(n):
                cols = range(n) if step == -1 else range(n-1, -1, -1)
                for c in cols:
                    if self.matrix[r][c]:
                        pos = self.get_cell_position(r, c)
                        new_x = pos.x + step
                        if new_x < 0 or new_x >= Tetromino.grid_width: return False
                        if grid.is_occupied(pos.y, new_x): return False
                        break
        else:   # down
            for c in range(n):
                for r in range(n - 1, -1, -1):
                    if self.matrix[r][c]:
                        pos = self.get_cell_position(r, c)
                        new_y = pos.y - 1
                        if new_y < 0: return False
                        if grid.is_occupied(new_y, pos.x): return False
                        break
        return True

    def move(self, direction, grid):
        if not self.can_be_moved(direction, grid):
            return False
        if direction == "left":
            self.bottom_left_cell.x -= 1
        elif direction == "right":
            self.bottom_left_cell.x += 1
        else:   # "down"
            self.bottom_left_cell.y -= 1
        return True


    def get_min_bounded_tile_matrix(self, return_position=False):
        n = len(self.matrix)
        min_r, max_r, min_c, max_c = n - 1, 0, n - 1, 0
        for r in range(n):
            for c in range(n):
                if self.matrix[r][c]:
                    min_r = min(min_r, r);
                    max_r = max(max_r, r)
                    min_c = min(min_c, c);
                    max_c = max(max_c, c)

        # -- KOPYA MATRİS OLUŞTUR --
        copy_mat = [[None] * (max_c - min_c + 1) for _ in range(max_r - min_r + 1)]
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.matrix[r][c]:
                    copy_mat[r - min_r][c - min_c] = copy.deepcopy(self.matrix[r][c])

        if not return_position:
            return copy_mat
        else:
            pos = Point(
                self.bottom_left_cell.x + min_c,
                self.bottom_left_cell.y + (n - 1 - max_r)
            )
            return copy_mat, pos


    def draw(self, ox=0, oy=0, cell_size=1):
        """ Eğer GameGrid.display() içinden çağrılırsa ox/oy kullanılmaz """
        for gx, gy, tile in self.get_cells():
            tile.draw(Point(gx, gy))
