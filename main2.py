import random
import pygame
import sys
import os

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap

from data import mainwind_des

with open('data/score_time', 'r') as f:
    result = f.readlines(0)[0].split(';')
    print(result)
    top_score = int(result[0])
    last_time = int(result[1])
    sixGameDone = int(result[2])


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()

        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


class Board:
    def __init__(self, width, height, left=10, top=10, cell_size=30):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = 0
        self.set_view(left, top, cell_size)

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(0, 0, 0), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def on_click(self, cell):
        pass

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)


class Minesweeper(Board):
    def __init__(self, width, height, n):
        global mines, time
        super().__init__(width, height)
        self.ncell = None
        self.board = [[-1] * width for _ in range(height)]
        i = 0
        while i < n:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.board[y][x] == -1:
                self.board[y][x] = 10
                i += 1

    def check_cell(self, cell):  # Проверка клетки без её открытия
        x, y = cell
        s = self.board[y][x]
        print('Коорд-ы клетки: ' + str(cell) + '. Значение клетки: ' + str(s))
        return s

    def open_cell(self, cell, justOpen=False):  # открытие клетки
        global extra_lives
        self.ncell = cell
        x, y = cell

        if self.board[y][x] == -2 or self.board[y][x] == -3:
            return

        if self.board[y][x] == 10:
            if extra_lives > 0:
                extra_lives -= 1
                pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                                 (x * self.cell_size + (self.left + 2),
                                  y * self.cell_size + (self.top + 2),
                                  self.cell_size, self.cell_size - 4))

                myimage = pygame.image.load("data/bomb_icon.png")
                screen.blit(myimage,
                            (x * self.cell_size + self.left + 3, y * self.cell_size + self.top + 2))
                pygame.display.flip()
            else:
                self.loose()
            return

        s = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if x + dx < 0 or x + dx >= self.width or y + dy < 0 or y + dy >= self.height:
                    continue
                if self.board[y + dy][x + dx] == 10 or self.board[y + dy][x + dx] == -3:
                    s += 1

        print('Коорд-ы клетки: ' + str(cell) + '. Кол-во мин вокруг клетки: ' + str(s))
        self.board[y][x] = s

        if not justOpen:
            self.open_all_zero(cell)

    def open_all_zero(self, cell):
        # открытие всех пустых клеток
        x, y = cell

        s = 0
        if self.board[y][x] == 0:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if (x + dx < 0) or (x + dx >= self.width) or (y + dy < 0) or (
                            y + dy >= self.height):
                        continue
                    if self.board[y + dy][x + dx] == 10 or self.board[y + dy][x + dx] == -3:
                        s += 1
                    else:  # Если мин вокруг 0...
                        self.open_cell((x + dx, y + dy), True)
        else:
            pass

    def on_click(self, cell):
        self.open_cell(cell)

    def set_flag(self, mouse_pos):  # установка флага
        global flags
        cell = x, y = self.get_cell(mouse_pos)
        myimage = pygame.image.load("data/flag_icon.png")
        myimage = pygame.transform.scale(myimage, (29, 29))
        self.ncell = cell
        self.board[y][x] = self.check_cell((x, y))

        if self.board[y][x] == 10:
            print('Flag on bomb!')
            flags -= 1
            pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                             (x * self.cell_size + self.left,
                              y * self.cell_size + self.top,
                              self.cell_size, self.cell_size))
            screen.blit(myimage, (x * self.cell_size + self.left, y * self.cell_size + self.top))
            pygame.display.flip()
            self.board[y][x] = -3

        elif (self.board[y][x] != -2) and (self.board[y][x] < 0) and (self.board[y][x] != -3):
            flags -= 1
            self.board[y][x] = -2
            screen.blit(myimage, (x * self.cell_size + self.left, y * self.cell_size + self.top))
            pygame.display.flip()

        elif self.board[y][x] == -2:  # убрать флаг, если нажать на него
            flags += 1
            self.board[y][x] = -1
            pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                             (x * self.cell_size + self.left,
                              y * self.cell_size + self.top,
                              self.cell_size, self.cell_size))
        elif self.board[y][x] == -3:
            flags += 1
            self.board[y][x] = 10
            pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                             (x * self.cell_size + self.left,
                              y * self.cell_size + self.top,
                              self.cell_size, self.cell_size))

    def render(self):
        for y in range(self.height):
            for x in range(self.width):

                # if self.board[y][x] == 10: # Покраска мин
                #     pygame.draw.rect(screen, pygame.Color((144, 144, 144)),                                                     # Цвет мин (144, 144, 144)
                #                      (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,  # Цвет мин
                #                       self.cell_size))                                                                # Цвет мин

                if self.board[y][x] >= 1 and self.board[y][x] != 10:  # Если мин вокруг более 1...
                    pygame.draw.rect(screen, pygame.Color(184, 184, 184),
                                     (x * self.cell_size + self.left, y * self.cell_size + self.top,
                                      self.cell_size, self.cell_size))

                    font = pygame.font.Font(None, self.cell_size - 6)
                    text = font.render(str(self.board[y][x]), True, (0, 0, 0))
                    screen.blit(text, (
                    x * self.cell_size + self.left + 3, y * self.cell_size + self.top + 3))

                if self.board[y][x] == 0:  # Если мин вокруг 0...
                    pygame.draw.rect(screen, pygame.Color(184, 184, 184),
                                     (x * self.cell_size + self.left,
                                      y * self.cell_size + self.top,
                                      self.cell_size, self.cell_size))

                # if self.board[y][x] == -2 or self.board[y][x] == -3:
                #     pygame.draw.rect(screen, pygame.Color(255, 255, 0),
                #                      (x * self.cell_size + self.left,
                #                       y * self.cell_size + self.top,
                #                       self.cell_size, self.cell_size))

                # if self.board[y][x] == -3:
                #     pygame.draw.rect(screen, pygame.Color(255, 255, 0),
                #                      (x * self.cell_size + self.left,
                #                       y * self.cell_size + self.top,
                #                       self.cell_size, self.cell_size))

                pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top,
                                  self.cell_size,
                                  self.cell_size), 1)

        pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                         (400, 73, self.cell_size * 2, self.cell_size))
        font = pygame.font.Font(None, 30)
        text = font.render(str(extra_lives), True, (0, 0, 0))
        screen.blit(text, (400, 75))

        pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                         (400, 18, self.cell_size * 2, self.cell_size * 2))
        font = pygame.font.Font(None, 30)
        text = font.render(str(time), True, (0, 0, 0))
        screen.blit(text, (420, 20))

        pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                         (50, 63, self.cell_size * 1.5, self.cell_size * 1.5))
        font = pygame.font.Font(None, 30)
        text = font.render(str(flags), True, (0, 0, 0))
        screen.blit(text, (50, 65))

        if not stoprender:
            self.is_win()

    def is_win(self):
        s = 0
        for y in range(self.height):
            for x in range(self.width):
                if (self.board[y][x] == 10) or (self.board[y][x] == -2) or (self.board[y][x] == -1) or (flags != 0):
                    s += 1
        if s == 0:
            self.win()

    def loose(self):
        global stoprender
        print('You Loose!')
        s = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 10 or self.board[y][x] == -3:
                    pygame.draw.rect(screen, pygame.Color(144, 144, 144),
                                     (x * self.cell_size + (self.left + 2),
                                      y * self.cell_size + (self.top + 2),
                                      self.cell_size, self.cell_size - 4))

                    myimage = pygame.image.load("data/bomb_icon.png")
                    screen.blit(myimage, (
                        x * self.cell_size + self.left + 3, y * self.cell_size + self.top + 2))
                    pygame.display.flip()

                    pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                                     (x * self.cell_size + self.left,
                                      y * self.cell_size + self.top, self.cell_size,
                                      self.cell_size), 1)

                    font = pygame.font.Font(None, 60)
                    text = font.render(str("You Loose!"), True, (230, 50, 10))
                    screen.blit(text, (125, 30))
        stoprender = True

    def win(self):
        global stoprender, sixGame, top_score
        print('You Win!')
        s = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 10 or self.board[y][x] == -3:
                    pygame.draw.rect(screen, pygame.Color(0, 255, 0),
                                     (x * self.cell_size + (self.left + 2),
                                      y * self.cell_size + (self.top + 2),
                                      self.cell_size, self.cell_size - 4))

                    myimage = pygame.image.load("data/bomb_icon.png")
                    screen.blit(myimage, (
                    x * self.cell_size + self.left + 3, y * self.cell_size + self.top + 2))
                    pygame.display.flip()

                    pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                                     (x * self.cell_size + self.left,
                                      y * self.cell_size + self.top, self.cell_size,
                                      self.cell_size), 1)

                    font = pygame.font.Font(None, 60)
                    text = font.render(str("You Win!"), True, (0, 255, 0))
                    screen.blit(text, (150, 30))
        stoprender = True

        if (lvl >= 6) or (top_score >= 6):
            sixGame = 1
        else:
            sixGame = 0
        if lvl >= top_score:
            with open('data/score_time', 'w', encoding='utf8') as f:
                f.write(f'{lvl};{time};{sixGame}')



