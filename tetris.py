import curses
import random

# Tetris shapes
shapes = [
    [[1, 1, 1],
     [0, 1, 0]],
    
    [[0, 2, 2],
     [2, 2, 0]],
    
    [[3, 3, 0],
     [0, 3, 3]],
    
    [[4, 4],
     [4, 4]],
    
    [[0, 0, 5],
     [5, 5, 5]],
    
    [[0, 6, 0],
     [6, 6, 6]],
    
    [[7, 7, 7, 7]]
]

# Game settings
width = 10
height = 20

def rotate(shape):
    return [ [ shape[y][x]
            for y in range(len(shape)) ]
            for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and board[y + off_y][x + off_x]:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for _ in range(width)]] + board

def join_matrixes(matrix_1, matrix_2, matrix_2_offset):
    offset_x, offset_y = matrix_2_offset
    for y, row in enumerate(matrix_2):
        for x, val in enumerate(row):
            matrix_1[y + offset_y][x + offset_x] += val
    return matrix_1

def new_board():
    board = [[0 for _ in range(width)] for _ in range(height)]
    board += [[1 for _ in range(width)]]
    return board

class Tetris:
    def __init__(self, stdscr):
        self.board = new_board()
        self.stdscr = stdscr
        self.gameover = False
        self.score = 0
        self.level = 1
        self.stone = None
        self.stone_x = 0
        self.stone_y = 0
        self.next_stone = shapes[random.randint(0, len(shapes) - 1)]
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = shapes[random.randint(0, len(shapes) - 1)]
        self.stone_x = int(width / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.stdscr.nodelay(1)
        self.stdscr.timeout(1000 // self.level)
        curses.noecho()
        curses.curs_set(0)
        self.new_stone()

    def draw_board(self):
        self.stdscr.clear()
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.stdscr.addstr(y, x * 2, "[]")

        for y, row in enumerate(self.stone):
            for x, cell in enumerate(row):
                if cell:
                    self.stdscr.addstr(self.stone_y + y, (self.stone_x + x) * 2, "[]")

        self.stdscr.addstr(0, 0, f"Score: {self.score}")
        self.stdscr.addstr(1, 0, f"Level: {self.level}")
        self.stdscr.refresh()

    def drop(self):
        if not self.gameover:
            self.stone_y += 1
            if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y - 1))
                self.score += 1
                self.new_stone()
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            self.score += 100
                            self.level = self.score // 500 + 1
                            break
                    else:
                        break
            self.draw_board()

    def rotate(self):
        if not self.gameover:
            rotated = rotate(self.stone)
            if not check_collision(self.board, rotated, (self.stone_x, self.stone_y)):
                self.stone = rotated
                self.draw_board()

    def move(self, delta_x):
        if not self.gameover:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x + len(self.stone[0]) > width:
                new_x = width - len(self.stone[0])
            if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x
                self.draw_board()

    def game(self):
        while not self.gameover:
            self.draw_board()
            self.stdscr.timeout(1000 // self.level)
            key = self.stdscr.getch()
            if key == curses.KEY_RIGHT:
                self.move(1)
            elif key == curses.KEY_LEFT:
                self.move(-1)
            elif key == curses.KEY_DOWN:
                self.drop()
            elif key == curses.KEY_UP:
                self.rotate()
            elif key == ord('q'):
                break

def main(stdscr):
    game = Tetris(stdscr)
    game.game()

curses.wrapper(main)
