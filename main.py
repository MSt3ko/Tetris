import random
import collections
import time
import os
import sys
import unittest
import pygame
import math

SHAPES = ['I', 'L', 'J', 'O', 'S', 'Z', 'T']
POINTS = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
BLOCK_SIZE = 40
BACKGROUND_COLOR = "#3f4a4e"
BLOCK_COLOR = "#901b1b"
TEXT_COLOR = "#FFFFFF"
SCREEN_COLOR = "#1c2e4a"


class Board:

    def __init__(self, n, m):
        self.width = m
        self.height = n
        self.field = [[None for i in range(m)] for j in range(n)]
        self.score = 0
        self.t = 0
        self.S = [SHAPES[random.randrange(0, 7)] for i in range(10000)]
        self.active = Tetromino(self.S.pop(), self)
        self.rows_total = 0
        self.rows_current = 0
        self.level = 0
        # self.filled_squares = collections.defaultdict(list)
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
            return None
        if Board.check_landed(self):
            self.active = Tetromino(self.S.pop(), self)
            for [x, y] in self.active_squares:
                # self.filled_squares[x].append(y)  ---- changing filled_squares to field
                self.field[x][y] = "o"
                # print("adding some filled squares:", self.filled_squares)
            self.delete_full_rows()
            self.set_active_squares(self.active.shape)
            # self.update_screen(BLOCK_SIZE) unnecessary, move to delete_full_rows
        else:
            self.active.loc[0] += 1
            new_active = [[i + 1, j] for [i, j] in self.active_squares]
            # for i in range(len(self.active_squares)):
            #    self.active_squares[i][0] += 1
            self.update_active_view(new_active)
        self.t += 1
        self.t %= 100000

        return None

    def move(self, x):
        # Try-except obsolete
        match x:
            case "L":
                # print("BEFORE", self.active_squares)
                try:
                    new_active = []
                    for [row, col] in self.active_squares:
                        if col == 0 or self.field[row][col - 1] == 'o':
                            return None
                        new_active.append([row, col - 1])
                        # print("success")
                    self.active.loc[1] -= 1
                except IndexError:
                    pass
                # print("AFTER: ", self.active_squares)
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
                    # return None
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
                pygame.draw.rect(screen, BACKGROUND_COLOR,
                                 pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                             BLOCK_SIZE - 1))
            if [i, j] in new_active and [i, j] not in self.active_squares:
                pygame.draw.rect(screen, BLOCK_COLOR,
                                 pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                             BLOCK_SIZE - 1))
            self.active_squares = new_active

    def rotate(self, direction):
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
            if x >= self.height:
                return None
            if y < 0 or y >= self.width:
                return None
            # if y in self.filled_squares[x]:
            if self.field[x][y] == 'o' and [x, y] not in self.active_squares:
                # print("I read the field wrong")
                return None
        # print(self.active_squares)
        self.update_active_view(new_active)
        # print(new_active)
        # print(self.active_squares)
        return None

    def check_landed(self):
        for [x, y] in self.active_squares:
            # if y in self.filled_squares[x+1] or x == self.height-1:
            if x == self.height - 1 or self.field[x + 1][y] == 'o':
                return True
        return False

    def delete_full_rows(self):
        # for row in self.filled_squares:
        #    if len(self.filled_squares[row]) == self.width:
        #        self.filled_squares[row].clear()
        #        self.gravity(row)
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
                self.draw_rect(row, col, screen, BACKGROUND_COLOR)
                if self.field[row - 1][col] == 'o' and self.field[row][col] is None:
                    self.draw_rect(row, col, screen, BLOCK_COLOR)
                    self.draw_rect(row - 1, col, screen, BACKGROUND_COLOR)
            self.field[row] = self.field[row - 1]
        self.field[0] = [None for i in range(self.width)]

    def game_over(self):
        for i in range(self.width // 2 - 2, self.width // 2 + 2):
            if self.field[0][i] == 'o':
                return True
        return False

    def __repr__(self):
        return self.field

    # Implement printing. Note field is not really used, only filled_fields.
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

    def update_screen(self, BLOCK_SIZE):
        pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(BLOCK_SIZE, BLOCK_SIZE, self.width * BLOCK_SIZE,
                                                               self.height * BLOCK_SIZE))
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i][j] is not None or [i, j] in self.active_squares:
                    pygame.draw.rect(screen, BLOCK_COLOR,
                                     pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                                 BLOCK_SIZE - 1))
                pygame.display.update()

    def draw_rect(self, i, j, surface, color):
        pygame.draw.rect(surface, color,
                         pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                     BLOCK_SIZE - 1))


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
    game = Board(height, width)
    pressing_down = False

    screen.fill(SCREEN_COLOR)

    pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(BLOCK_SIZE, BLOCK_SIZE, game.width * BLOCK_SIZE,
                                                           game.height * BLOCK_SIZE))
    pygame.display.update()
    while True:
        counter += 1
        counter %= 100000
        if counter % (fps // 2) == 0:
            game.progress_time()
        for event in pygame.event.get():
            # print("EVENT LOOP ENTERED")
            if event.type == pygame.QUIT:
                # print("I QUIT")
                break
            if event.type == pygame.KEYDOWN:
                # print("KEYDOWN REGISTERED")
                if event.key == pygame.K_UP:
                    # print("UP REGISTERED")
                    game.rotate("cw")
                if event.key == pygame.K_LEFT:
                    # print("LEFT REGISTERED")
                    game.move("L")
                if event.key == pygame.K_RIGHT:
                    # print("RIGHT REGISTERED")
                    game.move("R")
                if event.key == pygame.K_DOWN:
                    # print("DOWN REGISTERED")
                    game.move("D")
                if event.key == pygame.K_SPACE:
                    # print("SPACE REGISTERED")
                    game.move("S")
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)
                if event.key == pygame.K_q:
                    raise Exception("QUIT GAME")
        time.sleep(0.05)
        print(game)

        for i in range(game.height):
            for j in range(game.width):
                if game.field[i][j] is not None or [i, j] in game.active_squares:
                    pygame.draw.rect(screen, BLOCK_COLOR,
                                     pygame.Rect(BLOCK_SIZE * (j + 1), BLOCK_SIZE * (i + 1), BLOCK_SIZE - 1,
                                                 BLOCK_SIZE - 1))
                pygame.display.update()
                # pygame.draw.rect(screen, '#B2BEB5',
                #                 [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                # if game.field[i][j] > 0:
                #    pygame.draw.rect(screen, shapeColors[game.field[i][j]],
                #                     [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2,
                #                      game.zoom - 1])


# play()


if __name__ == "__main__":
    width = 10
    height = 15
    # test_time()
    pygame.font.init()
    screen = pygame.display.set_mode(((width + 2) * BLOCK_SIZE, (height + 4) * BLOCK_SIZE))
    pygame.display.set_caption("Tetris")
    run = True
    screen.fill(SCREEN_COLOR)
    font = pygame.font.SysFont("Montserrat", 40, bold=False)
    label = font.render("Press any key to play", True, TEXT_COLOR)
    screen.blit(label, (10, 30))
    pygame.display.update()
    while run:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                run = False
            if event_.type == pygame.KEYDOWN:
                play()
    pygame.quit()

# cover the outdated blocks with the background color, and then redraw the active blocks.
# this way you don't have to refresh everything.
