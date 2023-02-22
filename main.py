import random
import time
import pygame
import drawTetris
import copy

SHAPES = ('I', 'L', 'J', 'T', 'O', 'S', 'Z')
NON_SNAKE_SHAPES = ('I', 'L', 'J', 'T', 'O')
START_SHAPES = ('I', 'L', 'J', 'T')
POINTS = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
MAX_TETRO = 70000 // 7
MAX_T = 10000
WIDTH = 10
HEIGHT = 20
DAS = 1 / 5
AFTER_DAS = 1 / 40
LOCK_DELAY = 0.5
CONTROLS = {"left": {pygame.K_LEFT}, "right": {pygame.K_RIGHT}, "down": {pygame.K_DOWN},
            "rotate_cw": {pygame.K_x, pygame.K_UP}, "rotate_ccw": {pygame.K_z},
            "drop": {pygame.K_SPACE}}
SPACE_DELAY = 0.5


class Board:
    def __init__(self, n, m):
        self.width = m
        self.height = n
        self.field = [[None for i in range(m)] for j in range(n)]
        self.score = 0
        self.t = 0
        self.S = self.random_generator()
        self.active = Tetromino(self.S.pop(), self)
        self.ghost = self.ghost_brick()
        self.rows_total = 0
        self.rows_current = 0
        self.level = 0

    def progress_time(self):
        if self.check_landed():
            # if piece stack is empty, regenerate
            if not self.S:
                self.S = self.random_generator()

            # shape name is used to track the location in the grid - helps with color and ASCII version
            for (x, y) in self.active.fields:
                self.field[x][y] = self.active.shape
            self.delete_full_rows()
            self.active = Tetromino(self.S.pop(), self)
            drawTetris.update_score(self, SCREEN)
            drawTetris.piece(self, SCREEN, self.active, ghost=False)
            self.ghost = self.ghost_brick()
            drawTetris.piece(self, SCREEN, self.ghost, ghost=True)
        else:
            self.move("D")
        self.t += 1
        self.t %= MAX_T
        return None

    def delete_full_rows(self):
        rows_deleted = 0
        for row in range(self.height):
            # count not-None values in row, if equal to width, delete
            if sum(x is not None for x in self.field[row]) == self.width:
                self.gravity(row)
                rows_deleted += 1
        self.score += (self.level + 1) * POINTS[rows_deleted]
        self.rows_current += rows_deleted
        if self.rows_current >= self.next_lvl_rows(self.level):
            print(self.level)
            self.level += 1
        return None

    @staticmethod
    def next_lvl_rows(lvl):
        """One of the official options for number of rows needed for next level."""
        return (lvl + 1) * 10

    def gravity(self, deleted_row):
        """Make the bricks above the deleted rows fall into place."""
        for row in range(deleted_row, 0, -1):
            drawTetris.update_row(self, row, SCREEN)
            self.field[row] = self.field[row - 1]
        self.field[0] = [None for i in range(self.width)]

    def check_landed(self):
        for (x, y) in self.active.fields:
            if x == self.height - 1 or self.field[x + 1][y] is not None:
                return True
        return False

    def clear_rows(self):
        pass

    @staticmethod
    def random_generator(shapes=SHAPES, start_shapes=START_SHAPES, max_tetro=MAX_TETRO):
        """Bag based generator of shapes, as in most official versions."""
        s = [start_shapes[random.randrange(0, len(start_shapes))]]
        while len(s) < max_tetro:
            bag = list(shapes)
            while len(bag) > 0:
                new = bag[random.randrange(0, len(bag))]
                s.append(new)
                bag.remove(new)
        return s

    def ghost_brick(self, fields=None):
        """Creates a copy of the active brick under it, on top of the stack."""
        if not fields:
            drop_squares = copy.deepcopy(self.active.fields)
        if fields:
            drop_squares = copy.deepcopy(fields)
        temp_squares = []
        loc = copy.deepcopy(self.active.loc)
        while True:
            # noinspection PyUnboundLocalVariable
            for (i, j) in drop_squares:
                if i + 1 >= self.height or self.field[i + 1][j] is not None:
                    return Tetromino(self.active.shape, self, fields=drop_squares, loc=loc)
                else:
                    temp_squares.append((i + 1, j))
            loc[0] += 1
            drop_squares = copy.deepcopy(temp_squares)
            temp_squares = []

    def move(self, direction):
        """Move tetromino in given direction."""
        new_active = []
        match direction:
            case "L":
                try:
                    for (row, col) in self.active.fields:
                        if col == 0 or self.field[row][col - 1] is not None:
                            return None
                        new_active.append((row, col - 1))
                    self.active.loc[1] -= 1
                except IndexError:
                    pass
            case "R":
                try:
                    for (row, col) in self.active.fields:
                        if col == self.width - 1 or self.field[row][col + 1] is not None:
                            return None
                        new_active.append((row, col + 1))
                    self.active.loc[1] += 1
                except IndexError:
                    pass
            case "D":
                try:
                    for (row, col) in self.active.fields:
                        if row == self.height - 1 or self.field[row + 1][col] is not None:
                            return None
                        new_active.append((row + 1, col))
                    self.active.loc[0] += 1
                except IndexError:
                    pass
            case "S":
                while self.move("D"):
                    pass
                return None
            case _:
                raise Exception("Invalid direction.")

        new_active_piece = Tetromino(self.active.shape, self,
                                     fields=new_active, loc=self.active.loc)
        drawTetris.update_piece(self, SCREEN, new_active_piece)
        self.active = new_active_piece
        new_ghost = self.ghost_brick()
        drawTetris.update_piece(self, SCREEN, new_ghost, ghost=True)
        self.ghost = new_ghost
        return True

    def rotate(self, direction):
        """Rotate the active Tetromino clockwise or counter-clockwise."""
        if self.active.shape == 'O':
            return None
        new_active = []
        if direction == "cw":
            for (x, y) in self.active.fields:
                x2 = x - self.active.loc[0]
                y2 = y - self.active.loc[1]
                new_active.append((y2 + self.active.loc[0], -x2 + self.active.loc[1]))

        elif direction == "ccw":
            for (x, y) in self.active.fields:
                x2 = x - self.active.loc[0]
                y2 = y - self.active.loc[1]
                new_active.append((-y2 + self.active.loc[0], x2 + self.active.loc[1]))
        else:
            raise Exception("Invalid direction. Valid options cw and ccw.")

        kickback = self.kickback(new_active)
        if kickback:
            new_active = kickback
        else:
            return None

        new_active_piece = Tetromino(self.active.shape, self,
                                     fields=new_active, loc=self.active.loc)
        drawTetris.update_piece(self, SCREEN, new_active_piece)
        self.active = new_active_piece
        new_ghost = self.ghost_brick()
        drawTetris.update_piece(self, SCREEN, new_ghost, ghost=True)
        self.ghost = new_ghost
        return None

    def kickback(self, ideal_rot):
        """Even if a rotation is invalid,
        sometimes we want to move the brick automatically for responsiveness."""

        # If correct, don't change
        if self.check_valid(ideal_rot):
            return ideal_rot

        # Else, try moving right, then left, then up and down
        else:

            right = [(i, j + 1) for (i, j) in ideal_rot]
            if self.check_valid(right):
                self.active.loc[1] += 1
                return right

            left = [(i, j - 1) for (i, j) in ideal_rot]
            if self.check_valid(left):
                self.active.loc[1] -= 1
                return left

            down = [(i + 1, j) for (i, j) in ideal_rot]
            if self.check_valid(down):
                self.active.loc[0] += 1
                return down

            up = [(i - 1, j) for (i, j) in ideal_rot]
            if self.check_valid(up):
                self.active.loc[0] -= 1
                return up

            # The I shape sometimes needs to be moved 2 places for natural kickback.
            if self.active.shape == "I":

                right2 = [(i, j + 2) for (i, j) in ideal_rot]
                if self.check_valid(right2):
                    self.active.loc[1] += 2
                    return right2

                left2 = [(i, j - 2) for (i, j) in ideal_rot]
                if self.check_valid(left2):
                    self.active.loc[1] -= 2
                    return left2

                down2 = [(i + 2, j) for (i, j) in ideal_rot]
                if self.check_valid(down2):
                    self.active.loc[0] += 2
                    return down2

                up2 = [(i - 2, j) for (i, j) in ideal_rot]
                if self.check_valid(up2):
                    self.active.loc[0] -= 2
                    return up2

            return None

    def check_valid(self, fields):
        """Check if a potential tetromino position overlaps
        with any occupied spaces or falls outside of the grid"""
        for (i, j) in fields:
            if (i < 0) or (i >= self.height) or (j < 0) or (j >= self.width) or (self.field[i][j] is not None):
                return False
        return True

    def __str__(self):
        """This representation also enables an ASCII version of the game."""
        board = [" " + "-" * self.width + " "]
        for row in range(self.height):
            curr_row = ["|"]
            for col in range(self.width):
                if self.field[row][col] is not None:
                    curr_row.append(self.field[row][col])
                elif (row, col) in self.active.fields:
                    curr_row.append(self.active.shape)
                else:
                    curr_row.append(" ")
            curr_row.append("|")
            board.append(''.join(curr_row))
        board.append(" " + "-" * self.width + " ")
        return '\n'.join(board) + '\n' + "LVL" + str(self.level) \
               + ", " + str(self.score) + "PTS"

    @staticmethod
    def time_to_drop(lvl):
        """How much time passes between tetromino falling 1 space, per level."""
        return (0.8 - lvl * 0.007) ** lvl

    def all_options(self):
        """Return all possible options where a piece can be dropped.
        First implementation should be simple, not considering overhangs, T-spins etc,
        just dropping any rotation of piece from any position on top."""
        while self.move("L"):
            pass
        games = []
        current_game = copy.deepcopy(self)
        start_brick = current_game.active
        for i in range(4):
            current_game.move("S")
            games.append(current_game)
            current_game = copy.deepcopy(self)
            while current_game.move("R"):
                self.move("R")
                current_game.move("S")
                games.append(current_game)
                current_game = copy.deepcopy(self)
            self.rotate("cw")
            current_game.rotate("cw")

    def coastline_length(self):
        """Calculate the length of all the sides of bricks and the grid.
        Potential metric for grid cleanness."""
        coast_len = 0
        for (row, col) in self.field:
            if self.field[row][col] is not None:
                try:
                    if self.field[row - 1][col] is None:
                        coast_len += 1
                except IndexError:
                    pass
                try:
                    if self.field[row][col - 1] is None:
                        coast_len += 1
                except IndexError:
                    pass
                try:
                    if self.field[row][col + 1] is None:
                        coast_len += 1
                except IndexError:
                    pass
                try:
                    if self.field[row + 1][col] is None:
                        coast_len += 1
                except IndexError:
                    pass
            else:
                if col == 0 or col == self.width - 1:
                    coast_len += 1
        return coast_len

    def max_height(self):
        """Height of the tallest column in the grid."""
        for row in range(self.height):
            for col in range(self.width):
                if self.field[row][col] is not None:
                    return self.height - row
        return 0

    def count_deep_valleys(self):
        """Count valleys of depth >= 3, where I-shape tetromino is needed to fill them.
        More than 1 is unwanted."""
        previous_row_height = None
        current_row_height = None
        deep_valleys = 0
        for col in range(self.width):
            for row in range(self.height):
                if self.field[row][col] is not None:
                    if previous_row_height is None:
                        previous_row_height = self.height - row
                        break
                    else:
                        current_row_height = self.height - row
                    if abs(current_row_height - previous_row_height) >= 3:
                        deep_valleys += 1
                    previous_row_height = current_row_height
                    break
        return deep_valleys

    def count_holes(self):
        """First version counts overhangs as holes as well, they are both to be avoided."""
        holes = 0
        for (i, j) in self.field:
            try:
                if self.field[i][j] is None and self.field[i - 1][j] is not None:
                    holes += 1
            except IndexError:
                pass
        return holes