class MainWindow(QMainWindow, mainwind_des.Ui_MainWindow):
    def __init__(self, parent=None):
        global lvl, extra_lives, sixGame
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        print('showed!')

        self.lcdNumber_2.display(top_score)
        self.lcdNumber.display(last_time)
        self.spinBox_2.setValue(3)

        pixmap = QPixmap('data/bomb.png')
        self.label_3.setPixmap(pixmap)

        self.pushButton.clicked.connect(self.start_game)

        extra_lives= self.spinBox_2.value()
        lvl = int(self.spinBox.value())

        print(sixGameDone)
        if sixGameDone:
            self.label_5.setHidden(True)
            self.spinBox_2.setEnabled(True)
            sixGame = 1

    def start_game(self):
        global lvl, time, flags, sixGame, running, screen, size, stoprender, sixGameDone, clock, all_sprites, extra_lives
        ex.close()

        extra_lives = self.spinBox_2.value()
        print('hidden!')

        pygame.init()
        clock = pygame.time.Clock()
        all_sprites = pygame.sprite.Group()

        stoprender = False
        time = 0

        size = 500, 600
        screen = pygame.display.set_mode(size)

        time_on = False
        ticks = 0

        lvl = self.spinBox.value()
        board = Minesweeper(lvl, lvl, int(lvl ** 2 * 0.25))
        flags = int(lvl ** 2 * 0.25)
        board.set_view(int((500 - 30 * lvl) / 2), int((500 - 30 * lvl) / 2 + 100), 30)

        screen.fill((144, 144, 144))

        myimage = pygame.image.load("data/flag_icon.png")
        picture = pygame.transform.scale(myimage, (31, 31))
        screen.blit(picture, (10, 50))
        pygame.display.flip()

        myimage = pygame.image.load("data/clock_icon.png")
        picture = pygame.transform.scale(myimage, (31, 31))
        screen.blit(picture, (350, 15))
        pygame.display.flip()

        myimage = pygame.image.load("data/life_icon.png")
        picture = pygame.transform.scale(myimage, (31, 31))
        screen.blit(picture, (350, 70))
        pygame.display.flip()

        board.render()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
                    board.get_click(event.pos)
                if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 3):
                    board.set_flag(event.pos)
                if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 2):
                    board.win()
                    continue

            if not stoprender:
                board.render()

                if time != 999:
                    if (ticks % 100 == 0):
                        time += 1
                        ticks = 0
                        print(time)

            pygame.display.flip()
            clock.tick(100)
            ticks += 1
        pygame.quit()
        MainWindow().__init__()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
