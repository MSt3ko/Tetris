import pygame

FONT = "Montserrat"
GREETING = "Press any key to play"
BLOCK_SIZE = 40
BACKGROUND_COLOR = "#000000"
BLOCK_COLOR = "#901b1b"
TEXT_COLOR = "#FFFFFF"
SCREEN_COLOR = "#2a2a29"
COLORS = {"J": "#3a33e6", "Z": "#901b1b", "T": "#871f84", "S": "#008313", "L": "#C06002", "I": "#02b5c0",
          "O": "#Bcc002"}
GHOST_COLORS = {"J": "#2b2968", "Z": "#5e0809", "T": "#360f35", "S": "#0f2208", "L": "#49330f", "I": "#0F4948",
                "O": "#5a5e08"}
DIVIDER = 1
PTS = "PTS: "
NEXT = "Next: "
LVL = "LVL: "
GAME_OVER = "GAME OVER, press Esc to exit."


def square(game, coord, surface, color=None, size=BLOCK_SIZE, div=DIVIDER):
    """Draw a square."""
    if not color:
        color = COLORS[game.active.shape]
    pygame.draw.rect(surface, color,
                     pygame.Rect(size * (coord[1] + 1), size * (coord[0] + 1), size - div,
                                 size - div))
    return None


def square_fancy(game, coord, surface, shape, ghost=False, size=BLOCK_SIZE, div=DIVIDER):
    """We can't simply draw a square with a color - shapes have a predetermined color set."""
    pass


def piece(game, surface, tetromino, ghost=False):
    """draw a tetromino"""
    if ghost:
        colors = GHOST_COLORS
    else:
        colors = COLORS
    for (row, col) in tetromino.fields:
        square(game, (row, col), surface, colors[game.active.shape])
    return None


def update_row(game, row_to_fill, surface):
    """redraw the portions of a field when a row is deleted"""
    for col in range(game.width):
        square(game, (row_to_fill, col), surface, color=BACKGROUND_COLOR)
        if game.field[row_to_fill - 1][col] is not None and game.field[row_to_fill][col] is None:
            square(game, (row_to_fill, col), surface, color=COLORS[game.field[row_to_fill - 1][col]])
            square(game, (row_to_fill - 1, col), surface, color=BACKGROUND_COLOR)
    return None


def update_piece(game, surface, new_piece, ghost=False):
    if not ghost:
        old_piece = game.active
        colors = COLORS
    else:
        old_piece = game.ghost
        colors = GHOST_COLORS
    try:
        new_piece_fields = new_piece.fields
    except AttributeError:
        new_piece_fields = new_piece
    """redraw the needed squares to move the falling/rotating piece"""
    for (row, col) in (old_piece.fields + new_piece_fields):
        if (row, col) not in new_piece_fields:
            if row < 0:
                square(game, (row, col), surface, color=SCREEN_COLOR)
            else:
                square(game, (row, col), surface, color=BACKGROUND_COLOR)
        if (row, col) in new_piece_fields and (row, col) not in game.active.fields:
            square(game, (row, col), surface, color=colors[game.active.shape])


