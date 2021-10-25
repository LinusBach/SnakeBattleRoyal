import socket
import pickle
import random
from _thread import *

host = ''
port = 8080
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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
        self.alive = False
        self.head_color = (int(self.color[0]*0.5+64), int(self.color[1]*0.5+64), int(self.color[2]*0.5+64))
        self.color = (64, 64, 64)


try:
    serv.bind((host, port))
except socket.error as e:
    print(str(e))
serv.listen(5)

log = []

user = []

i_user = 0
dim = 5
max_food = 250
win_dim = (1000, 1000)
start_pos = [(100, 100), (100, 300), (100, 500), (100, 700), (100, 900),
             (300, 100), (300, 300), (300, 500), (300, 700), (300, 900),
             (500, 100), (500, 300), (500, 500), (500, 700), (500, 900),
             (700, 100), (700, 300), (700, 500), (700, 700), (700, 900),
             (900, 100), (900, 300), (900, 500), (900, 700), (900, 900)]
snake_color = (255, 0, 0)
snake_colors = [(255, 0, 0),    (0, 255, 0),    (0, 255, 255),  (0, 0, 255),
                (255, 0, 255),  (255, 0, 128),  (0, 255, 128),  (128, 0, 255)]
run = False


def threaded_login():
    print("waiting for connection")
    global run
    global i_user
    while True:
        clientsocket, addr = serv.accept()
        if not run:
            user.append({"socket": clientsocket, "address": addr[0] + ':' + str(addr[1]), "name": "user" + str(i_user),
                         "snake": Snake(snake_color, start_pos[i_user])})
            print('connected to: ' + user[i_user]["address"] + ' (' + user[i_user]["name"] + ')')
            clientsocket.send(user[i_user]["name"].encode())
            clientsocket.recv(4096)
            clientsocket.send(pickle.dumps(user[i_user]["snake"]))
            if i_user == 0:
                start_new_thread(client_receive_pre, (clientsocket, i_user))
            i_user += 1
            if i_user == 25:
                run = True


def client_receive_pre(conn, i):
    c_user = user[i]
    while True:

        # checking if user is still connected
        try:
            data = conn.recv(32767)
        except socket.error as e:
            print("disconnected: " + c_user["address"] + " (" + c_user["name"] + ")")
            user.remove(user[i])
            global i_user
            i_user -= 1
            break

        # checking for data
        if not data:
            break

        # breaking if data is "start"
        if data.decode() == "start":
            global run
            run = True
            break


print("host ip: " + str(socket.gethostbyname(socket.gethostname())) + "\nstart login")
start_new_thread(threaded_login, ())
print("start preround")
while not run:
    continue

# notify every user
for u in user:
    u["socket"].send("start".encode())

run = True
print("game begins")
events = []
food = []
while run:

    snakes = []
    for u in user:
        try:
            # receive & updating every users current snake
            u["snake"], snacked, events_client = pickle.loads(u["socket"].recv(64000))
            snakes.append(u["snake"])
            # adding death effect if a player died
            if "death" in events_client:
                events.append("flash")
            if snacked:
                food.remove(snacked)
                # events.append("flash")
        except socket.error as e:
            print("disconnected: {} ({})".format(u["address"], u["name"]))
            user.remove(u)
            i_user -= 1
        except ValueError:
            print("invalid snacked at ({})".format((u["snake"].pos_x, u["snake"].pos_y), u["name"]))

    # generating new food for snacked
    for i in range(max_food - len(food)):
        food.append((random.randint(0, (win_dim[0]-5)/dim)*dim, random.randint(0, (win_dim[1]-5)/dim)*dim))

        # send every user all snakes except for own snake + array of food + events
    for u in user:
        personal_snakes = snakes.copy()
        personal_snakes.remove(u["snake"])
        u["socket"].send(pickle.dumps((personal_snakes, food, events)))

    if "flash" in events:
        events.remove("flash")
