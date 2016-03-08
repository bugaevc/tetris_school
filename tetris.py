import pygame
from pygame.locals import *
import random
from math import floor

def random_color():
    while True:
        a, b, c = (random.choice([0, 128, 255]) for i in range(3))
        if a + b + c < 50 or a + b + c > 255 * 2:
            continue
        return a, b, c
    
def limit_aver(arr):
    return floor((max(arr) + min(arr)) / 2 + 1)
def aver(arr):
    return sum(arr) / len(arr)

class timer:
    events = dict()
    def work_event(event):
        if event in timer.events:
            timer.events[event].callback()
        return event in timer.events
    
    def __init__(self, interval, callback):
        #if interval is zero, callback will be called as in while-loop, but unlike it events like KEYDOWN will pass between iterations
        self.interval = interval
        self.running = False
        if interval:
            self.callback = callback
        else:
            def newcallback():
                if self.running:
                    callback()
                #Check if running again in order not to miss stopping during callback call
                #And check that there're no self.event in the queue in order not to miss restarting during callback call
                if self.running and not pygame.event.peek(self.event):
                    pygame.event.post(pygame.event.Event(self.event))
            self.callback = newcallback
        self.start()
        
    def start(self):
        self.event = next(ev for ev in range(USEREVENT, NUMEVENTS) if ev not in timer.events)
        pygame.event.clear(self.event)
        timer.events[self.event] = self
        if self.interval:
            pygame.time.set_timer(self.event, self.interval)
        else:
            pygame.event.post(pygame.event.Event(self.event))
        self.running = True

    def stop(self):
        self.running = False
        pygame.time.set_timer(self.event, 0)
        pygame.event.clear(self.event)
        if self.event in timer.events:
            del timer.events[self.event]

            
