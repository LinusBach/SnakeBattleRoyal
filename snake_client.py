import socket
import pickle
from _thread import *
import pygame


class Snake:
    def __init__(self, color, pos=(0, 0), length=1, width=5):
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

    def die(self):
        global events
        events.append("death")
        self.alive = False
        self.head_color = (int(self.color[0]*0.5+64), int(self.color[1]*0.5+64), int(self.color[2]*0.5+64))
        self.color = (64, 64, 64)


print("target IP:")
host = input()
port = 8080
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((host, port))
except socket.error as e:
    print(str(e))

preround = True


def threaded_console():
    inp = input()
    while inp != "start":
        inp = input()
    client.send(inp.encode())


start_new_thread(threaded_console, ())

pygame.init()
win_dim = (1000, 1000)
win = pygame.display.set_mode(win_dim)
pygame.display.set_caption("Snake_Battle_Royal")

dim = 5     # value used as metric for graphics
print(client.recv(4096).decode())
client.send(b"received")
s = pickle.loads(client.recv(32767))

snakes = []

while preround:
    from_server = client.recv(32767).decode()
    if from_server == "start":
        preround = False

food = []
events = []

run = True
while run:

    snacked = ()    # to store food that has been eaten

    pygame.time.delay(50)
    pxarray = pygame.PixelArray(win)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
            run = False

    keys = pygame.key.get_pressed()

    # left
    if keys[pygame.K_a] and s.vel_x != s.width:
        s.vel_x = -s.width
        s.vel_y = 0
    # right
    elif keys[pygame.K_d] and s.vel_x != -s.width:
        s.vel_x = s.width
        s.vel_y = 0
    # up
    elif keys[pygame.K_w] and s.vel_y != s.width:
        s.vel_y = -s.width
        s.vel_x = 0
    # down
    elif keys[pygame.K_s] and s.vel_y != -s.width:
        s.vel_y = s.width
        s.vel_x = 0

    if not s.vel_x == s.vel_y == 0 and not s.hatched:
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
            snacked = (s.pos_x, s.pos_y)
            s.length += 1
        # other collision
        elif pixel is not win.map_rgb((0, 0, 0)):
            s.die()
        else:
            for snake in snakes:
                if (s.pos_x, s.pos_y) == (snake.pos_x, snake.pos_y):
                    s.die()
                    break

        if len(s.body) >= s.length:
            s.body.pop()
        s.body.insert(0, (s.pos_x, s.pos_y))

    data = pickle.dumps((s, snacked, events))
    client.send(data)

    if "flash" in events:
        win.fill((255, 255, 255))
        pygame.display.update()
        pygame.time.delay(100)
        events.remove("flash")

    win.fill((0, 0, 0))
    data = client.recv(1048576)
    snakes, food, events = pickle.loads(data)

    for f in food:
        pygame.draw.rect(win, (255, 255, 0), (f[0], f[1], 5, 5))

    for c_s in snakes:
        for b in c_s.body:
            pygame.draw.rect(win, c_s.color, (b[0], b[1], c_s.width, c_s.width))
        pygame.draw.rect(win, c_s.head_color, (c_s.body[0][0], c_s.body[0][1], c_s.width, c_s.width))

    for b in s.body:
        pygame.draw.rect(win, s.color, (b[0], b[1], s.width, s.width))
    pygame.draw.rect(win, s.head_color, (s.body[0][0], s.body[0][1], s.width, s.width))

    pygame.display.update()


print("score: " + str(s.length))
pygame.quit()

while True:
    client.send(input().encode())
