import socket
import pickle
from _thread import *
import random
import pygame

control_sets = [{"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s},
                {"left": pygame.K_j, "right": pygame.K_l, "up": pygame.K_i, "down": pygame.K_k},
                {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN},
                {"left": pygame.K_f, "right": pygame.K_h, "up": pygame.K_t, "down": pygame.K_g},
                {"left": pygame.K_4, "right": pygame.K_6, "up": pygame.K_8, "down": pygame.K_5}]


class Snake:
    def __init__(self, color, pos=(0, 0), length=1, width=5, controls={"left" : pygame.K_a, "right" : pygame.K_d,
                                                                       "up" : pygame.K_w, "down" : pygame.K_s}):
        self.width = width
        self.length = length
        self.head_color = color
        self.color = (int(color[0]*0.75), int(color[1]*0.75), int(color[2]*0.75))
        self.pos_x, self.pos_y = pos
        self.vel_x = 0
        self.vel_y = 0
        self.hatched = False
        self.alive = True
        self.body = [(self.pos_x, self.pos_y)]
        self.controls = controls

    def die(self):
        global food
        self.alive = False
        self.head_color = (int(self.color[0]*0.5+64), int(self.color[1]*0.5+64), int(self.color[2]*0.5+64))
        # self.color = (255, 255, 0) # (64, 64, 64)
        for f in self.body:
            food.append(f)
        self.body = []


def process_player(s, keys, pxarray):
    global snacked
    global snakes
    if keys[s.controls["left"]] and s.vel_x != s.width:
        s.vel_x = -s.width
        s.vel_y = 0
    # right
    elif keys[s.controls["right"]] and s.vel_x != -s.width:
        s.vel_x = s.width
        s.vel_y = 0
    # up
    elif keys[s.controls["up"]] and s.vel_y != s.width:
        s.vel_y = -s.width
        s.vel_x = 0
    # down
    elif keys[s.controls["down"]] and s.vel_y != -s.width:
        s.vel_y = s.width
        s.vel_x = 0

    if not s.hatched and not s.vel_y == s.vel_x == 0:
        s.hatched = True

    if s.alive and s.hatched:

        # vertical movement
        s.pos_x += s.vel_x
        if s.pos_x < 0 or s.pos_x > win_dim[0]-s.width:
            s.pos_x -= s.vel_x
            s.die()

        # horizontal movement
        s.pos_y += s.vel_y
        if s.pos_y < 0 or s.pos_y > win_dim[1]-s.width:
            s.pos_y -= s.vel_y
            s.die()

        # collision checking
        pixel = pxarray[s.pos_x, s.pos_y]
        # collision with food
        if pixel == win.map_rgb((255, 255, 0)):
            snacked.append((s.pos_x, s.pos_y))
            s.length += 1
            # events.append("flash")
        # other collision
        elif pixel is not win.map_rgb((0, 0, 0)):
            s.die()
        else:
            for snake in snakes:
                if (not snake == s) and (s.pos_x, s.pos_y) == (snake.pos_x, snake.pos_y):
                    s.die()
                    break

        if len(s.body) >= s.length:
            s.body.pop()
        s.body.insert(0, (s.pos_x, s.pos_y))


pygame.init()
win_dim = (500, 500)
win = pygame.display.set_mode(win_dim)
pygame.display.set_caption("Snake_Battle_Royal")

dim = 5
max_food = 250
win_dim = (500, 500)
start_pos = [(100, 100), (100, 400), (400, 400), (400, 100),
             (50, 250),  (250, 50),  (250, 450), (450, 250)]
snake_colors = [(255, 0, 0),    (0, 255, 0),    (0, 255, 255),  (0, 0, 255),
                (255, 0, 255),  (255, 0, 128),  (0, 255, 128),  (128, 0, 255)]

snakes = []
print("How many players?")
inp = int(input())

while 1 > inp or inp > 5:
    print("wrong input")
    inp = int(input())

for i in range(inp):
    snakes.append(Snake(snake_colors[i], start_pos[i], controls=control_sets[i]))

food = []
events = []

run = True
while run:

    print("running")

    snacked = []    # to store food that has been eaten

    for i in range(max_food - len(food)):
        food.append((random.randint(0, (win_dim[0]-5)/dim)*dim, random.randint(0, (win_dim[1]-5)/dim)*dim))

    pygame.time.delay(50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
            run = False

    p_keys = pygame.key.get_pressed()
    p_pxarray = pygame.PixelArray(win)

    for snake in snakes:
        process_player(snake, p_keys, p_pxarray)

    if "flash" in events:
        events.remove("flash")
        win.fill((255, 255, 255))
        pygame.display.update()
        pygame.time.delay(100)

    win.fill((0, 0, 0))

    for f in snacked:
        if f in food:
            food.remove(f)

    for f in food:
        pygame.draw.rect(win, (255, 255, 0), (f[0], f[1], 5, 5))

    for c_s in snakes:
        for b in c_s.body:
            pygame.draw.rect(win, c_s.color, (b[0], b[1], c_s.width, c_s.width))
        pygame.draw.rect(win, c_s.head_color, (c_s.body[0][0], c_s.body[0][1], c_s.width, c_s.width))

    pygame.display.update()

pygame.quit()

