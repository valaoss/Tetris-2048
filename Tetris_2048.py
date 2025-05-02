import sys
import stddraw
from color import Color
import os, random, math, time
from point import Point
from game_grid import GameGrid
from tetromino import Tetromino
import copy
import pygame

BEST_SCORE_FILE   = "best_score.txt"
MUSIC_FILE        = "tetris_theme.wav"

MARGIN_CELLS      = 2
VERT_MARGIN_CELLS = 1
SIDE_UNITS        = 5

GAME_TITLE = "MergeTris"

PALETTE_2048 = [
    Color(238,228,218),
    Color(237,224,200),
    Color(242,177,121),
    Color(245,149, 99)
]
TEXT_2048 = Color(119,110,101)

falling_blocks = []

# --- Basit Zone-Combo Sistemi için global değişkenler ---
combo_count   = 0
last_zone     = None

# Oyun durumu
drop_delay    = 0.5
score         = 0
best_score    = 0
sound_on      = True
lines_cleared = 0
level         = 1
music_volume  = 0.5

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
    for x, y, _ in tetro.get_cells():
        if x < 0 or x >= grid.grid_width or y < 0 or y >= grid.grid_height:
            return False
        if grid.is_occupied(y, x):
            return False
    return True

def init_falling_blocks(n, grid_w, grid_h):
    global falling_blocks
    falling_blocks = []
    for _ in range(n):
        x     = random.uniform(0, grid_w + SIDE_UNITS)
        y     = random.uniform(grid_h, grid_h + 5)
        speed = random.uniform(0.2, 1.0)
        size  = random.uniform(0.2, 0.6)
        falling_blocks.append([x, y, speed, size])

def update_and_draw_falling_blocks(grid_w, grid_h):
    for blk in falling_blocks:
        x, y, speed, size = blk
        stddraw.setPenColor(Color(143,122,102))
        stddraw.filledRectangle(x, y, size, size)
        y -= speed * 0.1
        if y < -size:
            y = grid_h + size
        blk[1] = y

def display_start_screen(grid_h, grid_w):
    load_best_score()
    bg = Color(240,230,180)
    init_falling_blocks(20, grid_w, grid_h)

    menu_w, menu_h = grid_w * 0.6, 1.5
    spacing        = 0.5
    options        = ["New Game", "Continue", f"Best: {best_score}", "Quit Game"]
    colors_box     = PALETTE_2048
    colors_txt     = [TEXT_2048] * len(options)

    title_w = menu_w + 1.0
    title_h = 2.0
    cx = grid_w/2 + SIDE_UNITS/2
    ty  = grid_h - 5
    sy  = ty - title_h/2 - spacing - menu_h/2

    while True:
        stddraw.clear(bg)
        update_and_draw_falling_blocks(grid_w, grid_h)

        # Başlık
        stddraw.setPenColor(PALETTE_2048[0])
        stddraw.filledRectangle(cx - title_w/2, ty - title_h/2, title_w, title_h)
        stddraw.setPenColor(TEXT_2048); stddraw.setPenRadius(0.01)
        stddraw.rectangle(cx - title_w/2, ty - title_h/2, title_w, title_h)
        stddraw.setPenRadius()
        stddraw.setFontFamily("Arial"); stddraw.setFontSize(32)
        stddraw.text(cx, ty, GAME_TITLE)

        # Menü seçenekleri
        for i,(opt,cbox,ctxt) in enumerate(zip(options,colors_box,colors_txt)):
            y = sy - i*(menu_h+spacing)
            x0 = cx - menu_w/2
            stddraw.setPenColor(cbox)
            stddraw.filledRectangle(x0, y - menu_h/2, menu_w, menu_h)
            stddraw.setPenColor(ctxt); stddraw.setFontSize(24)
            stddraw.text(cx, y, opt)

        stddraw.show(100)
        if stddraw.mousePressed():
            mx,my = stddraw.mouseX(), stddraw.mouseY()
            for i in range(len(options)):
                y = sy - i*(menu_h+spacing)
                x0 = cx - menu_w/2
                if x0<=mx<=x0+menu_w and y-menu_h/2<=my<=y+menu_h/2:
                    return ['new','continue','best','quit'][i]