class Tetromino:

    def __init__(self, shape, board, fields=None, loc=None):
        """Sets spawning point and rotation center of a tetromino.
        If the spawn point is occupied, game over"""
        self.shape = shape
        self.fields = fields
        if not loc:
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
        else:
            self.loc = loc
        if not self.fields:
            match self.shape:
                case "I":
                    self.fields = [[self.loc[0], self.loc[1] + i] for i in range(-1, 3)]
                case "O":
                    self.fields = [[self.loc[0], self.loc[1]],
                                   [self.loc[0] + 1, self.loc[1]],
                                   [self.loc[0], self.loc[1] + 1],
                                   [self.loc[0] + 1, self.loc[1] + 1]]
                case "T":
                    self.fields = [[self.loc[0], self.loc[1]],
                                   [self.loc[0] - 1, self.loc[1]],
                                   [self.loc[0], self.loc[1] + 1],
                                   [self.loc[0], self.loc[1] - 1]]
                case "S":
                    self.fields = [[self.loc[0], self.loc[1]],
                                   [self.loc[0], self.loc[1] + 1],
                                   [self.loc[0] + 1, self.loc[1]],
                                   [self.loc[0] + 1, self.loc[1] - 1]]
                case "Z":
                    self.fields = [[self.loc[0], self.loc[1]],
                                   [self.loc[0], self.loc[1] - 1],
                                   [self.loc[0] + 1, self.loc[1]],
                                   [self.loc[0] + 1, self.loc[1] + 1]]
                case "L":
                    self.fields = [[self.loc[0], self.loc[1]],
                                   [self.loc[0], self.loc[1] - 1],
                                   [self.loc[0], self.loc[1] + 1],
                                   [self.loc[0] - 1, self.loc[1] + 1]]
                case "J":
                    self.fields = [[self.loc[0], self.loc[1]],
                                   [self.loc[0], self.loc[1] - 1],
                                   [self.loc[0], self.loc[1] + 1],
                                   [self.loc[0] - 1, self.loc[1] - 1]]
                case _:
                    raise Exception("Invalid shape.")
        else:
            self.fields = fields

        # Check if game over.
        for (row, col) in self.fields:
            if board.field[row][col] is not None:
                raise Exception("GAME OVER")


