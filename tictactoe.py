from UpemTK.upemtk import *
from time import time


class Direction:
    VERTICAL = 0
    HORIZONTAL = 1
    NW_SE_DIAGONAL = 2
    SW_NE_DIAGONAL = 4


CELL_SIZE = 100
BOARD_WIDTH = BOARD_HEIGHT = 3
WINDOW_WIDTH = (BOARD_WIDTH + 2) * CELL_SIZE
WINDOW_HEIGHT = (BOARD_HEIGHT + 1) * CELL_SIZE
X_MARGIN = (WINDOW_WIDTH - BOARD_WIDTH * CELL_SIZE) // 2
Y_MARGIN = (WINDOW_HEIGHT - BOARD_HEIGHT * CELL_SIZE) // 2
FRAMERATE = 20
BAR_HEIGHT = -1

RUNNING = True
START = True


def pixel_to_cell(x: int, y: int):
    return (x - X_MARGIN) // CELL_SIZE, (y - Y_MARGIN) // CELL_SIZE


def cell_to_pixel(x: int, y: int):
    return X_MARGIN + (x + .5) * CELL_SIZE, Y_MARGIN + (y + .5) * CELL_SIZE


def format_time(time_to_format: int):
    minutes = ("" if time_to_format // 60 >= 10 else "0") + str(time_to_format // 60)
    seconds = ("" if time_to_format % 60 >= 10 else "0") + str(time_to_format % 60)
    return minutes + ":" + seconds


def compute_text_size():
    global BAR_HEIGHT
    creer_fenetre(0, 0)
    BAR_HEIGHT = taille_texte('X')[1] + 19
    fermer_fenetre()


def check_win(grid: list):
    # Columns check
    for x in range(BOARD_WIDTH):
        winner = sum([grid[y][x] for y in range(BOARD_HEIGHT)]) / BOARD_HEIGHT
        if winner == -1 or winner == 1:
            return int(winner), x, Direction.VERTICAL

    # Lines check
    for y in range(BOARD_HEIGHT):
        winner = sum(grid[y]) / BOARD_WIDTH
        if winner == -1 or winner == 1:
            return int(winner), y, Direction.HORIZONTAL

    # NW-SE diagonal check
    winner = sum([grid[i][i] for i in range(BOARD_HEIGHT)]) / BOARD_HEIGHT
    if winner == -1 or winner == 1:
        return int(winner), 0, Direction.NW_SE_DIAGONAL

    # SW-NE diagonal check
    winner = sum([grid[i][BOARD_HEIGHT - 1 - i] for i in range(BOARD_HEIGHT)]) / BOARD_HEIGHT
    if winner == -1 or winner == 1:
        return int(winner), 0, Direction.SW_NE_DIAGONAL

    return False, None, None


def can_play(grid: list):
    for line in grid:
        for column in line:
            if not column:
                return True
    return False


def draw_label(x: float, y: float, text: str, anchor: str = "center", outline: str = "black", bg: str = "white",
               fg: str = "black", size: int = 24, force_width: int = 0, force_height: int = 0, margin: int = 5):
    width = force_width or taille_texte(text, taille=size)[0]
    height = force_height or taille_texte(text, taille=size)[1]
    if anchor == "center":
        xa, ya, xb, yb = x - width / 2 - margin, y - height / 2 - margin, \
                         x + width / 2 + margin, y + height / 2 + margin
    elif anchor == "n":
        xa, ya, xb, yb = x - width / 2 - margin, y, \
                         x + width / 2 + margin, y + height + 2 * margin
    elif anchor == "s":
        xa, ya, xb, yb = x - width / 2 - margin, y - height - 2 * margin, \
                         x + width / 2 + margin, y
    elif anchor == "e":
        xa, ya, xb, yb = x - width - 2 * margin, y - height / 2 - margin, \
                         x, y + height / 2 + margin
    elif anchor == "w":
        xa, ya, xb, yb = x, y - height / 2 - margin, \
                         x + width + 2 * margin, y + height / 2 + margin
    elif anchor == "nw":
        xa, ya, xb, yb = x, y, \
                         x + width + 2 * margin, y + height + 2 * margin
    elif anchor == "ne":
        xa, ya, xb, yb = x - width - 2 * margin, y, \
                         x, y + height + 2 * margin
    elif anchor == "sw":
        xa, ya, xb, yb = x, y - height - 2 * margin, \
                         x + width + 2 * margin, y
    elif anchor == "se":
        xa, ya, xb, yb = x - width - 2 * margin, y - height - 2 * margin, \
                         x, y
    else:
        return
    rectangle(xa, ya, xb, yb, outline, bg)
    texte((xa + xb) / 2, (ya + yb) / 2, text, fg, ancrage="center",
          taille=size)
    return xa, ya, xb, yb


def draw_board():
    for i in range(BOARD_HEIGHT - 1):
        x, y = cell_to_pixel(0, i + 1)
        ligne(x - CELL_SIZE / 2, y - CELL_SIZE / 2, x + ((BOARD_WIDTH - .5) * CELL_SIZE), y - CELL_SIZE / 2,
              couleur='gray25', epaisseur=CELL_SIZE / 15)
    for i in range(BOARD_WIDTH - 1):
        x, y = cell_to_pixel(i + 1, 0)
        ligne(x - CELL_SIZE / 2, y - CELL_SIZE / 2, x - CELL_SIZE / 2, y + ((BOARD_HEIGHT - .5) * CELL_SIZE),
              couleur='gray25', epaisseur=CELL_SIZE / 15)


def draw_bottom_bar(playing: bool, winner: int):
    rectangle(0, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT + BAR_HEIGHT, remplissage='black')
    if not playing:
        xa, ya, xb, yb = draw_label(WINDOW_WIDTH - 5, WINDOW_HEIGHT + BAR_HEIGHT - 5, 'Quitter', 'se')
        offset = xb - xa + 5
        buttons[(xa, ya, xb, yb)] = lambda: set_running(False)
        xa, ya, xb, yb = draw_label(WINDOW_WIDTH - 5 - offset, WINDOW_HEIGHT + BAR_HEIGHT - 5, 'Rejouer', 'se')
        buttons[(xa, ya, xb, yb)] = lambda: set_start(True)
        offset += xb - xa + 5
        if winner == -1:
            texte(WINDOW_WIDTH - 10 - offset, WINDOW_HEIGHT + BAR_HEIGHT / 2, "Les croix gagnent !",
                  ancrage='e', couleur='#3498db', taille=24)
        elif winner == 1:
            texte(WINDOW_WIDTH - 10 - offset, WINDOW_HEIGHT + BAR_HEIGHT / 2, "Les ronds gagnent !",
                  ancrage='e', couleur='green', taille=24)
        else:
            texte(WINDOW_WIDTH - 10 - offset, WINDOW_HEIGHT + BAR_HEIGHT / 2, "Match nul !",
                  ancrage='e', couleur='orange', taille=24)
    else:
        xa, ya, xb, yb = draw_label(WINDOW_WIDTH - 5, WINDOW_HEIGHT + BAR_HEIGHT - 5, 'Quitter', 'se')
        # offset = xb - xa + 5
        buttons[(xa, ya, xb, yb)] = lambda: set_running(False)


def draw_time(ticks: float, paused: bool):
    effacer('time')
    current_time = format_time(int(ticks))
    texte(10, WINDOW_HEIGHT + BAR_HEIGHT / 2, 'Pause' if paused else current_time, ancrage='w',
          couleur='green' if paused else 'white', taille=24, tag='time')


def draw_circle(x: float, y: float):
    cercle(x, y, 5 * CELL_SIZE / 16, couleur='green', epaisseur=CELL_SIZE / 15)


def draw_cross(x: float, y: float):
    offset = 6 * CELL_SIZE / 16 - CELL_SIZE / 15
    ligne(x - offset, y - offset, x + offset, y + offset, couleur='#3498db', epaisseur=CELL_SIZE / 15)
    ligne(x - offset, y + offset, x + offset, y - offset, couleur='#3498db', epaisseur=CELL_SIZE / 15)


def draw_players(grid: list):
    for i, line in enumerate(grid):
        for j, column in enumerate(line):
            x, y = cell_to_pixel(j, i)
            if column == -1:
                draw_cross(x, y)
            elif column == 1:
                draw_circle(x, y)


def draw_lane(lane: int, direction: Direction):
    if direction == Direction.HORIZONTAL:
        x, y = cell_to_pixel(0, lane)
        ligne(x - CELL_SIZE / 2 + 10, y, x + (BOARD_WIDTH - .5) * CELL_SIZE - 10, y,
              couleur='black', epaisseur=CELL_SIZE / 32)
    elif direction == Direction.VERTICAL:
        x, y = cell_to_pixel(lane, 0)
        ligne(x, y - CELL_SIZE / 2 + 10, x, y + (BOARD_WIDTH - .5) * CELL_SIZE - 10,
              couleur='black', epaisseur=CELL_SIZE / 32)
    elif direction == Direction.NW_SE_DIAGONAL:
        x, y = cell_to_pixel(0, 0)
        ligne(x - CELL_SIZE / 2 + 10, y - CELL_SIZE / 2 + 10, x + (BOARD_WIDTH - .5) * CELL_SIZE - 10,
              y + (BOARD_WIDTH - .5) * CELL_SIZE - 10, couleur='black', epaisseur=CELL_SIZE / 32)
    elif direction == Direction.SW_NE_DIAGONAL:
        x, y = cell_to_pixel(0, 0)
        ligne(x - CELL_SIZE / 2 + 10, y + (BOARD_WIDTH - .5) * CELL_SIZE - 10, x + (BOARD_WIDTH - .5) * CELL_SIZE - 10,
              y - CELL_SIZE / 2 + 10, couleur='black', epaisseur=CELL_SIZE / 32)


def draw_turn_indicator(player: int):
    radius = CELL_SIZE / 8
    cercle(0, WINDOW_HEIGHT / 2, CELL_SIZE / 2, remplissage='#3498db' if player == -1 else 'gray')
    cercle(WINDOW_WIDTH, WINDOW_HEIGHT / 2, CELL_SIZE / 2, remplissage='green' if player == 1 else 'gray')

    x, y = CELL_SIZE / 4.5, WINDOW_HEIGHT / 2
    ligne(x - radius, y - radius, x + radius, y + radius, couleur='white', epaisseur=CELL_SIZE / 32)
    ligne(x - radius, y + radius, x + radius, y - radius, couleur='white', epaisseur=CELL_SIZE / 32)

    x, y = WINDOW_WIDTH - CELL_SIZE / 4.5, WINDOW_HEIGHT / 2
    cercle(x, y, radius, 'white', epaisseur=CELL_SIZE / 32)


def draw_all(grid: list, player: int, ticks: float, playing: bool, paused: bool, winner: int):
    draw_bottom_bar(playing, winner)
    draw_time(ticks, paused)
    draw_board()
    draw_players(grid)
    draw_turn_indicator(player)


def left_click(ev: tuple):
    x, y = abscisse(ev), ordonnee(ev)
    for (xa, ya, xb, yb), f in buttons.items():
        if xa <= x <= xb and ya <= y <= yb:
            f()


def build_grid():
    grid = list()
    for _ in range(BOARD_WIDTH):
        grid.append([0] * BOARD_HEIGHT)
    return grid


def set_start(start: bool):
    global START
    START = start


def set_running(running: bool):
    global RUNNING
    RUNNING = running


def loop():
    creer_fenetre(WINDOW_WIDTH, WINDOW_HEIGHT + BAR_HEIGHT, nom='Morpion')

    grid = build_grid()
    winner = 0
    lane = 0
    direction = None
    player = -1
    playing = True
    paused = False
    ticks = 0
    last_time = time()
    last_round_time = -1

    while RUNNING:
        if START:
            grid = build_grid()
            winner = 0
            lane = 0
            direction = None
            player = -1
            set_start(False)
            playing = True
            paused = False
            ticks = 0
            last_time = time()
            last_round_time = -1

            effacer_tout()
            draw_all(grid, player, ticks, playing, paused, winner)

        ev = donner_ev()
        ty = type_ev(ev)

        if ty == 'Quitte':
            break
        elif ty == 'ClicGauche':
            left_click(ev)
        elif ty == 'Touche':
            if playing and touche(ev).lower() == 'p':
                paused = not paused
                if paused:
                    buttons.clear()
                    effacer_tout()
                    draw_all(grid, player, ticks, paused, playing, winner)

        delta = time() - last_time
        last_time = time()

        if playing and not paused:
            if ty == 'ClicGauche':
                x, y = pixel_to_cell(abscisse(ev), ordonnee(ev))

                if not (0 <= x <= BOARD_WIDTH - 1 and 0 <= y <= BOARD_HEIGHT - 1):
                    continue

                if grid[y][x]:
                    continue

                grid[y][x] = player
                player *= -1

                winner, lane, direction = check_win(grid)
                if winner in (-1, 1):
                    playing = False
                else:
                    playing = can_play(grid)
                    winner = 0
                    lane = 0
                    direction = None

                if not playing:
                    player = winner

            ticks += delta

            if ty:
                buttons.clear()
                effacer_tout()
                draw_all(grid, player, ticks, playing, paused, winner)
                if not playing:
                    draw_lane(lane, direction)
            elif int(ticks) % 60 != last_round_time:
                last_round_time = int(ticks) % 60
                draw_time(ticks, paused)

        attendre(1 / FRAMERATE)

    fermer_fenetre()


if __name__ == "__main__":
    buttons = dict()
    compute_text_size()
    loop()
