import stddraw
import time
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from color import Color
from tile import Tile
from point import Point

class GameGrid:

    def __init__(self, rows=20, cols=10, web_port=None):
        self.grid_height = rows
        self.grid_width  = cols
        self.tile_matrix = [[None for _ in range(cols)] for _ in range(rows)]
        self.current_tetromino = None
        self.game_over = False

        # Visual settings
        self.empty_color    = Color(42, 69, 99)
        self.line_color     = Color(0, 100, 200)
        self.border_color   = Color(0, 100, 200)
        self.line_thickness = 0.002
        self.border_thick   = 10 * self.line_thickness
        if web_port:
            self._start_web_server(web_port)

    def _start_web_server(self, port):
        class GridHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/grid':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    grid_data = [[tile.number if tile else None for tile in row]
                                 for row in self.server.gamegrid.tile_matrix]
                    self.wfile.write(json.dumps({'grid': grid_data}).encode())
                elif self.path == '/state':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    state = {
                        'game_over': self.server.gamegrid.game_over,
                        'height': self.server.gamegrid.grid_height,
                        'width': self.server.gamegrid.grid_width
                    }
                    self.wfile.write(json.dumps(state).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

        server = HTTPServer(('0.0.0.0', port), GridHandler)
        server.gamegrid = self
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

    def is_inside(self, row, col):
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width

    def is_occupied(self, row, col):
        return self.is_inside(row, col) and self.tile_matrix[row][col] is not None

    def update_grid(self, tiles_to_lock, blc_pos):
        self.current_tetromino = None
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
        for r in range(n_rows):
            for c in range(n_cols):
                tile = tiles_to_lock[r][c]
                if tile is None:
                    continue
                gx = blc_pos.x + c
                gy = blc_pos.y + (n_rows - 1 - r)
                if self.is_inside(gy, gx):
                    self.tile_matrix[gy][gx] = tile
                else:
                    self.game_over = True
        return self.game_over

    def merge_tiles(self):
        score = 0
        merged_cells = []
        for col in range(self.grid_width):
            row = 0
            while row < self.grid_height - 1:
                cur = self.tile_matrix[row][col]
                above = self.tile_matrix[row + 1][col]
                if cur and above and cur.number == above.number:
                    new_val = cur.number * 2
                    self.tile_matrix[row][col] = Tile(new_val)
                    self.tile_matrix[row + 1][col] = None
                    score += new_val
                    merged_cells.append((row, col))
                row += 1
        for (r, c) in merged_cells:
            ux, uy = c, r
            for scale in (1.3, 1.1, 1.0):
                stddraw.clear(self.empty_color)
                self._draw_grid_lines()
                self._draw_tiles()
                self._draw_border()
                stddraw.setPenColor(Color(255, 255, 255))
                stddraw.filledSquare(ux, uy, scale * 0.5)
                stddraw.show(80)
        return score

    def clear_full_rows(self):
        score = 0
        r = 0
        while r < self.grid_height:
            if None not in self.tile_matrix[r]:
                score += sum(t.number for t in self.tile_matrix[r])
                del self.tile_matrix[r]
                self.tile_matrix.append([None] * self.grid_width)
            else:
                r += 1
        return score

    def remove_floating(self):
        h, w = self.grid_height, self.grid_width
        visited = [[False] * w for _ in range(h)]
        removed_tiles = []
        removed_score = 0

        def flood(r, c):
            if r < 0 or r >= h or c < 0 or c >= w:
                return
            if visited[r][c] or self.tile_matrix[r][c] is None:
                return
            visited[r][c] = True
            flood(r + 1, c)
            flood(r - 1, c)
            flood(r, c + 1)
            flood(r, c - 1)

        for c in range(w):
            if self.tile_matrix[0][c] is not None:
                flood(0, c)

        for r in range(h):
            for c in range(w):
                tile = self.tile_matrix[r][c]
                if tile and not visited[r][c]:
                    removed_score += tile.number
                    removed_tiles.append((r, c, tile))
                    self.tile_matrix[r][c] = None

        if len(removed_tiles) >= 4:
            for radius in (0.2, 0.35, 0.5, 0.35, 0.2):
                stddraw.clear(self.empty_color)
                self._draw_grid_lines()
                self._draw_tiles()
                self._draw_border()
                stddraw.setPenColor(Color(255, 255, 0))
                for (rr, cc, _) in removed_tiles:
                    stddraw.circle(cc, rr, radius)
                stddraw.show(80)

        if removed_tiles:
            target_x = self.grid_width + 2
            target_y = self.grid_height - 2
            frames = 15
            for f in range(1, frames + 1):
                stddraw.clear(self.empty_color)
                self._draw_grid_lines()
                self._draw_tiles()
                self._draw_border()
                for (rr, cc, tile) in removed_tiles:
                    x = cc + (target_x - cc) * (f / frames)
                    y = rr + (target_y - rr) * (f / frames)
                    tile.draw(Point(x, y), size=0.8)
                stddraw.show(30)
        return removed_score

    def find_2_combos(self):
        """
        Her 3×3 bölgeyi tarar; eğer çevresindeki 8 hücredeki tüm Tile.number == 2 ise
        ortadaki hücrenin (row, col) koordinatını döndürür.
        """
        combos = []
        for r in range(1, self.grid_height - 1):
            for c in range(1, self.grid_width - 1):
                cnt2 = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        tile = self.tile_matrix[r + dr][c + dc]
                        if tile is not None and tile.number == 2:
                            cnt2 += 1
                if cnt2 == 8:
                    combos.append((r, c))
        return combos

    def apply_2_combo(self):
        """
        find_2_combos() ile bulunan her merkez için:
         - çevresindeki 8 bloğu temizler
         - ortadaki bloğun number özelliğini 16 yapar
        """
        for (r, c) in self.find_2_combos():
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    self.tile_matrix[r + dr][c + dc] = None
            center = self.tile_matrix[r][c]
            if center is not None:
                center.number = 16

    def apply_falling_chain(self):
        """
        Uçurum sonrası düşen bloklardan meydana gelen yeni merge'leri
        zincirleme olarak uygular. Toplam skoru döner.
        """
        chain_score = 0
        while True:
            s = self.merge_tiles()
            if s == 0:
                break
            chain_score += s
            self.remove_floating()
        return chain_score

    def display(self):
        stddraw.clear(self.empty_color)
        self._draw_grid_lines()
        self._draw_tiles()
        self._draw_border()
        if self.current_tetromino:
            self.current_tetromino.draw()

    def _draw_tiles(self):
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                tile = self.tile_matrix[r][c]
                if tile:
                    tile.draw(Point(c, r))

    def _draw_grid_lines(self):
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        sx, ex = -0.5, self.grid_width - 0.5
        sy, ey = -0.5, self.grid_height - 0.5
        for x in range(1, self.grid_width):
            stddraw.line(sx + x, sy, sx + x, ey)
        for y in range(1, self.grid_height):
            stddraw.line(sx, sy + y, ex, sy + y)
        stddraw.setPenRadius()

    def _draw_border(self):
        stddraw.setPenColor(self.border_color)
        stddraw.setPenRadius(self.border_thick)
        stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        stddraw.setPenRadius()