def play():
    """Event loop, DAS, lock delay and similar."""
    # consider adding a small timer within which no new button can be drop (or rotate) again
    pygame.init()
    counter = 0
    game = Board(HEIGHT, WIDTH)

    drawTetris.field(SCREEN, game)
    drawTetris.piece(game, SCREEN, game.active)
    landed_counter = 1
    # start_time = time.time()  // nice to have in time attack modes etc
    loop_time = time.time()
    last_drop = time.time()
    first_landed = True
    drop = False
    while True:

        counter += 1
        counter %= 100000
        landed_counter %= 100000
        if (time.time() - loop_time > game.time_to_drop(game.level) and game.check_landed() is False) or drop:
            game.progress_time()
            loop_time = time.time()
            first_landed = True
            drop = False
        if game.check_landed() and first_landed:
            first_landed = False
            landed_time = time.time()
        if game.check_landed() and not first_landed and time.time() - landed_time > LOCK_DELAY:
            first_landed = True
            game.progress_time()
            loop_time = time.time()

        for event in pygame.event.get():
            pygame.key.set_repeat(int(DAS * 1000), int(AFTER_DAS * 1000))
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key in CONTROLS["rotate_cw"]:
                    game.rotate("cw")
                if event.key in CONTROLS["rotate_ccw"]:
                    game.rotate("ccw")
                if event.key in CONTROLS["left"]:
                    game.move("L")
                if event.key in CONTROLS["right"]:
                    game.move("R")
                if event.key in CONTROLS["down"]:
                    game.move("D")
                if event.key in CONTROLS["drop"]:
                    if time.time() - last_drop < SPACE_DELAY:
                        break
                    game.move("S")
                    last_drop = time.time()
                    drop = True
                    break
                pygame.key.set_repeat(int(DAS * 1000), int(AFTER_DAS * 1000))
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)
                if event.key == pygame.K_q:
                    raise Exception("QUIT GAME")

        print(game)

        drawTetris.event_loop_update(game, SCREEN)


if __name__ == "__main__":
    """Initialize game and call the event loop function."""
    pygame.font.init()
    SCREEN_W = (WIDTH + 2) * drawTetris.BLOCK_SIZE
    SCREEN_H = (HEIGHT + 4) * drawTetris.BLOCK_SIZE
    SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    # maybe unnecessary
    pygame.display.set_caption("Tetris")

    run = True
    drawTetris.welcome_screen(SCREEN, SCREEN_W, SCREEN_H)
    while run:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                run = False
            if event_.type == pygame.KEYDOWN:
                play()
    pygame.quit()


def loss(game):
    """Evaluate how well a game is going.
    Possible parameters: points, coastline, max height, height variance, monotonicity"""
