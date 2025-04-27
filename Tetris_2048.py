import stddraw
from color import Color
import os, random, time
from point import Point
from game_grid import GameGrid
from tetromino import Tetromino
import copy
import pygame
from picture import Picture

BEST_SCORE_FILE = "best_score.txt"
MUSIC_FILE = "tetris_theme.wav"
MENU_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'image', 'menu_image.png')

drop_delay = 0.5  # seconds between automatic drops
score = 0
best_score = 0

def load_best_score():
    global best_score
    if os.path.exists(BEST_SCORE_FILE):
        try:
            with open(BEST_SCORE_FILE, "r") as f:
                best_score = int(f.read().strip())
        except:
            best_score = 0
    else:
        best_score = 0

def save_best_score():
    try:
        with open(BEST_SCORE_FILE, "w") as f:
            f.write(str(best_score))
    except:
        pass

def valid_position(tetro, grid):
    for x, y, tile in tetro.get_cells():
        if x < 0 or x >= grid.grid_width or y < 0 or y >= grid.grid_height:
            return False
        if grid.is_occupied(y, x):
            return False
    return True

def display_start_screen(grid_h, grid_w):
    """Shows New Game / Continue / Best Score menu"""
    bg = Color(42, 69, 99)
    load_best_score()
    try:
        menu_pic = Picture(MENU_IMAGE_PATH)
    except:
        menu_pic = None

    options = ["New Game", "Continue", f"Best: {best_score}"]
    n = len(options)
    box_w, box_h, spacing = 8, 2, 1.5
    cx, cy = grid_w/2, grid_h/2
    start_y = cy + (n-1)/2*(box_h+spacing)

    while True:
        stddraw.clear(bg)
        if menu_pic:
            stddraw.picture(menu_pic, cx, grid_h - 3)
        for i, text in enumerate(options):
            y = start_y - i*(box_h+spacing)
            x0, y0 = cx - box_w/2, y - box_h/2
            stddraw.setPenColor(Color(200, 200, 200))
            stddraw.filledRectangle(x0, y0, box_w, box_h)
            stddraw.setPenColor(Color(0, 0, 0))
            stddraw.setFontSize(20)
            stddraw.text(cx, y, text)
        stddraw.show(100)

        if stddraw.mousePressed():
            mx, my = stddraw.mouseX(), stddraw.mouseY()
            for i in range(n):
                y = start_y - i*(box_h+spacing)
                if cx-box_w/2 <= mx <= cx+box_w/2 and y-box_h/2 <= my <= y+box_h/2:
                    return "new" if i==0 else ("continue" if i==1 else "best")

def draw_side_panel(grid_w, next_tetro):
    global score, best_score
    px = grid_w + 0.2
    gh = Tetromino.grid_height

    box_w, box_h = 2, 1.5
    gap = 0.5
    y_top = gh - 2

    # SCORE box
    stddraw.setPenColor(Color(50, 50, 50))
    stddraw.filledRectangle(px, y_top - box_h/2, box_w, box_h)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontSize(14)
    stddraw.text(px + box_w/2, y_top + 0.3, "SCORE")
    stddraw.setFontSize(20)
    stddraw.text(px + box_w/2, y_top - 0.3, str(score))

    # BEST box
    bx = px + box_w + gap
    stddraw.setPenColor(Color(50, 50, 50))
    stddraw.filledRectangle(bx, y_top - box_h/2, box_w, box_h)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontSize(14)
    stddraw.text(bx + box_w/2, y_top + 0.3, "BEST")
    stddraw.setFontSize(20)
    stddraw.text(bx + box_w/2, y_top - 0.3, str(best_score))

    # NEXT preview
    label_y = y_top - box_h - 1
    center_x = px + (2*box_w + gap)/2
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontSize(16)
    stddraw.text(center_x, label_y + 0.5, "NEXT:")
    mat = next_tetro.get_min_bounded_tile_matrix(False)
    rows, cols = len(mat), len(mat[0])
    cell = 1
    total_w = cols * cell
    start_x = center_x - total_w/2
    start_y = label_y - 1 - (rows - 1) * cell / 2
    for r in range(rows):
        for c in range(cols):
            tile = mat[r][c]
            if tile:
                x = start_x + c * cell + cell/2
                y = start_y + (rows - 1 - r) * cell
                tile.draw(Point(x, y))

def start():
    global score, best_score
    pygame.mixer.init()
    if os.path.exists(MUSIC_FILE):
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)

    grid_h, grid_w = 20, 10
    canvas_h = 40 * grid_h
    canvas_w = 40 * grid_w + 200
    stddraw.setCanvasSize(canvas_w, canvas_h)
    stddraw.setXscale(-0.5, grid_w + 4.5)
    stddraw.setYscale(-0.5, grid_h - 0.5)
    Tetromino.grid_height, Tetromino.grid_width = grid_h, grid_w

    grid = GameGrid(grid_h, grid_w)
    current = Tetromino()
    grid.current_tetromino = current
    next_tetro = Tetromino()

    choice = display_start_screen(grid_h, grid_w)
    if choice == "new":
        score = 0
        grid = GameGrid(grid_h, grid_w)
        current = Tetromino()
        grid.current_tetromino = current
        next_tetro = Tetromino()
    load_best_score()

    last_drop = time.time()
    while True:
        now = time.time()

        # automatic drop
        if now - last_drop > drop_delay:
            landed = not current.move("down", grid)
            last_drop = now

            if landed:
                tiles, pos = current.get_min_bounded_tile_matrix(True)
                game_over = grid.update_grid(tiles, pos)
                score += grid.merge_tiles()
                score += grid.clear_full_rows()
                score += grid.remove_floating()

                if game_over:
                    break

                # spawn next
                current = next_tetro
                grid.current_tetromino = current
                next_tetro = Tetromino()

                # **NEW CHECK**: if we can’t place the new piece, end game
                if not valid_position(current, grid):
                    break

        # user input
        while stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == "left":
                current.move("left", grid)
            elif key == "right":
                current.move("right", grid)
            elif key == "down":
                current.move("down", grid)
            elif key in ("up", "z", "space"):
                old_mat = copy.deepcopy(current.matrix)
                ox, oy = current.bottom_left_cell.x, current.bottom_left_cell.y
                current.rotate()
                kicked = False
                for dx in (0, -1, 1, -2, 2):
                    current.bottom_left_cell.x = ox + dx
                    if valid_position(current, grid):
                        kicked = True
                        break
                if not kicked:
                    current.matrix = old_mat
                    current.bottom_left_cell.x, current.bottom_left_cell.y = ox, oy

            elif key == "p":
                pygame.mixer.music.pause()
                ch = display_start_screen(grid_h, grid_w)
                pygame.mixer.music.unpause()
                if ch == "new":
                    score = 0
                    grid = GameGrid(grid_h, grid_w)
                    current = Tetromino()
                    grid.current_tetromino = current
                    next_tetro = Tetromino()

            stddraw.clearKeysTyped()

        # draw
        grid.display()
        draw_side_panel(grid_w, next_tetro)
        stddraw.show(50)

    # game over
    if score > best_score:
        best_score = score
        save_best_score()

    stddraw.clear(Color(0, 0, 0))
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontSize(30)
    stddraw.text(grid_w/2, grid_h/2 + 2, "GAME OVER")
    stddraw.text(grid_w/2, grid_h/2, f"Score: {score}")
    stddraw.text(grid_w/2, grid_h/2 - 2, f"Best: {best_score}")
    stddraw.show()

if __name__ == '__main__':
    start()