class game:
    def __init__(self, methods):
        self.WIDTH, self.HEIGHT = 10, 20
        self.SQUARE_SIZE = 40
        self.BORDER_WIDTH = 1
        
        self.figures = [
        [(1, 0), (0, 0), (1, 1), (0, 1)], #O
        [(0, 0), (1, 0), (2, 0), (3, 0)], #I
        [(0, 0), (1, 0), (2, 0), (2, 1)], #J
        [(0, 0), (1, 0), (2, 0), (0, 1)], #L
        [(0, 0), (1, 0), (1, 1), (2, 1)], #Z
        [(0, 1), (1, 1), (1, 0), (2, 0)], #S
        [(0, 0), (1, 0), (2, 0), (1, 1)]] #T
        
        self.bgcolor = (255, 255, 255)
        self.brdcolor = (0, 0, 0)
        self.size = ((self.WIDTH + 8) * self.SQUARE_SIZE, self.HEIGHT * self.SQUARE_SIZE)

        self.draw_rect, self.render, self.display_update, self.end_game, self.new_figure_actions = methods

    def start(self):
        #Always call this method berfore playing
        #It also works for rstart the game
        
        #None is free cell, -1 is border
        #First y then x
        self.field = [[-1 if x >= self.WIDTH or y >= self.HEIGHT else None for x in range(self.WIDTH + 4)] for y in range(self.HEIGHT + 4)]
        self.d, self.destroyed_line = 0, self.HEIGHT
        self.speed = 1000
        self.score = 0
        self.figure_id = -1
        self.figures_colors = []
        self.gameover_state = None #None - game isn't finished, True/False - show/hide "game over ..." text
        try:
            self.timer.stop()
        except:
            self.timer = timer(10000, lambda: None)
            self.timer.stop()
        self.paused = False
        self.next_figure = self.random_figure()
        self.figures_colors.append(random_color())
        self.load_new_figure()

    def draw_cell(self, cell, y_move=0, field=None):
        if field is None:
            field = self.field
        ind = field[cell[1]][cell[0]]
        color = self.bgcolor if ind is None else self.figures_colors[ind]
        x, y = cell[0] * self.SQUARE_SIZE, cell[1] * self.SQUARE_SIZE + y_move
        self.draw_rect(self.change_color(self.brdcolor), (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
        parts = [(0, self.SQUARE_SIZE - self.BORDER_WIDTH), (self.SQUARE_SIZE - self.BORDER_WIDTH, self.BORDER_WIDTH)]
        for dx in [0, 1]:
            for dy in [0, 1]:
                if not dx + dy or (ind is not None and field[cell[1]][cell[0]] == field[cell[1] + dy][cell[0] + dx]):
                    self.draw_rect(self.change_color(color), (x + parts[dx][0], y + parts[dy][0], parts[dx][1], parts[dy][1]))

    def change_color(self, color):
        if self.gameover_state is not None:
            return tuple(c // 4 for c in color)
        return color
    
    def redraw(self):
        self.draw_rect(self.change_color(self.bgcolor), (0, 0, self.size[0], self.size[1]))
        if not self.d:
            for x in range(self.WIDTH):
                for y in range(self.HEIGHT):
                    self.draw_cell((x, y))
        else:
            for y in range(self.destroyed_line, self.HEIGHT + 1):
                for x in range(self.WIDTH):
                    self.draw_cell((x, y), -self.SQUARE_SIZE)
            for y in range(self.destroyed_line):
                for x in range(self.WIDTH):
                    self.draw_cell((x, y), self.d)
        dx, dy = self.WIDTH + 1, 1
        temp_field = [line[:] +  [-1] * self.WIDTH for line in self.field]
        for x, y in self.next_figure:
            temp_field[y + dy][x + dx] = self.figure_id + 1
        for x, y in self.next_figure:
            self.draw_cell((x + dx, y + dy), field=temp_field)
        self.render(str(self.score), self.SQUARE_SIZE * 4, self.change_color(self.brdcolor),
                    self.change_color(self.bgcolor), ((self.WIDTH + 1) * self.SQUARE_SIZE, self.SQUARE_SIZE * 8))
        self.render(str(self.figure_id), self.SQUARE_SIZE * 3, self.change_color(self.brdcolor),
                    self.change_color(self.bgcolor), ((self.WIDTH + 1) * self.SQUARE_SIZE, self.SQUARE_SIZE * 15))
        if self.gameover_state:
            self.render('Game over', self.SQUARE_SIZE * 4, (255, 0, 0), None, (self.SQUARE_SIZE * 2, self.SQUARE_SIZE * 2))
            self.render('Your score: ' + str(self.score), self.SQUARE_SIZE * 3, (255, 0, 0), None, (self.SQUARE_SIZE, self.SQUARE_SIZE * 6))            
            self.render('Press SPACE to exit', self.SQUARE_SIZE * 2, (255, 0, 0), None, (self.SQUARE_SIZE * 2, self.SQUARE_SIZE * 10))
        self.display_update()

    def put_figure(self, visible=True):
        for x, y in self.current:
            self.field[y][x] = self.figure_id if visible else None
        #Drawing figure only after applying all field changes in order to prevent false borders
        for cell in self.current:
            self.draw_cell(cell)

    def pause(self, pause=None):
        if pause is None:
            pause = not self.paused
        self.paused = pause
        if pause:
            self.timer.stop()
        else:
            self.redraw()
            self.timer.start()

    def move(self, new_figure):
        self.put_figure(False)
        nf = list(new_figure)
        if all(self.field[y][x] is None for x, y in nf):
            self.current = nf
            res = True
        else:
            res = False
        self.put_figure()
        self.display_update()
        return res

    def check_lines(self, end_callback): #Timer-owned function
        lines_count = 0
        y = 0
        def callback():
            nonlocal y, lines_count
            while y < self.HEIGHT and any(self.field[y][x] is None for x in range(self.WIDTH)):
                y += 1
            if y == self.HEIGHT:
                self.score += 2 ** lines_count - 1
                end_callback()
            else:
                lines_count += 1
                self.destroy_line(y, callback)
        callback()

    def destroy_line(self, y, end_callback): #Timer-owned function
        #Adding a new line
        self.field[:0] = [[None] * self.WIDTH + [-1] * (len(self.field[0]) - self.WIDTH)]
        #Smooth animation
        #It is after adding a new first line but before deleting full line in order to supress false borders
        self.d = -self.SQUARE_SIZE
        self.destroyed_line = y + 1 #Because of the added line
        def callback():
            #Drawing a frame
            self.redraw()
            self.d += 1
            if not self.d:
                self.timer.stop()
                del self.field[y + 1]
                #And now the final frame with borders
                self.redraw()
                #Instead of simple call end_callback(), we use this to avoid recursion (it would appear if end_callback calls destroy_line):
                def mini_callback():
                    self.timer.stop()
                    end_callback()
                self.timer = timer(0, mini_callback)
        self.timer.stop()
        self.timer = timer(0, callback) #ATTENTION: This line is the last one but callback will work after it

    def work_event(self, event):
        if self.d or self.paused:
            return
        if event == 'down':
            if not self.move((x, y + 1) for x, y in self.current):
                self.load_new_figure()
        if event == 'left':
            self.move((x - 1, y) for x, y in self.current)
        if event == 'right':
            self.move((x + 1, y) for x, y in self.current)
        if event == 'up':
            #Rotation about (0, 0)
            new_figure = [(-y, x) for x, y in self.current]
            #Finding centers
            cntr_x, cntr_y = map(limit_aver, zip(*self.current))
            cntr_x_new, cntr_y_new = map(limit_aver, zip(*new_figure))
            #Now moving to the destination
            any(self.move((x - cntr_x_new + cntr_x + dx, y - cntr_y_new + cntr_y + dy) for x, y in new_figure)
                for dx in [0, -1, 1, -2, 2, -3, 3, -4, 4] for dy in [0, -1, 1, -2, 2, -3, 3, -4, 4])
        if event == 'space':
            if self.gameover_state is not None:
                self.gameover_state = None
            else:
                self.timer.stop()
                self.timer = timer(0, lambda: self.work_event('down'))

    def random_figure(self):
        return random.choice(self.figures)
    
    def load_new_figure(self):
        def callback():
            dx = self.WIDTH // 2 - limit_aver([x for x, y in self.next_figure])
            self.current = [(x + dx, y) for x, y in self.next_figure]
            if all(self.field[y][x] is None for x, y in self.current):
                self.next_figure = self.random_figure()
                self.figures_colors.append(random_color())
                self.figure_id += 1
                if self.figure_id % 10 == 9:
                    self.speed -= self.speed // 10
                self.put_figure()
                self.redraw()
                self.timer.stop()
                self.timer = timer(self.speed, lambda: self.work_event('down'))
                self.new_figure_actions()
            else:
                self.game_over()
        self.check_lines(callback)

    def game_over(self):
        self.timer.stop()
        self.gameover_state = True
        self.new_figure_actions()
        def callback():
            if self.gameover_state is None:
                self.timer.stop()
                self.end_game()
            else:
                self.gameover_state = not self.gameover_state
                self.redraw()
        self.timer = timer(1000, callback)
        

pygame.init()

def change_color(color):
    if botgame.paused:
        return color
    if color is None:
        return color
    r, g, b = (c // 4 for c in color)
    return r, g, b + 128
def screen_fill(color, *args):
    screen.fill(change_color(color), *args)
def render(text, size, color, backcolor, dest):
    color, backcolor = change_color(color), change_color(backcolor)
    if backcolor is None: #Because of pygame is C-written and passing None as backcolor will raise an error, unlike passing noting
        screen.blit(pygame.font.SysFont(None, size).render(text, True, color), dest)
    else:
        screen.blit(pygame.font.SysFont(None, size).render(text, True, color, backcolor), dest)
def end_game():
    global game_started
    if botgame.paused:
        game_started = False
        botgame.pause()
    else:
        botgame.start()
      
def display_update():
    if not botgame.paused:
        screen.blit(surface_TETRIS, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE))
        if game_started:
            screen.blit(surface_paused, (botgame.SQUARE_SIZE * 6, botgame.SQUARE_SIZE * 5))
        else:
            screen.blit(surface_press_SPACE, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 5))
        screen.blit(surface_P, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 8))
        screen.blit(surface_arrows, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 9))
        screen.blit(surface_up, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 10))
        screen.blit(surface_SPACE, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 11))
        screen.blit(surface_R, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 12))
        screen.blit(surface_E, (botgame.SQUARE_SIZE * 2, botgame.SQUARE_SIZE * 13))
        screen.blit(surface_copyright, (botgame.SQUARE_SIZE, botgame.SQUARE_SIZE * 15))
    pygame.display.update()