def update_score(game, screen, block_size=BLOCK_SIZE):

    pygame.draw.rect(screen, SCREEN_COLOR, pygame.Rect(block_size,
                                                       block_size * (game.height + 2),
                                                       game.width * block_size,
                                                       3 * block_size))
    score_font = pygame.font.SysFont(FONT, block_size // 2, bold=True)
    score_text = score_font.render(PTS, True, TEXT_COLOR)
    screen.blit(score_text, (block_size * (2 * game.width // 3 + 2), block_size * (game.height + 2)))
    pygame.display.update()

    score_value = score_font.render(str(game.score), True, TEXT_COLOR)
    screen.blit(score_value, (block_size * (2 * game.width // 3 + 3), block_size * (game.height + 2)))
    pygame.display.update()

    lvl_value = score_font.render(str(game.level+1), True, TEXT_COLOR)
    screen.blit(lvl_value, (block_size * (game.width // 3 + 3), block_size * (game.height + 2)))
    pygame.display.update()

    next_text = score_font.render(NEXT, True, TEXT_COLOR)
    screen.blit(next_text, (block_size, block_size * (game.height + 2)))
    pygame.display.update()

    lvl_text = score_font.render(LVL, True, TEXT_COLOR)
    screen.blit(lvl_text, (block_size * (game.width // 3 + 2), block_size * (game.height + 2)))
    pygame.display.update()

    pygame.draw.rect(screen, SCREEN_COLOR, pygame.Rect(block_size * 2,
                                                       block_size * (game.height + 1.5),
                                                       2 * block_size,
                                                       2 * block_size))
    show_brick(game, block_size * 2, int(block_size * (game.height + 1.5)), block_size // 2, screen)
    return None



def show_brick(game, left_offset, top_offset, size, screen):
    match game.S[-1]:
        case "I":
            for offset in range(4):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))

        case "O":
            for offset in range(2):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
            for offset in range(2):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
        case "T":
            pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + size,
                                                                     top_offset,
                                                                     size - DIVIDER,
                                                                     size - DIVIDER))
            for offset in range(3):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
        case "S":
            for offset in range(2):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + (offset + 1) * size,
                                                                         top_offset,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
            for offset in range(2):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
        case "Z":
            for offset in range(2):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
            for offset in range(2):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + (offset + 1) * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
        case "L":
            pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + 2 * size,
                                                                     top_offset,
                                                                     size - DIVIDER,
                                                                     size - DIVIDER))
            for offset in range(3):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
        case "J":
            pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset,
                                                                     top_offset,
                                                                     size - DIVIDER,
                                                                     size - DIVIDER))
            for offset in range(3):
                pygame.draw.rect(screen, COLORS[game.S[-1]], pygame.Rect(left_offset + offset * size,
                                                                         top_offset + size,
                                                                         size - DIVIDER,
                                                                         size - DIVIDER))
    return None


def field(screen, game):
    """initialize game"""

    screen.fill(SCREEN_COLOR)

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1),
                                                                   BLOCK_SIZE - DIVIDER,
                                                                   BLOCK_SIZE - DIVIDER))

    piece(game, screen, game.ghost_brick(), ghost=True)
    pygame.display.update()
    update_score(game, screen)


def welcome_screen(screen, width, height):
    """draw the welcome screen"""
    screen.fill(SCREEN_COLOR)
    font = pygame.font.SysFont(FONT, BLOCK_SIZE, bold=False)
    label = font.render(GREETING, True, TEXT_COLOR)
    label_rect = label.get_rect(center=(width / 2, height / 2))
    screen.blit(label, label_rect)
    pygame.display.update()


def game_over_screen(screen, width, height, game, block_size=BLOCK_SIZE):
    screen.fill(SCREEN_COLOR)
    font = pygame.font.SysFont(FONT, BLOCK_SIZE, bold=False)
    label = font.render(GAME_OVER, True, TEXT_COLOR)
    label_rect = label.get_rect(center=(width / 2, height / 2))
    screen.blit(label, label_rect)


    score_value = font.render(LVL + " " + str(game.level + 1) + "    " + PTS + " " + str(game.score), True, TEXT_COLOR)
    score_rect = score_value.get_rect(center=(width / 2, height * 2 / 3))
    screen.blit(score_value, score_rect)

    pygame.display.update()


def event_loop_update(game, screen):
    for i in range(game.height):
        for j in range(game.width):
            if game.field[i][j] is not None:
                # pygame.draw.rect(screen, COLORS[game.field[i][j]],
                #                 pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                #                             BLOCK_SIZE - 1))
                square(game, (i, j), screen, COLORS[game.field[i][j]])
            if (i, j) in game.active.fields:
                # pygame.draw.rect(screen, COLORS[game.active.shape],
                #                 pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                #                             BLOCK_SIZE - 1))
                square(game, (i, j), screen, COLORS[game.active.shape])
            pygame.display.update()