def draw_border(grid_w, grid_h):
    stddraw.setPenColor(Color(33,150,243)); stddraw.setPenRadius(0.005)
    lo,bo,inset = -0.45, -0.45, 0.5
    stddraw.line(lo,bo, grid_w-inset,bo)
    stddraw.line(grid_w-inset,bo, grid_w-inset,grid_h-inset)
    stddraw.line(grid_w-inset,grid_h-inset, lo,grid_h-inset)
    stddraw.line(lo,grid_h-inset, lo,bo)
    stddraw.setPenRadius()

def draw_side_panel(grid_w, next_tetro):
    global score, best_score, combo_count, sound_on, level, music_volume

    panel_w  = SIDE_UNITS
    panel_x0 = grid_w
    sp       = 0.3
    h        = Tetromino.grid_height
    dy       = -0.5

    # Arka plan
    stddraw.setPenColor(Color(20,20,40))
    stddraw.filledRectangle(panel_x0, dy, panel_w, h)

    # Başlık
    logo_h = 2.0
    stddraw.setPenColor(Color(255,215,0))
    stddraw.filledRectangle(panel_x0, h-logo_h+dy, panel_w, logo_h)
    stddraw.setPenColor(Color(230,230,230)); stddraw.setFontSize(24)
    stddraw.text(panel_x0+panel_w/2, h-logo_h/2+dy, GAME_TITLE)

    # Skor ve Best
    box_h = 1.2
    box_w = (panel_w - 3*sp)/2
    y0    = h - logo_h - sp - box_h + dy
    x0    = panel_x0 + sp
    x1    = panel_x0 + panel_w - sp - box_w
    for lbl,val,x in [("Score",score,x0),("Best",best_score,x1)]:
        stddraw.setPenColor(Color(70,70,90))
        stddraw.filledRectangle(x, y0, box_w, box_h)
        stddraw.setPenColor(Color(230,230,230)); stddraw.setFontSize(12)
        stddraw.text(x+box_w/2, y0+box_h-0.2, lbl)
        stddraw.setFontSize(18)
        stddraw.text(x+box_w/2, y0+box_h/2-0.1, str(val))

    # Combo göstergesi
    small_h = 0.8
    y1 = y0 - sp - small_h
    stddraw.setPenColor(Color(60,160,60))
    stddraw.filledRectangle(x0, y1, panel_w-2*sp, small_h)
    stddraw.setPenColor(Color(230,230,230)); stddraw.setFontSize(12)
    stddraw.text(panel_x0+panel_w/2, y1+small_h/2-0.05, f"Combo x{combo_count}")

    # Seviye
    lvl_y = y1 - sp - 0.4
    stddraw.setPenColor(Color(255,215,0)); stddraw.setFontSize(14)
    stddraw.text(panel_x0+panel_w/2, lvl_y+dy, f"Level {level}")

    # Next preview
    ny = lvl_y - sp - 0.3
    stddraw.setPenColor(Color(230,230,230)); stddraw.setFontSize(12)
    stddraw.text(panel_x0+panel_w/2, ny+dy, "Next")
    mat = next_tetro.get_min_bounded_tile_matrix(False)
    rows,cols = len(mat), len(mat[0])
    cell = 0.75
    pw,ph = cols*cell, rows*cell
    px = panel_x0 + (panel_w-pw)/2
    py = ny - sp - ph + dy
    for r in range(rows):
        for c in range(cols):
            t = mat[r][c]
            if t:
                tx = px + c*cell
                ty = py + (rows-1-r)*cell
                cp = copy.deepcopy(t)
                cp.cell_size = cell
                cp.draw(Point(tx+cell/2, ty+cell/2))

    # Ses butonları
    by = sp + dy
    btn_w = (panel_w - 4*sp) / 3
    btn_h = small_h
    cx = panel_x0 + panel_w/2
    total = 3*btn_w + 2*sp
    start_x = cx - total/2

    mute_x = start_x
    stddraw.setPenColor(Color(70,70,90))
    stddraw.filledRectangle(mute_x, by, btn_w, btn_h)
    stddraw.setPenColor(Color(230,230,230)); stddraw.setFontSize(16)
    stddraw.text(mute_x+btn_w/2, by+btn_h/2, "🔇")
    mute_btn = (mute_x, by, btn_w, btn_h)

    vd_x = mute_x + btn_w + sp
    stddraw.setPenColor(Color(70,70,90))
    stddraw.filledRectangle(vd_x, by, btn_w, btn_h)
    stddraw.setPenColor(Color(230,230,230))
    stddraw.text(vd_x+btn_w/2, by+btn_h/2, "-")
    vol_down_btn = (vd_x, by, btn_w, btn_h)

    vu_x = vd_x + btn_w + sp
    stddraw.setPenColor(Color(70,70,90))
    stddraw.filledRectangle(vu_x, by, btn_w, btn_h)
    stddraw.setPenColor(Color(230,230,230))
    stddraw.text(vu_x+btn_w/2, by+btn_h/2, "+")
    vol_up_btn = (vu_x, by, btn_w, btn_h)

    return mute_btn, vol_down_btn, vol_up_btn

