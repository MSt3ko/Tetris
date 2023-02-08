import random
import time
import os
import unittest
import pygame

SHAPES = ['I', 'L', 'J', 'T', 'O', 'S', 'Z']
NON_SNAKE_SHAPES = ['I', 'L', 'J', 'T', 'O']
START_SHAPES = ['I', 'L', 'J', 'T']
POINTS = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
BLOCK_SIZE = 40
BACKGROUND_COLOR = "#3f4a4e"
BLOCK_COLOR = "#901b1b"
TEXT_COLOR = "#FFFFFF"
SCREEN_COLOR = "#1c2e4a"
MAX_TETRO = 10000
MAX_SZ = 4
MAX_NO_I = 12
DIVIDER = 1
MAX_T = 10000
WIDTH = 10
HEIGHT = 20
DAS = 1/5
AFTER_DAS = 1/40



def random_generator():
    s = []
    sz_counter = 0
    i_counter = 0
    s.append(START_SHAPES[random.randrange(0, len(START_SHAPES))])
    for i in range(MAX_TETRO):
        if sz_counter < MAX_SZ and i_counter < MAX_NO_I:
            new_shape = SHAPES[random.randrange(0, len(SHAPES))]
        elif i_counter >= MAX_NO_I:
            new_shape = 'I'
        elif sz_counter >= MAX_SZ:
            new_shape = NON_SNAKE_SHAPES[random.randrange(0, len(NON_SNAKE_SHAPES))]
        if new_shape in ['S', 'Z']:
            sz_counter += 1
        else:
            sz_counter = 0
        if new_shape != 'I':
            i_counter += 1
        else:
            i_counter = 0
        s.append(new_shape)
    return s


def draw_rect(i, j, surface, color, size=BLOCK_SIZE, divider=DIVIDER):
    pygame.draw.rect(surface, color,
                     pygame.Rect(size * (j + 1), size * (i + 1), size - divider,
                                 size - divider))