bot_iter = -1
def bot():
    global bot_iter
    if botgame.paused:
        return
    bot_iter += 1
    cur_bot_iter = bot_iter
    if botgame.gameover_state is not None:
        def callback():
            if botgame.paused:
                return
            tmr.stop()
            if bot_iter != cur_bot_iter:
                return
            botgame.work_event('space')
        tmr = timer(4000, callback)
        return
    best_rating, best_dx, best_turns = -100000, -1000000, -1
    def end_callback():
        if bot_iter != cur_bot_iter:
            return
        actions = []
        for i in range(best_turns):
            actions.append('up')
        if best_dx > 0:
            for i in range(best_dx):
                actions.append('right')
        else:
            for i in range(-best_dx):
                actions.append('left')
        actions.append('space')
        def callback():
            nonlocal actions
            if not actions or bot_iter != cur_bot_iter:
                tmr.stop()
            else:
                botgame.work_event(actions[0])
                actions[0:1] = []
        tmr = timer(0, callback)
    turns = 0
    def turn_callback():
        nonlocal turns, best_dx, best_rating, best_turns
        if turns == 4 or bot_iter != cur_bot_iter:
            tmr.stop()
            end_callback()
            return
        field = [[None if (x, y) in botgame.current else botgame.field[y][x] for x in range(len(botgame.field[0]))] for y in range(len(botgame.field))]
        for dx in range(-botgame.WIDTH, botgame.WIDTH):
            current = [(x + dx, y) for x, y in botgame.current]
            if not all(0 <= x < botgame.WIDTH for x, y in current):
                continue
            rating = 0
            while all(field[y + 1][x] is None for x, y in current):
                current = [(x, y + 1) for x, y in current]
            rating = aver([y for x, y in current])
            rating -= len([x for x, y in current if (x, y + 1) not in current and field[y + 1][x] is None]) * rating / 4
            if rating > best_rating:
                best_rating, best_dx, best_turns = rating, dx, turns
        botgame.work_event('up')
        turns += 1
    tmr = timer(0, turn_callback)
    