def animate_combo(count, grid, grid_w, next_tetro):
    palette = [Color(255,100,100), Color(100,255,150),
               Color(150,100,255), Color(255,220,100)]
    cx = grid_w/2 + SIDE_UNITS/2
    cy = Tetromino.grid_height/2 + 4
    for frame in range(8):
        grid.display()
        draw_border(grid_w, Tetromino.grid_height)
        draw_side_panel(grid_w, next_tetro)
        size = 30 + (frame if frame<4 else 7-frame)*8
        stddraw.setFontSize(size)
        stddraw.setPenColor(random.choice(palette))
        stddraw.text(cx, cy, f"Combo x{count}!")
        for _ in range(12):
            a = random.random()*2*math.pi
            dist = random.uniform(2,5)*(frame+1)/8
            px = cx + math.cos(a)*dist
            py = cy + math.sin(a)*dist
            r = random.uniform(0.1,0.3)
            stddraw.filledCircle(px, py, r)
        stddraw.show(40)

def start():
    global score, best_score, combo_count, last_zone
    global drop_delay, lines_cleared, level, sound_on, music_volume

    pygame.mixer.init()
    if os.path.exists(MUSIC_FILE):
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
        sound_on = True

    grid_h, grid_w = 20, 10
    canvas_h = 40 * (grid_h + 2*VERT_MARGIN_CELLS)
    canvas_w = 40 * (grid_w + SIDE_UNITS + MARGIN_CELLS)
    stddraw.setCanvasSize(canvas_w, canvas_h)

    if hasattr(stddraw, 'setWindowTitle'):
        stddraw.setWindowTitle(GAME_TITLE)
    elif hasattr(stddraw, 'setTitle'):
        stddraw.setTitle(GAME_TITLE)

    stddraw.setXscale(-MARGIN_CELLS+1.0, grid_w + SIDE_UNITS + 1.0)
    stddraw.setYscale(-VERT_MARGIN_CELLS, grid_h + VERT_MARGIN_CELLS)
    Tetromino.grid_height, Tetromino.grid_width = grid_h, grid_w

    while True:
        load_best_score()
        choice = display_start_screen(grid_h, grid_w)
        if choice == "quit":
            pygame.mixer.quit()
            sys.exit()
        if choice == "best":
            continue

        score, combo_count, lines_cleared = 0, 0, 0
        last_zone = None
        level, drop_delay = 1, 0.5

        grid = GameGrid(grid_h, grid_w)
        current = Tetromino(); grid.current_tetromino = current
        next_tetro = Tetromino()
        last_drop = time.time()

        while True:
            now = time.time()
            if now - last_drop > drop_delay:
                landed = not current.move("down", grid)
                last_drop = now

                if landed:
                    # Blok sabitleme
                    cells = current.get_cells()
                    tiles, pos = current.get_min_bounded_tile_matrix(True)
                    game_over = grid.update_grid(tiles, pos)

                    # Merge & satır temizleme
                    merged = grid.merge_tiles()
                    rows   = grid.clear_full_rows()
                    grid.remove_floating()

                    # Zone tespiti
                    zone_width = max(1, grid.grid_width // 3)
                    min_x      = min(x for x,y,_ in cells)
                    zone       = min_x // zone_width

                    # Combo sayısını güncelle
                    if merged > 0 or rows > 0:
                        if zone == last_zone:
                            combo_count += 1
                        else:
                            combo_count = 1
                            last_zone    = zone
                    else:
                        combo_count = 0
                        last_zone    = None

                    # Çarpan hesapla (her combo +%50, max 3×)
                    multiplier = 1 + 0.5 * (combo_count - 1)
                    multiplier = min(multiplier, 3)

                    # Puan ekle
                    base_points = merged * 100 + rows * 200
                    score      += int(base_points * multiplier)

                    # Combo animasyonu
                    if combo_count > 1:
                        animate_combo(combo_count, grid, grid_w, next_tetro)

                    # Her satır temizleme başına 1 seviye atla (sadece 1 seviye)
                    if rows > 0:
                        lines_cleared += rows
                        level += 1
                        drop_delay = max(0.1, 0.5 - 0.05*(level-1))

                    if game_over:
                        break

                    # Sonraki parça
                    current = next_tetro
                    grid.current_tetromino = current
                    next_tetro = Tetromino()
                    if not valid_position(current, grid):
                        break

            # Kullanıcı girişi ve çizim
            while stddraw.hasNextKeyTyped():
                key = stddraw.nextKeyTyped()
                if key in ("left","right","down"):
                    current.move(key, grid)
                elif key == "space":
                    while current.move("down", grid):
                        grid.display()
                        draw_border(grid_w, grid_h)
                        draw_side_panel(grid_w, next_tetro)
                        stddraw.show(20)
                elif key == "up":
                    ox, oy = current.bottom_left_cell.x, current.bottom_left_cell.y
                    current.rotate()
                    if not valid_position(current, grid):
                        for dx in (1,-1,2,-2):
                            current.bottom_left_cell.x = ox + dx
                            if valid_position(current, grid): break
                        else:
                            for _ in range(3): current.rotate()
                            current.bottom_left_cell.x, current.bottom_left_cell.y = ox, oy
                elif key == "p":
                    if sound_on: pygame.mixer.music.pause()
                    sub = display_start_screen(grid_h, grid_w)
                    if sound_on: pygame.mixer.music.unpause()
                    if sub == "quit":
                        pygame.mixer.quit()
                        sys.exit()
                    if sub == "new":
                        break
                elif key == "q":
                    pygame.mixer.quit()
                    sys.exit()
                stddraw.clearKeysTyped()
            else:
                sound_btn, minus_btn, plus_btn = draw_side_panel(grid_w, next_tetro)
                if stddraw.mousePressed():
                    mx, my = stddraw.mouseX(), stddraw.mouseY()
                    x0, y0, w0, h0 = sound_btn
                    if x0<=mx<=x0+w0 and y0<=my<=y0+h0:
                        sound_on = not sound_on
                        if sound_on: pygame.mixer.music.unpause()
                        else:        pygame.mixer.music.pause()
                    xm, ym, wm, hm = minus_btn
                    if xm<=mx<=xm+wm and ym<=my<=ym+hm:
                        music_volume = max(0.0, music_volume-0.1)
                        pygame.mixer.music.set_volume(music_volume)
                    xp, yp, wp, hp = plus_btn
                    if xp<=mx<=xp+wp and yp<=my<=yp+hp:
                        music_volume = min(1.0, music_volume+0.1)
                        pygame.mixer.music.set_volume(music_volume)

                grid.display()
                draw_border(grid_w, grid_h)
                draw_side_panel(grid_w, next_tetro)
                stddraw.show(50)
                continue
            break

        # Oyun bittiğinde skor kaydetme ve ekran
        if score > best_score:
            best_score = score
            save_best_score()

        stddraw.clear(Color(0,0,0))
        stddraw.setPenColor(Color(255,255,255)); stddraw.setFontSize(30)
        stddraw.text(grid_w/2+SIDE_UNITS/2, grid_h/2+2, "GAME OVER")
        stddraw.setFontSize(20)
        stddraw.text(grid_w/2+SIDE_UNITS/2, grid_h/2,       f"Score: {score}")
        stddraw.text(grid_w/2+SIDE_UNITS/2, grid_h/2-2,     f"Best:  {best_score}")
        stddraw.show(1000)

if __name__ == '__main__':
    start()