class Board:

    def __init__(self, n, m):
        self.width = m
        self.height = n
        self.field = [[None for i in range(m)] for j in range(n)]
        self.score = 0
        self.t = 0
        self.S = random_generator()
        self.active = Tetromino(self.S.pop(), self)
        self.rows_total = 0
        self.rows_current = 0
        self.level = 0
        match self.active.shape:
            case "I":
                self.active_squares = [[self.active.loc[0], self.active.loc[1] + i] for i in range(-1, 3)]
            case "O":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0] + 1, self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] + 1, self.active.loc[1] + 1]]
            case "T":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0] - 1, self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0], self.active.loc[1] - 1]]
            case "S":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] + 1, self.active.loc[1]],
                                       [self.active.loc[0] + 1, self.active.loc[1] - 1]]
            case "Z":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] - 1],
                                       [self.active.loc[0] + 1, self.active.loc[1]],
                                       [self.active.loc[0] + 1, self.active.loc[1] + 1]]
            case "L":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] - 1],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] - 1, self.active.loc[1] + 1]]
            case "J":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] - 1],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] - 1, self.active.loc[1] - 1]]
            case _:
                raise Exception("Invalid shape.")

    def progress_time(self):
        if self.game_over():
            raise Exception("GAME OVER")
        if self.check_landed():
            if not self.S:
                self.S = random_generator()
            self.active = Tetromino(self.S.pop(), self)
            for [x, y] in self.active_squares:
                self.field[x][y] = "o"
            self.delete_full_rows()
            self.update_score()
            self.set_active_squares(self.active.shape)
        else:
            self.active.loc[0] += 1
            new_active = [[i + 1, j] for [i, j] in self.active_squares]
            self.update_active_view(new_active)
        self.t += 1
        self.t %= MAX_T

        return None

    def move(self, x):
        match x:
            case "L":
                try:
                    new_active = []
                    for [row, col] in self.active_squares:
                        if col == 0 or self.field[row][col - 1] == 'o':
                            return None
                        new_active.append([row, col - 1])
                    self.active.loc[1] -= 1
                except IndexError:
                    pass
            case "R":
                try:
                    new_active = []
                    for [row, col] in self.active_squares:
                        if col == self.width - 1 or self.field[row][col + 1] == 'o':
                            return None
                        new_active.append([row, col + 1])
                    self.active.loc[1] += 1
                except IndexError:
                    pass
            case "D":
                try:
                    new_active = []
                    for [row, col] in self.active_squares:
                        if row == self.height - 1 or self.field[row + 1][col] == 'o':
                            return None
                        new_active.append([row + 1, col])
                    self.active.loc[0] += 1
                    self.update_active_view(new_active)
                except IndexError:
                    pass
            case "S":
                while self.move("D") is not None:
                    pass
                return None
        self.update_active_view(new_active)
        return True

    def update_active_view(self, new_active):
        for [i, j] in (self.active_squares + new_active):
            if [i, j] not in new_active:
                if i < 0:
                    pygame.draw.rect(screen, SCREEN_COLOR,
                                     pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                                 BLOCK_SIZE - 1))
                else:
                    pygame.draw.rect(screen, BACKGROUND_COLOR,
                                     pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                                 BLOCK_SIZE - 1))
            if [i, j] in new_active and [i, j] not in self.active_squares:
                pygame.draw.rect(screen, BLOCK_COLOR,
                                 pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                             BLOCK_SIZE - 1))
            self.active_squares = new_active

    def rotate(self, direction):
        if self.active.shape == 'O':
            return None
        new_active = []
        if direction == "cw":
            for [x, y] in self.active_squares:
                x2 = x - self.active.loc[0]
                y2 = y - self.active.loc[1]
                new_active.append([y2 + self.active.loc[0], -x2 + self.active.loc[1]])

        elif direction == "ccw":
            for [x, y] in self.active_squares:
                x2 = x - self.active.loc[0]
                y2 = y - self.active.loc[1]
                new_active.append([-y2 + self.active.loc[0], x2 + self.active.loc[1]])
        else:
            raise Exception("Invalid direction. Valid options cw and ccw.")
        # print("old: ", self.active_squares, " \n new: ", new_active)
        # Need to check validity of coordinates - don't allow rotation if it would cause overlap with existing bricks
        # or edges of the map.
        # Possible speedup if this is checked earlier, when they are added to the list. This approach is clearer so it
        # stays for now.
        for [x, y] in new_active:
            if x < 0:
                self.move("D")
                self.rotate(direction)
                pygame.draw.rect(screen, SCREEN_COLOR,
                                 pygame.Rect(0, 0, BLOCK_SIZE*WIDTH,
                                             BLOCK_SIZE))
            if x >= self.height:
                return None
            if y < 0 or y >= self.width:
                return None
            if self.field[x][y] == 'o' and [x, y] not in self.active_squares:
                return None
        self.update_active_view(new_active)
        return None

    def check_landed(self):
        for [x, y] in self.active_squares:
            if x == self.height - 1 or self.field[x + 1][y] == 'o':
                return True
        return False

    def delete_full_rows(self):
        rows_deleted = 0
        for row in range(self.height):
            if sum(x is not None for x in self.field[row]) == self.width:
                self.gravity(row)
                rows_deleted += 1
        self.score += max(self.level, 1) * POINTS[rows_deleted]
        self.rows_current += rows_deleted
        if self.rows_current >= min(self.level * 10 + 10, max(100, self.level * 10 - 50)):
            self.level += 1
        #lvl = font.render("LVL" + str(self.level), True, TEXT_COLOR)
        #screen.blit(lvl, (10, 30))
        return None

    def gravity(self, deleted_row):
        for row in range(deleted_row, 0, -1):
            for col in range(self.width):
                draw_rect(row, col, screen, BACKGROUND_COLOR)
                if self.field[row - 1][col] == 'o' and self.field[row][col] is None:
                    draw_rect(row, col, screen, BLOCK_COLOR)
                    draw_rect(row - 1, col, screen, BACKGROUND_COLOR)
            self.field[row] = self.field[row - 1]
        self.field[0] = [None for i in range(self.width)]

    def game_over(self):
        for i in range(self.width // 2 - 2, self.width // 2 + 2):
            if self.field[0][i] == 'o':
                return True
        return False

    def __repr__(self):
        return self.field

    def __str__(self):
        board = [" " + "-" * self.width + " "]
        for row in range(self.height):
            curr_row = ["|"]
            for col in range(self.width):
                if self.field[row][col] == 'o' or [row, col] in self.active_squares:
                    curr_row.append("o")
                else:
                    curr_row.append(" ")
            curr_row.append("|")
            board.append(''.join(curr_row))
        board.append(" " + "-" * self.width + " ")
        return '\n'.join(board) + '\n' + "LVL" + str(self.level) + ", " + str(self.score) + "PTS"

    def set_active_squares(self, shape):
        match shape:
            case "I":
                self.active_squares = [[self.active.loc[0], self.active.loc[1] + i] for i in range(-1, 3)]
            case "O":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0] + 1, self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] + 1, self.active.loc[1] + 1]]
            case "T":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0] - 1, self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0], self.active.loc[1] - 1]]
            case "S":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] + 1, self.active.loc[1]],
                                       [self.active.loc[0] + 1, self.active.loc[1] - 1]]
            case "Z":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] - 1],
                                       [self.active.loc[0] + 1, self.active.loc[1]],
                                       [self.active.loc[0] + 1, self.active.loc[1] + 1]]
            case "L":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] - 1],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] - 1, self.active.loc[1] + 1]]
            case "J":
                self.active_squares = [[self.active.loc[0], self.active.loc[1]],
                                       [self.active.loc[0], self.active.loc[1] - 1],
                                       [self.active.loc[0], self.active.loc[1] + 1],
                                       [self.active.loc[0] - 1, self.active.loc[1] - 1]]

    def update_screen(self, block_size=BLOCK_SIZE):
        pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(block_size, block_size, self.width * block_size,
                                                               self.height * block_size))
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i][j] is not None or [i, j] in self.active_squares:
                    pygame.draw.rect(screen, BLOCK_COLOR,
                                     pygame.Rect(block_size * (j + 1), block_size * (i + 1), block_size - 1,
                                                 block_size - 1))
                pygame.display.update()

    def update_score(self, block_size=BLOCK_SIZE):

        pygame.draw.rect(screen, SCREEN_COLOR, pygame.Rect(block_size,
                                                           block_size * (self.height + 2),
                                                           self.width * block_size,
                                                           3 * block_size))
        score_font = pygame.font.SysFont("Montserrat", block_size//2, bold=True)
        score_text = score_font.render("PTS: ", True, TEXT_COLOR)
        screen.blit(score_text, (block_size * (2 * self.width // 3 + 2), block_size * (self.height + 2)))
        pygame.display.update()

        score_value = score_font.render(str(self.score), True, TEXT_COLOR)
        screen.blit(score_value, (block_size * (2 * self.width // 3 + 3), block_size * (self.height + 2)))
        pygame.display.update()



        lvl_value = score_font.render(str(self.level), True, TEXT_COLOR)
        screen.blit(lvl_value, (block_size * (self.width // 3 + 3), block_size * (self.height + 2)))
        pygame.display.update()

        next_text = score_font.render("Next: ", True, TEXT_COLOR)
        screen.blit(next_text, (block_size, block_size * (self.height + 2)))
        pygame.display.update()

        lvl_text = score_font.render("LVL:", True, TEXT_COLOR)
        screen.blit(lvl_text, (block_size * (self.width // 3 + 2), block_size * (self.height + 2)))
        pygame.display.update()

        pygame.draw.rect(screen, SCREEN_COLOR, pygame.Rect(block_size * 2,
                                                           block_size * (self.height + 1.5),
                                                           2 * block_size,
                                                           2 * block_size))
        self.show_brick(block_size * 2, int(block_size * (self.height + 1.5)), block_size//2)



        pass


    def show_brick(self, left_offset, top_offset, size):
        match self.S[-1]:
            case "I":
                for offset in range(4):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))

            case "O":
                for offset in range(2):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
                for offset in range(2):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
            case "T":
                pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + size,
                                                                  top_offset,
                                                                  size - DIVIDER,
                                                                  size - DIVIDER))
                for offset in range(3):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
            case "S":
                for offset in range(2):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + (offset + 1) * size,
                                                                      top_offset,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
                for offset in range(2):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
            case "Z":
                for offset in range(2):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
                for offset in range(2):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + (offset + 1) * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
            case "L":
                pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + 2 * size,
                                                                  top_offset,
                                                                  size - DIVIDER,
                                                                  size - DIVIDER))
                for offset in range(3):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))
            case "J":
                pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset,
                                                                  top_offset,
                                                                  size - DIVIDER,
                                                                  size - DIVIDER))
                for offset in range(3):
                    pygame.draw.rect(screen, BLOCK_COLOR, pygame.Rect(left_offset + offset * size,
                                                                      top_offset + size,
                                                                      size - DIVIDER,
                                                                      size - DIVIDER))


# Tetrominos don't exist until they are on the board. The stack of "next brick" is just symbols.
class Tetromino:

    def __init__(self):
        self.shape = SHAPES[random.randrange(0, 7)]
        self.loc = [0, self.width // 2]
        self.landed = False

    def __init__(self, shape, board):
        self.shape = shape
        match shape:
            case "I":
                self.loc = [0, board.width // 2 - 1]
            case "O":
                self.loc = [0, board.width // 2 - 1]
            case "S":
                self.loc = [0, board.width // 2 - 1]
            case "Z":
                self.loc = [0, board.width // 2 - 1]
            case "T":
                self.loc = [1, board.width // 2 - 1]
            case "J":
                self.loc = [1, board.width // 2 - 1]
            case "L":
                self.loc = [1, board.width // 2 - 1]

    def rotate(self):
        pass

    def drop(self):
        pass

    def move(self, direction):
        pass


def clear():
    os.system('cls')


class TestTetris(unittest.TestCase):

    def test_rotation(self):
        pass


def test_time():
    game = Board(10, 10)
    for i in range(50):
        print(game)
        game.rotate("cw")
        game.progress_time()
        time.sleep(0.4)
        clear()


def test_drawing():
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Tetris")
    run = True
    screen.fill(SCREEN_COLOR)
    font = pygame.font.SysFont("Calibri", 70, bold=True)
    label = font.render("HA!", True, TEXT_COLOR)
    screen.blit(label, (10, 30))
    pygame.display.update()
    BLOCK_SIZE = 5
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    raise Exception("QUIT GAME")
            pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(BLOCK_SIZE, BLOCK_SIZE, 10 * BLOCK_SIZE,
                                                                   10 * BLOCK_SIZE))
            pygame.display.update()


def play():
    pygame.init()
    done = False
    clock = pygame.time.Clock()
    fps = 25
    counter = 0
    game = Board(HEIGHT, WIDTH)

    screen.fill(SCREEN_COLOR)

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1),
                                                                   BLOCK_SIZE - DIVIDER,
                                                                   BLOCK_SIZE - DIVIDER))

    pygame.display.update()
    game.update_score()
    landed_counter = 1
    while True:
        counter += 1
        counter %= 100000
        landed_counter %= 100000
        if counter % (fps // (game.level + 1) // 2) == 0 and not game.check_landed():
            game.progress_time()
            first_landed = True
        if game.check_landed():
            landed_counter += 1
            first_landed = False
        if landed_counter % (fps // (game.level + 1) // 4) == 0:
            game.progress_time()
            first_landed = True
            landed_counter = 1
        for event in pygame.event.get():
            pygame.key.set_repeat(int(DAS * 1000), int(AFTER_DAS * 1000))
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate("cw")
                if event.key == pygame.K_LEFT:
                    # print("LEFT REGISTERED")
                    game.move("L")
                if event.key == pygame.K_RIGHT:
                    game.move("R")
                if event.key == pygame.K_DOWN:
                    game.move("D")
                if event.key == pygame.K_SPACE:
                    game.move("S")
                    break
                pygame.key.set_repeat(int(DAS * 1000), int(AFTER_DAS * 1000))
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)
                if event.key == pygame.K_q:
                    raise Exception("QUIT GAME")


        print(game)

        for i in range(game.height):
            for j in range(game.width):
                if game.field[i][j] is not None or [i, j] in game.active_squares:
                    pygame.draw.rect(screen, BLOCK_COLOR,
                                     pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                                 BLOCK_SIZE - 1))
                pygame.display.update()



# play()


if __name__ == "__main__":
    pygame.font.init()
    screen_w = (WIDTH + 2) * BLOCK_SIZE
    screen_h = (HEIGHT + 4) * BLOCK_SIZE
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Tetris")
    run = True
    screen.fill(SCREEN_COLOR)
    font = pygame.font.SysFont("Montserrat", BLOCK_SIZE, bold=False)
    label = font.render("Press any key to play", True, TEXT_COLOR)
    label_rect = label.get_rect(center=(screen_w / 2, screen_h / 2))
    screen.blit(label, label_rect)
    pygame.display.update()
    while run:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                run = False
            if event_.type == pygame.KEYDOWN:
                play()
    pygame.quit()