game_started = False
methods = [screen_fill, render, display_update, end_game, bot]
usergame = game(methods)
botgame = game(methods)
screen = pygame.display.set_mode(botgame.size)

surface_TETRIS = pygame.font.SysFont(None, botgame.SQUARE_SIZE * 5).render('TETRIS', False, (255, 0, 0))
surface_paused = pygame.font.SysFont(None, botgame.SQUARE_SIZE * 2).render('Paused', False, (255, 0, 0))
surface_press_SPACE = pygame.font.SysFont(None, botgame.SQUARE_SIZE * 2).render('Press SPACE to start', False, (255, 0, 0))
surface_P = pygame.font.SysFont(None, botgame.SQUARE_SIZE).render('P                             pause/continue', False, (255, 0, 0))
surface_arrows = pygame.font.SysFont(None, botgame.SQUARE_SIZE).render('left, right, down    move the figure', False, (255, 0, 0))
surface_up = pygame.font.SysFont(None, botgame.SQUARE_SIZE).render('up                           turn the figure', False, (255, 0, 0))
surface_SPACE = pygame.font.SysFont(None, botgame.SQUARE_SIZE).render('SPACE                    drop the figure', False, (255, 0, 0))
surface_R = pygame.font.SysFont(None, botgame.SQUARE_SIZE).render('R                             restart the game', False, (255, 0, 0))
surface_E = pygame.font.SysFont(None, botgame.SQUARE_SIZE).render('E                             abort the game', False, (255, 0, 0))
surface_copyright = pygame.font.SysFont(None, botgame.SQUARE_SIZE * 2).render('(c) bugaevc, 2012-2013', False, (255, 0, 0))


pygame.display.set_caption('Tetris')
botgame.start()

while True:
    event = pygame.event.wait()
    if event.type == QUIT:
        exit()
    timer.work_event(event.type)
    if event.type == KEYDOWN:
        #Game control
        if game_started:
            if event.key in [K_DOWN, K_UNKNOWN]:
                usergame.work_event('down')
            if event.key == K_LEFT:
                usergame.work_event('left')
            if event.key == K_RIGHT:
                usergame.work_event('right')
            if event.key == K_UP:
                usergame.work_event('up')
            if event.key == K_SPACE:
                usergame.work_event('space')
        #General
        if event.key == K_p:
            if game_started:
                #Exactly in this order!
                botgame.pause()
                usergame.pause()
        if event.key == K_r:
            if botgame.paused:
                usergame.start()
            else:
                botgame.start()
        if event.key == K_F5:
            if botgame.paused:
                usergame.redraw()
            else:
                botgame.redraw()
        if not game_started and event.key == K_SPACE:
            botgame.pause()
            game_started = True
            usergame.start()
        if event.key == K_e:
            game_started = False
            usergame.pause(True)
            botgame.pause(False)
