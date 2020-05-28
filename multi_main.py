import pygame
from random import randint, random, choice, shuffle
import socket, time, threading, requests, sys, logging, os

# logging setup
log_filename = 'covid_cover.log'
global_exit = False

logging.basicConfig(filename=log_filename,
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)
logging.info('game init')


# exit point IN ANY WAY
# is used when game stops
# saves and logs exit code (error_code)
def exit_game():
    global global_exit
    # setting signal for other threads to stop
    global_exit = True
    # waiting for threads to stop
    time.sleep(0.25)
    logging.info(f'exit code: {error_code}')
    with open('score.dat', mode='w', encoding='utf-8') as file:
        file.write(str(score) + ' ' + str(error_code))
    sys.exit()


error_code = 0
score = None
# parsing and amount validation for cmd args
if len(sys.argv) != 7:
    error_code = -7
    exit_game()
args = sys.argv[1:]

pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
# sprite groups set up
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
building_group = pygame.sprite.Group()
settings_buttons_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
terrain_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()

bank_buttons = pygame.sprite.Group()

pharm_buttons = pygame.sprite.Group()
pharm_group = pygame.sprite.Group()
background_pharm = pygame.sprite.Group()
pharm_products = pygame.sprite.Group()

shop_buttons = pygame.sprite.Group()
shop_group = pygame.sprite.Group()
background_shop = pygame.sprite.Group()
shop_products = pygame.sprite.Group()

house_buttons = pygame.sprite.Group()
house_group = pygame.sprite.Group()
background_house = pygame.sprite.Group()
house_products = pygame.sprite.Group()

product_buttons = pygame.sprite.Group()

remote_players = pygame.sprite.Group()
# remote players are stored in this dict
online_players = dict()
# other global vars
building_collide_step = 0
near_building_message = None
near_building = None
gravity = 1
menu_is_on = False
music_on = True
effects_on = True
arrested = False

orders = None

# internal_id = input('Enter internal id:   ')
# setting vars from args for online mode
role, score, host, port, internal_id, player_name = args
score = int(score)
port = int(port)
api_port = 8080
# for debug
'''role = 'volunteer'
score = 0
host, port = '127.0.0.1', 9000
player_name = '123456'
# internal_id = '9f8e6b0c-62c7-4b09-b6d3-f923f3bf9860'
# internal_id = '0c4b8f94-b0d1-4731-8566-0bfa4a989610'
internal_id = '2a288d46-b3bf-4669-a938-dbaa6e8d9126'''
# ip = socket.gethostbyname('0.tcp.ngrok.io')
# host = ip
# host = '84.201.168.123'

# once a player is caught his id is added to this list
# this list id transmitted
# if id of client is in the list we procceed this case and arrest him
caught_ids = []
# all sounds for levels (used only in single mode)
speeches = {'intro': pygame.mixer.Sound('data/speech/intro.wav'),
            '1': pygame.mixer.Sound('data/speech/1.wav'),
            '2': pygame.mixer.Sound('data/speech/2.wav'),
            '3': pygame.mixer.Sound('data/speech/3.wav'),
            'autro': pygame.mixer.Sound('data/speech/autro.wav'),
            'news': pygame.mixer.Sound('data/speech/news.wav')}

music = {'main': pygame.mixer.Sound('data/music/main_music.ogg')}
# music['main'].play(-1)

# all objects sounds
sounds = {'apple': pygame.mixer.Sound('data/sounds/apple_crunch.wav'),
          'atm_button': pygame.mixer.Sound('data/sounds/atm_button.wav'),
          'bottle_open': pygame.mixer.Sound('data/sounds/bottle_open.wav'),
          'cashbox': pygame.mixer.Sound('data/sounds/cashbox.wav'),
          'close_door': pygame.mixer.Sound('data/sounds/close_door.wav'),
          'drink_gulp': pygame.mixer.Sound('data/sounds/drink_gulp.wav'),
          'open_door': pygame.mixer.Sound('data/sounds/open_door.wav')}

player_params = dict()
products = dict()


# the heart of multi mode
def operate_player_data():
    global global_exit
    # always trying to get a connection
    while True:
        try:
            # only sockets (tcp) are used for transmitting coords and other data
            con = socket.socket()
            try:
                con.connect((host, port))
            except ConnectionRefusedError:
                # if server is too busy to establish a connection we don't mind and catch the exception
                con.close()
            caught = caught_ids.copy()
            # transmitting all necessary vars to the server at once
            # raw str '\t' is used to join args
            # '%' is used to join caught players id at the end
            con.send(
                (player.id + r'\t' + player_name + r'\t' + player.get_pos_info() + r'\t' + '%'.join(caught)).encode(
                    'utf-8'))

            # we get data until it ends (and use end flag as a signal)
            end = False
            while not end:
                # get data
                data = con.recv(1024).decode('utf-8')
                # if that's it but we have the last data
                if 'end' in data and len(data) > 3:
                    # switch flag
                    end = True
                    # separate 'end'
                    data = data[:data.index('end')]
                # if that's the end, stop immediatly
                elif data == 'end':
                    break
                # by this point we have got remote player params
                # firstly, separate id and name
                id, name, params = data.split(r'\t')[0], data.split(r'\t')[1], r'\t'.join(data.split(r'\t')[2:])
                # if we are NOT drawing this character (it's NOT in the group and dict)
                # that character is not the client
                if str(id) not in player_params.keys() and id != player.id:
                    role = params.split(r'\t')[0]
                    # create instance and add to the group as well as to our dict
                    player_params[id] = RemotePlayer(str(id), 0, 0, role, name, remote_players)
                    # if there was an exception in the __init__ or
                    # in the update_images (explained in the RemotePlayer below)
                    if len(player_params[id].groups()) == 0:
                        player_params[id] = RemotePlayer(str(id), 0, 0, role, name, remote_players)
                    time.sleep(0.002)
                # by this point we have already declared needed remote player
                # set params to update position direction side etc
                player_params[id].set_params(params)
                time.sleep(0.002)
        # if ANY trouble in the loop
        # continue the loop to save connection
        # if the wireless connection is weak it happens often, so, we often do not update other players
        # and if it happens too often the cleanning thread just delete them
        except Exception as e:
            # print(e)
            continue
        finally:
            # in any way we check the exit flag
            if global_exit:
                break


# function in the thread
# deletes and kills all remote players
def clean_params():
    global global_exit, player_params, caught_ids
    while True:
        try:
            print(player_params)
            for i in player_params:
                player_params[i].kill()
            player_params = dict()
        finally:
            caught_ids = []
            if global_exit:
                break
            time.sleep(5)


# to check if order is done (request to server, if not found, it's done)
def check_order_is_done():
    global player, error_code
    if player.order:
        try:
            response = requests.get(f'http://{host}:{api_port}/api/orders/{player.order}/token/{internal_id}',
                                    timeout=0.25)
        except requests.exceptions.Timeout:
            error_code = -6
            exit_game()
        except requests.exceptions.ConnectionError:
            error_code = -5
            exit_game()
        print(response.status_code)
        if response.status_code == 404:
            player.order = 'done'


def stop_speeches():
    for sound in speeches.values():
        sound.stop()


def load_image(path, colorkey=None, size=None) -> pygame.Surface:
    image = pygame.image.load(path).convert_alpha()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    if size:
        image = pygame.transform.scale(image, size)
    return image


def check_collisions(player):
    check_near_building(player)
    for i in all_sprites:
        if id(player) == id(i):
            continue
        if i.is_obstacle():
            if pygame.sprite.collide_mask(player, i):
                return True
    return False


# if player collides building (logical, not phisical collision))
def check_near_building(player):
    global near_building, near_building_message
    near_building, near_building_message = None, None
    for building in building_group:
        if pygame.sprite.collide_mask(player, building):
            near_building = building
            near_building_message = f'Нажмите [E], чтобы войти в {building.name}'


def render_text(line, size=50, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    text = font.render(line, 1, color)
    return text


# main class for all remote players, stores params for drawing
class RemotePlayer(pygame.sprite.Sprite):
    def __init__(self, id, x, y, role, name, *groups):
        self.id = id  # internal id of user
        self.name = name  # username
        super().__init__(groups)
        self.role = role  # policeman, citizen or volunteer
        self.scanner_is_on = False  # only for policemen
        self.side = 'left'  # the sidem direction for drawing sprite
        self.update_images()

        self.image = self.frames['right'][0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.is_moving = False
        self.clock = pygame.time.Clock()

        self.infected = None

        self.caught = 0

    def get_coords(self):
        return self.rect.x, self.rect.y

    def set_position(self, pos):
        self.rect.x, self.rect.y = pos

    def set_moving(self, value):
        self.is_moving = value

    def is_obstacle(self):
        return False

    # main func for remote players
    # update all params got from the server
    def set_params(self, data):
        data = data.split(r'\t')[1:]
        # print(123)
        # print(data)
        # validation of params
        try:
            # assert len(data) == 5
            new_x, new_y = int(data[0]), int(data[1])
            moving = True if data[2] == 'True' else False
            assert data[3] in ['left', 'right'] and str(data[3]).isalpha()
            infected = str(data[4])
        except Exception as e:
            return
        # updating params
        self.set_position((new_x + terrain.rect.x, new_y + terrain.rect.y))
        self.is_moving = moving
        # probably a mistake, but set image can be avaliable only for the second or even third time
        # game work better in this way
        while True:
            try:
                self.image = self.frames[data[3]][0]
            except IndexError:
                continue
            break
        # if player was caught, proceed the arrest
        if internal_id in data[5].split('%'):
            global arrested
            arrested = True
        if infected == 'None':
            self.infected = None
        elif infected.isdigit():
            self.infected = int(infected)

    # func for setting next image, animation and changing according to the params from server
    def update_images(self):
        # if params were damaged and init wasn't finished because of error
        # probably fixed
        if not self.role:
            self.kill()
        self.frames = {'left': [], 'right': []}
        role = self.role
        if self.role == 'volunteer':
            role = 'citizen'
        self.frames['left'].append(
            pygame.transform.flip(load_image(f'data/characters/{role}_right_5.png', size=(80, 110)), 1, 0))
        try:
            self.frames['left'][0].blit(render_text(self.name, 17, (255, 0, 0)), (0, 0))
        except Exception as e:
            print(e)
        # if client is a policeman and the scanner is on: draw the infected state
        if self.scanner_is_on:
            if self.infected == 1:
                self.frames['left'][0].blit(load_image('data/characters/not_stated.png', size=(20, 20)), (60, 0))
            elif self.infected == 2:
                self.frames['left'][0].blit(load_image('data/characters/ok.png', size=(20, 20)), (60, 0))
            elif self.infected == 3:
                self.frames['left'][0].blit(load_image('data/characters/infected.png', size=(20, 20)), (60, 0))

        self.frames['right'].append(
            load_image(f'data/characters/{role}_right_5.png', size=(80, 110)))
        try:
            self.frames['right'][0].blit(render_text(self.name, 17, (255, 0, 0)), (0, 0))
        except Exception as e:
            print(e)
        if self.scanner_is_on:
            if self.infected == 1:
                self.frames['right'][0].blit(load_image('data/characters/not_stated.png', size=(20, 20)), (60, 0))
            elif self.infected == 2:
                self.frames['right'][0].blit(load_image('data/characters/ok.png', size=(20, 20)), (60, 0))
            elif self.infected == 3:
                self.frames['right'][0].blit(load_image('data/characters/infected.png', size=(20, 20)), (60, 0))
        # setting prepared image
        self.image = self.frames[self.side][0]

    def update(self, *args):
        if not args:
            return
        scanner_on = args[0]
        if scanner_on != self.scanner_is_on:
            # func is called again if scanner state was changed
            self.scanner_is_on = scanner_on
            self.update_images()


# main class for client
# drawing; storing vars, products, etc; moving; changing health, money, infection % etc
# is declared before the menu (game startup)
class Player(pygame.sprite.Sprite):
    speed = 10
    jump_power = 15

    def __init__(self, x, y, role, *groups):
        super().__init__(groups)
        # set role value as an attr
        self.role = role
        # citizen and volunteer each has the same sprite, so, we can change local var after its value is stored
        if role == 'volunteer':
            role = 'citizen'
        # flag: if the player is inside any building
        self.inside = False

        self.frames = {'left': [], 'right': []}
        self.frames['left'].append(
            pygame.transform.flip(load_image(f'data/characters/{role}_right_5.png', size=(80, 110)), 1, 0))
        self.frames['right'].append(
            load_image(f'data/characters/{role}_right_5.png', size=(80, 110)))

        self.image = self.frames['right'][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        self.prev_coords = x, y
        self.is_moving = False
        self.grav = 0
        self.is_jumping = False
        self.clock = pygame.time.Clock()
        self.side = 'left'

        self.health = 100
        self.hazard_risk = 0
        self.danger_level = 1
        self.hazard_timer = 0
        self.id = None

        self.card_money = 2500
        self.cash = 5000

        # generating pin
        self.objects = []
        pin = str(randint(1000, 9999))
        products['card'].description = (r'Пин код:\n' + str(pin)).split(r'\n')
        products['card'].pin = pin
        self.objects.append(products['card'])

        self.infected = 1

        if self.role == 'citizen':
            self.infection_rate = 1250
        else:
            self.infection_rate = 2000

        self.order = None
        self.id = None
        self.name = None

    def get_objects(self):
        return self.objects

    def add_objects(self, *objects):
        global score
        score += 10 * len(objects)
        for i in objects:
            self.objects.append(i)

    def get_cash(self):
        return self.cash

    def set_cash(self, value):
        self.cash = value

    def give_money(self, amount):
        if amount <= self.cash:
            self.cash -= amount
            return True
        return False

    def set_card_money(self, value):
        self.card_money = value

    def get_card_money(self):
        return self.card_money

    def spend_money(self, amount):
        if amount <= self.card_money:
            self.card_money -= amount
            return True
        return False

    def set_position(self, pos):
        self.rect.x, self.rect.y = pos

    def set_moving(self, value):
        self.is_moving = value

    def get_coords(self):
        return self.rect.x, self.rect.y

    def get_card_balance(self):
        return self.card_money

    def is_obstacle(self):
        return False

    def move_left(self):
        self.side = 'left'
        self.image = self.frames[self.side][0]

        self.prev_coords = self.get_coords()
        self.rect.x -= Player.speed
        # it's the "auto jumping"
        # if we can jums so that move further, we just jump
        if check_collisions(self):
            self.rect.y -= 5
        if check_collisions(self):
            self.rect.y -= 10
        if check_collisions(self):
            self.rect.y -= 15
        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def move_right(self):
        self.side = 'right'
        self.image = self.frames[self.side][0]
        self.rect.x += Player.speed
        if check_collisions(self):
            self.rect.y -= 5
        if check_collisions(self):
            self.rect.y -= 10
        if check_collisions(self):
            self.rect.y -= 15
        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def move_down(self, value):
        self.prev_coords = self.get_coords()
        self.rect.y -= value
        if check_collisions(self):
            if self.grav < -20:
                self.health -= abs(self.grav) - 10
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]
            self.grav = -5
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.grav = Player.jump_power
            self.is_jumping = True

    def render_info(self, color=(255, 255, 255), background=(0, 0, 0)):
        canvas = pygame.Surface((width // 2 + 350, 20))
        canvas.fill(background)
        font = pygame.font.Font(None, 30)
        canvas.blit(
            font.render(
                f'Здоровье: {self.health}%  Риск заражения: {self.hazard_risk}%  Наличные: {self.cash} Р   На карте: {self.card_money} Р  Баллы: {score}',
                1, color), (0, 0))
        return canvas

    # is called to get params of local client for transmittion
    def get_pos_info(self):
        x, y = str(self.rect.x - terrain.rect.x), str(self.rect.y - terrain.rect.y)
        if self.inside:
            x, y = '0', '0'
        res = self.role + r'\t' + x + r'\t' + y + r'\t' + str(
            self.is_moving) + r'\t' + self.side + r'\t' + str(self.infected)
        # print(res)
        return res

    # reducing health, increasing danger_level (risk of infection)
    def update_params(self):
        self.danger_level = 1 - (100 - self.health) / 100
        self.hazard_timer += self.clock.tick()
        if self.hazard_timer > self.infection_rate * self.danger_level:
            self.hazard_risk += 1
            self.hazard_timer = 0

        if self.health <= 0:
            self.health = 0
        if self.hazard_risk >= 100:
            self.hazard_risk = 100

        # cheking dead state (added gravity here, in this way we check if player is falling too fast)
        if self.health == 0 or self.grav < -50:
            screen.fill((0, 0, 0))
            # background_group.draw(screen)
            screen.blit(self.render_info(), (0, 0))
            text = render_text('Вы мертвы!!!')
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
            pygame.display.flip()
            for i in range(5):
                self.clock.tick(1)
            exit_game()
        elif self.hazard_risk == 100:
            self.infected = 3

    def update(self, *args):
        self.move_down(self.grav)
        self.grav -= gravity

        self.update_params()


class Terrain(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/textures/city_platforms.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def is_obstacle(self):
        return True


# building
# such mark (comment above) is used to tip the class is:
# class contains main func enter, called when player enters the building
# inside the method is big loop with its own groups, sprites, gameplay etc
class Bank(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/bank.png', size=(300, 250))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        # name is displayed when player is near
        self.name = 'Банк'

    def is_obstacle(self):
        return False

    def enter(self):
        logging.info('enter Bank')
        button_group.empty()
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
        running = True

        mode = ''
        right_pin = products['card'].pin
        current_pin = ''
        deposit_summ = ''

        main_display = pygame.Surface((width // 2, height // 3 + 150))
        main_display.fill((0, 0, 0))

        card_size = (100, 150)
        card = Button(width - card_size[0], height - card_size[1], *card_size,
                      load_image('data/objects/bank_card.png', size=card_size), None, 'card', bank_buttons)
        card_moving = False
        hole_rect = pygame.Rect(888, 107, 300, 20)

        # buttons adding eith specific ids and mainly with None instead of func
        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, None, bank_buttons)

        Button(50, 100, 50, 50, images['right_arrow'], None, 'first', bank_buttons)
        Button(50, 200, 50, 50, images['right_arrow'], None, 'second', bank_buttons)
        Button(50, 300, 50, 50, images['right_arrow'], None, 'third', bank_buttons)

        Button(100 + main_display.get_width(), 100, 50, 50, images['left_arrow'], None, 'fourth', bank_buttons)
        Button(100 + main_display.get_width(), 200, 50, 50, images['left_arrow'], None, 'fifth', bank_buttons)
        Button(100 + main_display.get_width(), 300, 50, 50, images['left_arrow'], None, 'sixth', bank_buttons)

        # buttons with special images
        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('1', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 470, 50, 50, image, None, '1', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('2', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 470, 50, 50, image, None, '2', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('3', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 470, 50, 50, image, None, '3', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('4', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 545, 50, 50, image, None, '4', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('5', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 545, 50, 50, image, None, '5', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('6', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 545, 50, 50, image, None, '6', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('7', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 620, 50, 50, image, None, '7', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('8', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 620, 50, 50, image, None, '8', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('9', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 620, 50, 50, image, None, '9', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('0', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 670, 50, 50, image, None, '0', bank_buttons)

        image = load_image('data/objects/long_button.png')
        image.blit(render_text('Enter', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 3, 620, 208, 47, image, None, 'enter', bank_buttons)

        image = load_image('data/objects/long_button.png')
        image.blit(render_text('Clear', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 3, 545, 208, 47, image, None, 'clear', bank_buttons)

        # strucrure: in case of game button is pressed, we check id and change mode var
        # in the drawing section we draw all bank sprites according to the mode var
        # so, we can devide interface in several stages
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEMOTION:
                    if card_moving:
                        card.rect.x, card.rect.y = event.pos

                    if card.rect.colliderect(hole_rect):
                        mode = 'pin'
                        bank_buttons.remove(card)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in bank_buttons:
                        if btn.rect.collidepoint(event.pos):
                            if not btn.id:
                                running = btn.run()
                            elif btn.id == 'card':
                                card_moving = True
                                card.rect.x, card.rect.y = event.pos
                            elif btn.id == 'clear':
                                current_pin = ''
                                deposit_summ = ''
                            elif btn.id.isdigit() and mode == 'pin':
                                current_pin += btn.id
                                if len(current_pin) == 4 and current_pin == right_pin:
                                    mode = 'main'
                                    current_pin = ''
                            elif mode == 'main':
                                if btn.id == 'first':
                                    mode = 'balance'
                                elif btn.id == 'second':
                                    mode = 'deposit'
                            elif mode == 'balance':
                                if btn.id == 'sixth':
                                    mode = 'main'
                            elif mode == 'deposit':
                                if btn.id == 'enter':
                                    # validate number and top the balance
                                    if deposit_summ.isdigit() and player.give_money(int(deposit_summ)):
                                        player.card_money += int(deposit_summ)
                                        logging.info('added' + str(deposit_summ) + 'successfully')
                                        mode = 'success'
                                    else:
                                        mode = 'error'
                                    deposit_summ = ''
                                elif btn.id.isdigit():
                                    deposit_summ += btn.id
                            elif mode == 'error' or mode == 'success':
                                mode = 'main'
                            button_group.empty()
                            pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)
            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

            # drawing section
            main_display.fill((0, 0, 0))
            if mode == 'pin':
                main_display.blit(render_text('Введите пин код:', color=(232, 208, 79)),
                                  (main_display.get_width() // 4, main_display.get_height() // 2 - 50))
                main_display.blit(render_text(('_' * (4 - len(current_pin))).rjust(4, '*'), color=(232, 208, 79)),
                                  (main_display.get_width() // 2, main_display.get_height() // 2))
            elif mode == 'main':
                main_display.blit(render_text('Показать баланс', color=(232, 208, 79)), (60, 30))
                main_display.blit(render_text('Внести наличные', color=(232, 208, 79)), (60, 130))
            elif mode == 'balance':
                main_display.blit(
                    render_text(f'Ваш баланс: {player.get_card_balance()} рублей', color=(232, 208, 79)),
                    (0, main_display.get_height() // 3))
                main_display.blit(render_text('Назад', color=(232, 208, 79)), (main_display.get_width() - 125, 250))
            elif mode == 'success':
                main_display.blit(render_text('Успешно!', color=(232, 208, 79)),
                                  (main_display.get_width() // 3, main_display.get_height() // 2))
            elif mode == 'error':
                main_display.blit(render_text('Ошибка!', color=(232, 208, 79)),
                                  (main_display.get_width() // 3, main_display.get_height() // 2))
            elif mode == 'deposit':
                main_display.blit(render_text('Введите сумму:', color=(232, 208, 79)),
                                  (main_display.get_width() // 4, main_display.get_height() // 2 - 50))
                main_display.blit(render_text(deposit_summ, color=(232, 208, 79)),
                                  (main_display.get_width() // 2, main_display.get_height() // 2))

            screen.fill((156, 65, 10))
            player.update_params()
            button_group.draw(screen)
            bank_buttons.draw(screen)
            screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
            screen.blit(main_display, (100, 70))
            pygame.draw.rect(screen, (0, 0, 0), hole_rect)
            pygame.display.flip()
            clock.tick(fps)
        # cleaning groups at the end
        bank_buttons.empty()
        button_group.empty()


# building
class MainHouse(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/main_house.png', size=(250, 500))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Дом'

        self.clock = pygame.time.Clock()

    def is_obstacle(self):
        return False

    def enter(self):
        # structure: depending on the player's role room (bed, etc) or
        # special delivery terminal for volunteers is displayed
        # room interface is devided to room and terminal (for creatn orders)
        logging.info('entered main house:  ' + player.role)

        def play_radio_info():
            speeches['news'].play()
            return True

        def simple_house():
            def order_terminal():
                # similar to bank terminal
                if player.role != 'citizen':
                    return
                global orders, score, error_code

                running = True
                mode = 'main'
                if player.order:
                    mode = 'Заказ уже оформлен'
                current_order = None

                main_display = pygame.Surface((width // 2, height // 3 + 150))
                main_display.fill((0, 0, 0))

                Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                       100, 50, images['exit_sign'], lambda: False, None, bank_buttons)

                Button(50, 100, 50, 50, images['right_arrow'], None, 'first', bank_buttons)
                Button(50, 200, 50, 50, images['right_arrow'], None, 'second', bank_buttons)
                Button(50, 300, 50, 50, images['right_arrow'], None, 'third', bank_buttons)

                Button(100 + main_display.get_width(), 100, 50, 50, images['left_arrow'], None, 'fourth',
                       bank_buttons)
                Button(100 + main_display.get_width(), 200, 50, 50, images['left_arrow'], None, 'fifth',
                       bank_buttons)
                Button(100 + main_display.get_width(), 300, 50, 50, images['left_arrow'], None, 'sixth',
                       bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('1', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4, 470, 50, 50, image, None, '1', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('2', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75, 470, 50, 50, image, None, '2', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('3', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75 * 2, 470, 50, 50, image, None, '3', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('4', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4, 545, 50, 50, image, None, '4', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('5', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75, 545, 50, 50, image, None, '5', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('6', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75 * 2, 545, 50, 50, image, None, '6', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('7', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4, 620, 50, 50, image, None, '7', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('8', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75, 620, 50, 50, image, None, '8', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('9', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75 * 2, 620, 50, 50, image, None, '9', bank_buttons)

                image = load_image('data/objects/digit_button.png')
                image.blit(render_text('0', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75, 670, 50, 50, image, None, '0', bank_buttons)

                image = load_image('data/objects/long_button.png')
                image.blit(render_text('Enter', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75 * 3, 620, 208, 47, image, None, 'enter',
                       bank_buttons)

                image = load_image('data/objects/long_button.png')
                image.blit(render_text('Clear', color=(0, 0, 0)), (10, 5))
                Button(100 + main_display.get_width() // 4 + 75 * 3, 545, 208, 47, image, None, 'clear',
                       bank_buttons)

                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            exit_game()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for btn in bank_buttons:
                                if btn.rect.collidepoint(event.pos):
                                    if not btn.id:
                                        running = btn.run()
                                    elif mode == 'main':  # author choice
                                        if btn.id == 'first':
                                            mode = 'order'
                                    elif mode == 'order' and btn.id == 'sixth':
                                        mode = 'final'

                                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu,
                                                          button_group)
                    data = pygame.key.get_pressed()
                    player.set_moving(False)
                    if data[27]:
                        menu(pause=True)
                        button_group.empty()
                        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None,
                                              button_group)
                    if mode == 'order' and not current_order:
                        # generating order
                        goods = ['Маска', 'Спирт', 'Мыло', 'Картофель', 'Яблоко', 'Витамины']
                        current_order = {'token': internal_id,
                                         'goods': []}
                        for i in range(3):
                            product = choice(goods)
                            current_order['goods'].append(product)
                            goods.remove(product)
                        current_order['goods'] = ', '.join(current_order['goods'])

                    if mode == 'final' and current_order:
                        # sending order to server and proceeding response
                        logging.info('creating order...')
                        url = f'http://{host}:{api_port}/game_api/create_order'
                        try:
                            response = requests.get(url, params=current_order, timeout=1.).json()
                            logging.info('success:' + str(current_order))
                        except requests.exceptions.ConnectionError:
                            error_code = -5
                            exit_game()
                        except requests.exceptions.Timeout:
                            error_code = -6
                            exit_game()
                        if not response['success']:
                            error_code = -7
                            exit_game()

                        mode = 'success'
                        current_order = None
                        player.order = response['token']

                    main_display.fill((0, 0, 0))
                    if mode == 'main':
                        main_display.blit(
                            render_text('Заказать', color=(232, 208, 79)),
                            (main_display.get_width() // 8, main_display.get_height() // 2 - 50 * 2))
                    elif mode == 'order':
                        for i in range(len(current_order['goods'].split(', '))):
                            main_display.blit(
                                render_text(current_order['goods'].split(', ')[i], color=(232, 208, 79)),
                                (main_display.get_width() // 8, main_display.get_height() // 2 - 50 + 35 * i))
                        main_display.blit(
                            render_text('Подтвердить', color=(232, 208, 79)),
                            (main_display.get_width() - 250, 300))
                    elif mode == 'success':
                        main_display.blit(
                            render_text('Успешно!', color=(232, 208, 79)),
                            (main_display.get_width() - 250, 300))
                    else:
                        main_display.blit(
                            render_text(mode, color=(232, 208, 79)),
                            (main_display.get_width() // 3, main_display.get_height() // 2))

                    screen.fill((156, 65, 10))
                    player.update_params()
                    button_group.draw(screen)
                    bank_buttons.draw(screen)
                    screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
                    screen.blit(main_display, (100, 70))
                    pygame.display.flip()
                    clock.tick(fps)

            radio = Button(width - 350, height // 2 - 137, 170, 145, images['radio'], play_radio_info, None,
                           house_buttons)
            monitor = Button(width - 250, height // 2 - 100, 170, 100, images['monitor'], order_terminal, None,
                             house_buttons)

            backgr = pygame.sprite.Sprite(background_house)
            backgr.image = load_image('data/inside/room.png', size=size)
            backgr.rect = backgr.image.get_rect()

            running = True

            Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                   100, 50, images['exit_sign'], lambda: False, None, house_buttons)
            thread_num = 0
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in house_buttons:
                            if btn.rect.collidepoint(event.pos):
                                running = btn.run()

                data = pygame.key.get_pressed()
                player.set_moving(False)
                if data[27]:
                    menu(pause=True)
                    button_group.empty()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, house_buttons)
                if player.order == 'done':
                    logging.info('order delivered')
                    screen.fill((177, 170, 142))
                    text = render_text('Заказ доставлен. Вы спасены! =)')
                    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
                    pygame.display.flip()
                    global score
                    score += 50
                    for i in range(5):
                        clock.tick(1)
                    player.order = None

                screen.fill((177, 170, 142))
                background_house.draw(screen)
                button_group.draw(screen)
                house_buttons.draw(screen)
                house_group.draw(screen)
                screen.blit(player.render_info(background=(177, 170, 142)), (0, 0))
                pygame.display.flip()
                clock.tick(fps)
                thread_num += 1
                if thread_num >= 200:
                    threading.Thread(target=check_order_is_done).start()
                    thread_num = 0

        def delivery_terminal():
            # very-very similar to the bank
            global orders, score, error_code
            running = True
            mode = 'main'

            if orders:
                shuffle(orders)
            else:
                mode = 'нет заказов'

            main_display = pygame.Surface((width // 2, height // 3 + 150))
            main_display.fill((0, 0, 0))

            Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                   100, 50, images['exit_sign'], lambda: False, None, bank_buttons)

            Button(50, 100, 50, 50, images['right_arrow'], None, 'first', bank_buttons)
            Button(50, 200, 50, 50, images['right_arrow'], None, 'second', bank_buttons)
            Button(50, 300, 50, 50, images['right_arrow'], None, 'third', bank_buttons)

            Button(100 + main_display.get_width(), 100, 50, 50, images['left_arrow'], None, 'fourth', bank_buttons)
            Button(100 + main_display.get_width(), 200, 50, 50, images['left_arrow'], None, 'fifth', bank_buttons)
            Button(100 + main_display.get_width(), 300, 50, 50, images['left_arrow'], None, 'sixth', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('1', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4, 470, 50, 50, image, None, '1', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('2', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75, 470, 50, 50, image, None, '2', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('3', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75 * 2, 470, 50, 50, image, None, '3', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('4', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4, 545, 50, 50, image, None, '4', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('5', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75, 545, 50, 50, image, None, '5', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('6', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75 * 2, 545, 50, 50, image, None, '6', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('7', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4, 620, 50, 50, image, None, '7', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('8', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75, 620, 50, 50, image, None, '8', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('9', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75 * 2, 620, 50, 50, image, None, '9', bank_buttons)

            image = load_image('data/objects/digit_button.png')
            image.blit(render_text('0', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75, 670, 50, 50, image, None, '0', bank_buttons)

            image = load_image('data/objects/long_button.png')
            image.blit(render_text('Enter', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75 * 3, 620, 208, 47, image, None, 'enter', bank_buttons)

            image = load_image('data/objects/long_button.png')
            image.blit(render_text('Clear', color=(0, 0, 0)), (10, 5))
            Button(100 + main_display.get_width() // 4 + 75 * 3, 545, 208, 47, image, None, 'clear', bank_buttons)

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in bank_buttons:
                            if btn.rect.collidepoint(event.pos):
                                if not btn.id:
                                    running = btn.run()
                                elif mode == 'main':  # author choice
                                    if btn.id == 'first' and len(orders) >= 1:
                                        mode = '0'
                                    elif btn.id == 'second' and len(orders) >= 2:
                                        mode = '1'
                                    elif btn.id == 'third' and len(orders) >= 3:
                                        mode = '2'
                                if mode.isdigit():
                                    if player.order['nickname'] == orders[int(mode)]['nickname']:
                                        aims = orders[int(mode)]['goods']
                                        for i in player.get_objects():
                                            if i.name in aims:
                                                aims.remove(i.name)
                                        if not aims:
                                            url = f'http://{host}:{api_port}/game_api/delete_order?user_token={player.order["token"]}'
                                            try:
                                                logging.info(f'deleting order of user token: {player.order["token"]}')
                                                response = requests.get(url, timeout=1.)
                                            except requests.exceptions.ConnectionError:
                                                error_code = -5
                                                exit_game()
                                            except requests.exceptions.Timeout:
                                                error_code = -6
                                                exit_game()
                                            if not response.json()['success']:
                                                error_code = -7
                                                exit_game()

                                            player.order = None
                                            player.card_money += 750
                                            score += 500
                                            mode = 'Успешно'
                                            logging.info('order delivered successfully')
                                        else:
                                            mode = 'Неполная комплектация'
                                            logging.info('few goods')
                                    else:
                                        mode = 'Неверный адрес'
                                        logging.info('wrong address')

                                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)
                data = pygame.key.get_pressed()
                player.set_moving(False)
                if data[27]:
                    menu(pause=True)
                    button_group.empty()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
                main_display.fill((0, 0, 0))
                if mode == 'main':
                    for i in range(len(orders)):
                        main_display.blit(
                            render_text(orders[i]['nickname'], color=(232, 208, 79)),
                            (main_display.get_width() // 8, 100 + 100 * i))
                else:
                    main_display.blit(
                        render_text(mode, color=(232, 208, 79)),
                        (main_display.get_width() // 5, main_display.get_height() // 2))
                    if mode == 'Успешно':
                        orders = []

                screen.fill((156, 65, 10))
                player.update_params()
                button_group.draw(screen)
                bank_buttons.draw(screen)
                screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
                screen.blit(main_display, (100, 70))
                pygame.display.flip()
                clock.tick(fps)

        button_group.empty()
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, house_buttons)

        if player.role == 'volunteer':
            delivery_terminal()
        else:
            simple_house()

        house_buttons.empty()
        house_group.empty()


# building
class Shop(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/shop_1.png', size=(250, 200))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Продуктовый магазин'

    def is_obstacle(self):
        return False

    def enter(self):
        logging.info('entered shop')

        # different interface for cheking out (brown background and list of selected goods)
        def checkout():
            # reducing money and adding goods to the player's list
            def buy():
                summ = sum([i.get_price() for i in cart])
                if player.spend_money(summ):
                    player.add_objects(*cart)
                    logging.info('transaction success')
                    return False, True, 'success'
                logging.info('transaction error')
                return False, True, 'error'

            running = True
            shop_buttons.empty()
            Button(width // 3, height - 100, 200, 50, render_text('Назад'), lambda: (False, True, 'ok'), None,
                   shop_buttons)
            Button(width // 3 * 2, height - 100, 200, 50, render_text('Купить'), buy, None, shop_buttons)

            Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                   100, 50, images['exit_sign'], lambda: (False, False, 'ok'), None, shop_buttons)

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in shop_buttons:
                            if btn.rect.collidepoint(event.pos):
                                running, run, status = btn.run()
                data = pygame.key.get_pressed()
                player.set_moving(False)
                if data[27]:
                    menu(pause=True)
                    button_group.empty()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

                screen.fill((156, 65, 10))
                shop_buttons.draw(screen)
                screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
                # rendering list of selected goods
                for num in range(len(cart)):
                    screen.blit(render_text(f'{num + 1} -- {cart[num].name} ------ {cart[num].get_price()}'),
                                (width // 2, height // 2 - 200 + 35 * num))
                pygame.display.flip()
                clock.tick(fps)
            shop_buttons.empty()
            return run, status

        button_group.empty()
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, pharm_buttons)

        backgr = pygame.sprite.Sprite(background_shop)
        backgr.image = load_image('data/inside/shop_1_inside.png', size=size)
        backgr.rect = backgr.image.get_rect()

        running = True

        # every products has flag can_be_bought (switches to False after successful transaction)
        # only if player if a policwman or a citizen
        carrot = products['carrot']
        if carrot.can_be_bought():
            carrot.set_pos((350, 180))
            carrot.add_to_groups(shop_products)

        potato = products['potato']
        if potato.can_be_bought():
            potato.set_pos((550, 180))
            potato.add_to_groups(shop_products)

        apple = products['apple']
        if apple.can_be_bought():
            apple.set_pos((350, 300))
            apple.add_to_groups(shop_products)

        cart = []
        cart_rect = pygame.Rect(950, 300, 150, 450)

        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, None, shop_buttons)
        status = 'ok'
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in shop_buttons:
                        if btn.rect.collidepoint(event.pos):
                            running = btn.run()
                    for product in shop_products:
                        if product.rect.collidepoint(event.pos):
                            cart.append(product)
                            for i in cart:
                                i.reset_groups()
                    if cart_rect.collidepoint(event.pos):
                        running, status = checkout()
                        if status == 'success':
                            cart = []
                        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                               100, 50, images['exit_sign'], lambda: False, None, shop_buttons)
                        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, shop_buttons)

            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

            screen.fill((156, 65, 10))
            player.update_params()
            background_shop.draw(screen)
            button_group.draw(screen)
            shop_buttons.draw(screen)
            shop_group.draw(screen)
            shop_products.draw(screen)
            if status == 'error':
                screen.blit(render_text('Недостаточно средств! Посетите банк!', color=(255, 0, 0)), (200, 100))
            screen.blit(player.render_info(background=(179, 185, 206)), (0, 0))
            pygame.display.flip()
            clock.tick(fps)
        shop_buttons.empty()
        shop_group.empty()
        shop_products.empty()
        logging.info('left shop')


# building
# shop (watch shop comments above)
class SecondShop(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/shop_2.png', size=(250, 200))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Хозяйственный магазин'

    def is_obstacle(self):
        return False

    def enter(self):
        logging.info('entered second shop')

        def checkout():
            def buy():
                summ = sum([i.get_price() for i in cart])
                if player.spend_money(summ):
                    player.add_objects(*cart)
                    return False, True, 'success'
                return False, True, 'error'

            running = True
            shop_buttons.empty()
            Button(width // 3, height - 100, 200, 50, render_text('Назад'), lambda: (False, True, 'ok'), None,
                   shop_buttons)
            Button(width // 3 * 2, height - 100, 200, 50, render_text('Купить'), buy, None, shop_buttons)

            Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                   100, 50, images['exit_sign'], lambda: (False, False, 'ok'), None, shop_buttons)

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in shop_buttons:
                            if btn.rect.collidepoint(event.pos):
                                running, run, status = btn.run()
                data = pygame.key.get_pressed()
                player.set_moving(False)
                if data[27]:
                    menu(pause=True)
                    button_group.empty()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

                screen.fill((156, 65, 10))
                shop_buttons.draw(screen)
                screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
                for num in range(len(cart)):
                    screen.blit(render_text(f'{num + 1} -- {cart[num].name} ------ {cart[num].get_price()}'),
                                (width // 2, height // 2 - 200 + 35 * num))
                pygame.display.flip()
                clock.tick(fps)
            shop_buttons.empty()
            return run, status

        button_group.empty()
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, pharm_buttons)

        backgr = pygame.sprite.Sprite(background_shop)
        backgr.image = load_image('data/inside/shop_2_inside.png', size=size)
        backgr.rect = backgr.image.get_rect()

        running = True

        soap = products['soap']
        if soap.can_be_bought():
            soap.set_pos((950, 180))
            soap.add_to_groups(shop_products)

        cart = []
        cart_rect = pygame.Rect(300, 327, 80, 200)

        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, None, shop_buttons)
        status = 'ok'
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in shop_buttons:
                        if btn.rect.collidepoint(event.pos):
                            running = btn.run()
                    for product in shop_products:
                        if product.rect.collidepoint(event.pos):
                            cart.append(product)
                            for i in cart:
                                i.reset_groups()
                    if cart_rect.collidepoint(event.pos):
                        a = 1
                        running, status = checkout()
                        if status == 'success':
                            cart = []
                        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                               100, 50, images['exit_sign'], lambda: False, None, shop_buttons)
                        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, shop_buttons)

            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

            screen.fill((156, 65, 10))
            player.update_params()
            background_shop.draw(screen)
            button_group.draw(screen)
            shop_buttons.draw(screen)
            shop_group.draw(screen)
            shop_products.draw(screen)
            if status == 'error':
                screen.blit(render_text('Недостаточно средств! Посетите банк!', color=(255, 0, 0)), (200, 100))
            screen.blit(player.render_info(background=(179, 185, 206)), (0, 0))
            pygame.display.flip()
            clock.tick(fps)
        shop_buttons.empty()
        shop_group.empty()
        shop_products.empty()
        logging.info('left second shop')


# building
# shop (watch shop comments above)
class Pharmacy(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/pharmacy.png', size=(250, 200))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Аптека'

    def is_obstacle(self):
        return False

    def enter(self):
        logging.info('entered pharmacy')

        def checkout():
            def buy():
                summ = sum([i.get_price() for i in cart])
                if player.spend_money(summ):
                    player.add_objects(*cart)
                    return False, True, 'success'
                return False, True, 'error'

            running = True
            pharm_buttons.empty()
            Button(width // 3, height - 100, 200, 50, render_text('Назад'), lambda: (False, True, 'ok'), None,
                   pharm_buttons)
            Button(width // 3 * 2, height - 100, 200, 50, render_text('Купить'), buy, None, pharm_buttons)

            Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                   100, 50, images['exit_sign'], lambda: (False, False, 'ok'), None, pharm_buttons)

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in pharm_buttons:
                            if btn.rect.collidepoint(event.pos):
                                running, run, status = btn.run()
                data = pygame.key.get_pressed()
                player.set_moving(False)
                if data[27]:
                    menu(pause=True)
                    button_group.empty()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

                screen.fill((156, 65, 10))
                pharm_buttons.draw(screen)
                screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
                for num in range(len(cart)):
                    screen.blit(render_text(f'{num + 1} -- {cart[num].name} ------ {cart[num].get_price()}'),
                                (width // 2, height // 2 - 200 + 35 * num))
                pygame.display.flip()
                clock.tick(fps)
            pharm_buttons.empty()
            return run, status

        button_group.empty()
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, pharm_buttons)

        backgr = pygame.sprite.Sprite(background_pharm)
        backgr.image = load_image('data/inside/pharmacy_inside.png', size=size)
        backgr.rect = backgr.image.get_rect()

        running = True

        bottle = products['alcohol']
        if bottle.can_be_bought():
            bottle.set_pos((350, 180))
            bottle.add_to_groups(pharm_products)

        mask = products['mask']
        if mask.can_be_bought():
            mask.set_pos((550, 180))
            mask.add_to_groups(pharm_products)

        pills = products['pills']
        if pills.can_be_bought():
            pills.set_pos((750, 180))
            pills.add_to_groups(pharm_products)

        cart = []
        cart_rect = pygame.Rect(950, 300, 150, 450)

        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, None, pharm_buttons)
        status = 'ok'
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in pharm_buttons:
                        if btn.rect.collidepoint(event.pos):
                            running = btn.run()
                    for product in pharm_products:
                        if product.rect.collidepoint(event.pos):
                            cart.append(product)
                            for i in cart:
                                i.reset_groups()
                    if cart_rect.collidepoint(event.pos):
                        running, status = checkout()
                        if status == 'success':
                            cart = []
                        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
                               100, 50, images['exit_sign'], lambda: False, None, pharm_buttons)
                        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, pharm_buttons)

            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

            screen.fill((156, 65, 10))
            player.update_params()
            background_pharm.draw(screen)
            button_group.draw(screen)
            pharm_buttons.draw(screen)
            pharm_group.draw(screen)
            pharm_products.draw(screen)
            if status == 'error':
                screen.blit(render_text('Недостаточно средств! Посетите банк!', color=(255, 0, 0)), (200, 100))
            screen.blit(player.render_info(background=(179, 185, 206)), (0, 0))
            pygame.display.flip()
            clock.tick(fps)
        pharm_buttons.empty()
        pharm_group.empty()
        logging.info('left pharmacy')


# building
# not used in the single mode
# player can get a test result (if he is infected or not)
# similar to bank terminal
class Hospital(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/hospital.png', size=(370, 340))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Больница'

    def is_obstacle(self):
        return False

    def enter(self):
        logging.info('entered hospital')
        global score
        button_group.empty()
        if player.role != 'citizen':
            return
        if player.infected != 1:
            return
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
        running = True

        mode = 'main'
        current_year = ''
        math = ''
        answer = ''
        right_answer = ''

        main_display = pygame.Surface((width // 2, height // 3 + 150))
        main_display.fill((0, 0, 0))

        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, None, bank_buttons)

        Button(50, 100, 50, 50, images['right_arrow'], None, 'first', bank_buttons)
        Button(50, 200, 50, 50, images['right_arrow'], None, 'second', bank_buttons)
        Button(50, 300, 50, 50, images['right_arrow'], None, 'third', bank_buttons)

        Button(100 + main_display.get_width(), 100, 50, 50, images['left_arrow'], None, 'fourth', bank_buttons)
        Button(100 + main_display.get_width(), 200, 50, 50, images['left_arrow'], None, 'fifth', bank_buttons)
        Button(100 + main_display.get_width(), 300, 50, 50, images['left_arrow'], None, 'sixth', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('1', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 470, 50, 50, image, None, '1', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('2', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 470, 50, 50, image, None, '2', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('3', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 470, 50, 50, image, None, '3', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('4', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 545, 50, 50, image, None, '4', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('5', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 545, 50, 50, image, None, '5', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('6', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 545, 50, 50, image, None, '6', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('7', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 620, 50, 50, image, None, '7', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('8', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 620, 50, 50, image, None, '8', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('9', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 620, 50, 50, image, None, '9', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('0', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 670, 50, 50, image, None, '0', bank_buttons)

        image = load_image('data/objects/long_button.png')
        image.blit(render_text('Enter', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 3, 620, 208, 47, image, None, 'enter', bank_buttons)

        image = load_image('data/objects/long_button.png')
        image.blit(render_text('Clear', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 3, 545, 208, 47, image, None, 'clear', bank_buttons)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in bank_buttons:
                        if btn.rect.collidepoint(event.pos):
                            if not btn.id:
                                running = btn.run()
                            elif mode == 'error' or btn.id == 'clear':
                                current_year = ''
                                answer = ''
                                if mode == 'error':
                                    mode = 'main'
                                    math = ''
                            elif mode == 'main' and btn.id.isdigit():
                                current_year += btn.id
                            elif btn.id == 'enter' and mode == 'main':
                                if len(current_year) != 4:
                                    mode = 'error'
                                else:
                                    # the second stage is math (adding to 3-digit numbers)
                                    mode = 'math'
                                    a = randint(100, 999)
                                    b = randint(100, 999)
                                    right_answer = str(a + b)
                                    math = f'{a} + {b}'
                            elif mode == 'math' and btn.id.isdigit():
                                answer += btn.id
                            elif mode == 'math' and btn.id == 'enter':
                                if right_answer == answer:
                                    logging.info('math answer right')
                                    # infection probability value here
                                    # after getting result we set state to the player
                                    if random() < 0.75:
                                        player.infected = 3
                                        mode = 'infected'
                                        logging.info('set infected')
                                    else:
                                        mode = 'ok'
                                        player.infected = 2
                                        logging.info('set not infected')
                                else:
                                    logging.info('math answer wrong')
                                    mode = 'error'

                            pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)
            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

            main_display.fill((0, 0, 0))
            if mode == 'main':
                main_display.blit(
                    render_text('Введите ваш год рождения,', color=(232, 208, 79)),
                    (main_display.get_width() // 8, main_display.get_height() // 2 - 50))
                main_display.blit(
                    render_text('если вы хотите сдать анализы', color=(232, 208, 79)),
                    (main_display.get_width() // 8, main_display.get_height() // 2))

                main_display.blit(render_text(('_' * (4 - len(current_year))).rjust(4, '*'), color=(232, 208, 79)),
                                  (main_display.get_width() // 2, main_display.get_height() // 2 + 50))
            elif mode == 'math':
                main_display.blit(render_text('Решите простой пример, ', color=(232, 208, 79)),
                                  (main_display.get_width() // 8, main_display.get_height() // 2 - 50))
                main_display.blit(render_text('пока Ваши анализы готовятся...', color=(232, 208, 79)),
                                  (main_display.get_width() // 8, main_display.get_height() // 2))

                main_display.blit(render_text(math, color=(232, 208, 79)),
                                  (main_display.get_width() // 8, main_display.get_height() // 2 + 50))

                main_display.blit(render_text(('_' * (4 - len(answer))).rjust(4, '*'), color=(232, 208, 79)),
                                  (main_display.get_width() // 2, main_display.get_height() // 2 + 100))
            elif mode == 'error':
                main_display.blit(
                    render_text('Ошибка! Попробуйте снова;)', color=(232, 208, 79)),
                    (main_display.get_width() // 4, main_display.get_height() // 2 - 50))
            elif mode == 'infected':
                main_display.blit(render_text('Вы инфецированы и заразны!', color=(232, 208, 79), size=35),
                                  (10, main_display.get_height() // 2 - 50))
                main_display.blit(render_text('Срочно необходима строгая изоляция!', color=(232, 208, 79), size=35),
                                  (10, main_display.get_height() // 2))

            elif mode == 'ok':
                main_display.blit(render_text('Вы здоровы!', color=(232, 208, 79)),
                                  (main_display.get_width() // 4, main_display.get_height() // 2 - 50))
                main_display.blit(render_text('Но мы советуем оставаться дома!', color=(232, 208, 79)),
                                  (main_display.get_width() // 8, main_display.get_height() // 2))

            screen.fill((156, 65, 10))
            player.update_params()
            button_group.draw(screen)
            bank_buttons.draw(screen)
            screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
            screen.blit(main_display, (100, 70))
            pygame.display.flip()
            clock.tick(fps)
        score += 100
        bank_buttons.empty()
        button_group.empty()
        logging.info('left hospital')


# building
# contains terminal (as well as bank)
# not used in the single mode
# players can pick up and order to deliver
class Volunteers(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/buildings/volunteers.png', size=(370, 340))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Штаб-квартира'

    def is_obstacle(self):
        return False

    def enter(self):
        logging.info('entered voulunteers')
        global orders, error_code
        orders = None
        button_group.empty()
        if player.role != 'volunteer':
            return
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

        running = True
        mode = 'main'

        main_display = pygame.Surface((width // 2, height // 3 + 150))
        main_display.fill((0, 0, 0))

        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, None, bank_buttons)

        Button(50, 100, 50, 50, images['right_arrow'], None, 'first', bank_buttons)
        Button(50, 200, 50, 50, images['right_arrow'], None, 'second', bank_buttons)
        Button(50, 300, 50, 50, images['right_arrow'], None, 'third', bank_buttons)

        Button(100 + main_display.get_width(), 100, 50, 50, images['left_arrow'], None, 'fourth', bank_buttons)
        Button(100 + main_display.get_width(), 200, 50, 50, images['left_arrow'], None, 'fifth', bank_buttons)
        Button(100 + main_display.get_width(), 300, 50, 50, images['left_arrow'], None, 'sixth', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('1', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 470, 50, 50, image, None, '1', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('2', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 470, 50, 50, image, None, '2', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('3', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 470, 50, 50, image, None, '3', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('4', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 545, 50, 50, image, None, '4', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('5', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 545, 50, 50, image, None, '5', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('6', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 545, 50, 50, image, None, '6', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('7', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4, 620, 50, 50, image, None, '7', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('8', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 620, 50, 50, image, None, '8', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('9', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 2, 620, 50, 50, image, None, '9', bank_buttons)

        image = load_image('data/objects/digit_button.png')
        image.blit(render_text('0', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75, 670, 50, 50, image, None, '0', bank_buttons)

        image = load_image('data/objects/long_button.png')
        image.blit(render_text('Enter', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 3, 620, 208, 47, image, None, 'enter', bank_buttons)

        image = load_image('data/objects/long_button.png')
        image.blit(render_text('Clear', color=(0, 0, 0)), (10, 5))
        Button(100 + main_display.get_width() // 4 + 75 * 3, 545, 208, 47, image, None, 'clear', bank_buttons)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in bank_buttons:
                        if btn.rect.collidepoint(event.pos):
                            if not btn.id:
                                running = btn.run()
                            elif mode == 'main':  # order choice
                                if btn.id == 'first' and len(orders) >= 1:
                                    mode = '0'
                                elif btn.id == 'second' and len(orders) >= 2:
                                    mode = '1'
                                elif btn.id == 'third' and len(orders) >= 3:
                                    mode = '2'
                            elif mode.isdigit() and btn.id == 'sixth':
                                # if submit button id pressed we set order to the playr's attr
                                player.order = orders[int(mode)]
                                mode = 'success'
                            pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)
            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
            if mode == 'main' and not orders:
                # at the beginning we get list of all oredrs from the server
                logging.info('getting orders')
                url = f'http://{host}:{api_port}/game_api/get_orders?user_token={internal_id}'
                try:
                    json_response = requests.get(url, timeout=1.).json()
                except requests.exceptions.Timeout:
                    error_code = -6
                    exit_game()
                except requests.exceptions.ConnectionError:
                    error_code = -5
                    exit_game()
                if not json_response['success']:
                    error_code = -7
                    exit_game()
                logging.info(f'response result: {json_response}')
                # take only 3 first
                orders = json_response['data'][:3]
                logging.info('got orders')
            main_display.fill((0, 0, 0))
            if mode == 'main':
                # display orders on the screen approximately to the right to the buttons
                for i in range(len(orders)):
                    main_display.blit(
                        render_text(orders[i]['nickname'], color=(232, 208, 79)),
                        (main_display.get_width() // 8, 100 + 100 * i))
            elif mode.isdigit():
                for i in range(len(orders[int(mode)]['goods'])):
                    main_display.blit(
                        render_text(orders[int(mode)]['goods'][i], color=(232, 208, 79)),
                        (main_display.get_width() // 8, main_display.get_height() // 2 - 50 + 35 * i))
                main_display.blit(
                    render_text('Принять', color=(232, 208, 79)),
                    (main_display.get_width() - 300, 300))
            elif mode == 'success':
                main_display.blit(
                    render_text('Успешно!', color=(232, 208, 79), size=65),
                    (main_display.get_width() // 2 - 75, main_display.get_height() // 2))

            screen.fill((156, 65, 10))
            player.update_params()
            button_group.draw(screen)
            bank_buttons.draw(screen)
            screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
            screen.blit(main_display, (100, 70))
            pygame.display.flip()
            clock.tick(fps)
        bank_buttons.empty()
        button_group.empty()
        logging.info('left voulunteers')


# instance of product for
# 1) generation at the game start from the file
# 2) drawing at the equipment and shop buildings
# 3) storage for the vars (health and infection risk addition)
class Product(pygame.sprite.Sprite):
    def __init__(self, x, y, name, image, price, describtion, *groups):
        super().__init__(groups)

        self.image = image
        self.small_image = pygame.transform.scale(self.image.copy(), (Equipment.cell_cize, Equipment.cell_cize))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = name
        self.price = price
        self.id = id
        self.description = describtion
        self.bought = False
        self.is_used = False
        self.pin = None

    def was_used(self):
        return self.is_used

    def can_be_bought(self):
        return not self.bought

    def buy(self):
        self.bought = True

    def set_pos(self, pos):
        self.rect.x, self.rect.y = pos

    def get_price(self):
        return self.price

    def get_info(self):
        return f'{self.name} за {self.price} рублей'

    def get_describtion(self):
        return self.description

    def get_id(self):
        return self.id

    def add_to_groups(self, *groups):
        for i in groups:
            i.add(self)

    def remove_from_groups(self, *groups):
        for i in groups:
            i.remove(self)

    def reset_groups(self):
        for i in self.groups():
            i.remove(self)

    def get_small_image(self):
        return self.small_image

    # renders name, price, description
    def render_info(self, background=(156, 65, 10), color=(255, 255, 255)):
        display = pygame.Surface((width // 2, height // 2 * 3))
        display.fill(background)
        # main image
        display.blit(self.image, (display.get_width() // 2 - self.image.get_width() // 2, 50))
        # main information about title and price
        display.blit(render_text(self.get_info(), color=color), (50, self.image.get_height() + 50 + 20))
        # info about effects
        pxl_num = 1
        for i in self.description:
            display.blit(render_text(i, color=color), (50, self.image.get_height() + 50 + 35 * pxl_num + 50))
            pxl_num += 1
        return display

    # changing health and infection risk and setting is_used flag
    def use(self):
        if self.name == 'Маска':
            player.infection_rate += 300
        elif self.name == 'Спирт':
            player.infection_rate += 250
        elif self.name == 'Мыло':
            player.infection_rate += 200
        elif self.name == 'Витамины':
            player.infection_rate += 100
        else:
            player.infection_rate += 50
            player.health += 10
            if player.health > 100:
                player.health = 100
        if self.name == 'Яблоко':
            sounds['apple'].play()
        self.is_used = True
        return True


# is displayed as an equipment interface
class Equipment:
    table_width = 4
    table_height = 4
    cell_cize = 100

    def __init__(self, player):
        self.products = player.get_objects()

    def enter(self):
        # func to clean and then display updates products again
        def reset():
            product_buttons.empty()
            for i in range(Equipment.table_height):
                for j in range(Equipment.table_width):
                    index = i * Equipment.table_width + j
                    if index >= len(self.products):
                        break
                    if not self.products[index].was_used():
                        # every displyed product is drawn as a button
                        Button(Equipment.cell_cize + Equipment.cell_cize * j,
                               Equipment.cell_cize + Equipment.cell_cize * i, Equipment.cell_cize, Equipment.cell_cize,
                               self.products[index].get_small_image(),
                               self.products[index].render_info, index, product_buttons)

        running = True

        reset()
        Button(width - images['exit_sign'].get_width(), height - images['exit_sign'].get_height(),
               100, 50, images['exit_sign'], lambda: False, 'exit', product_buttons)

        info_display = None
        use_btn = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in product_buttons:
                        if btn.rect.collidepoint(event.pos):
                            if btn.id == 'exit':
                                running = False
                            elif btn != use_btn:
                                info_display = btn.run()
                                if btn.id is not None:
                                    if use_btn:
                                        use_btn.kill()
                                    use_btn = Button(width - 300, height - 150, 300, 75, render_text('Использовать'),
                                                     self.products[int(btn.id)].use, None, product_buttons)
                            else:
                                btn.run()
                                reset()
                                if info_display:
                                    info_display.fill((156, 65, 10))
                if event.type == pygame.KEYUP:
                    if event.key == 9:  # TAB
                        running = False
            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[27]:
                menu(pause=True)
                button_group.empty()
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
            screen.fill((156, 65, 10))
            player.update_params()
            if info_display:
                screen.blit(info_display, (width // 2, 50))
            button_group.draw(screen)
            product_buttons.draw(screen)
            screen.blit(player.render_info(background=(156, 65, 10)), (0, 0))
            pygame.display.flip()
            clock.tick(fps)
        product_buttons.empty()


# class for the button instance
# x, y, w, h - coords and size int
# image is a picturem set to the sprite
# run func gets args and use them in the set func call
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image, func, id=None, *groups):
        groups = list(groups)
        super().__init__(groups)
        self.h = h
        self.w = w
        self.id = id
        self.image = image
        self.image.set_alpha(255)
        self.rect = self.image.get_rect()
        self.func = func
        self.rect.x, self.rect.y = x, y
        self.frames = [self.image] * 2
        self.frames[0].set_alpha(50)
        self.frames[1].set_alpha(300)
        self.image = self.frames[0]

    def run(self, *args):
        return self.func(*args)

    def check_selection(self, pos):
        if self.rect.collidepoint(pos):
            self.image = self.frames[1]
        else:
            self.image = self.frames[0]

    def is_obstacle(self):
        return False

    def update(self, *args):
        # struggle to change alpha channel when mouse pos is in the button rect
        if args:
            pos = args[0]
            self.image.set_alpha(100)
            if self.rect.collidepoint(pos):
                self.image.set_alpha(255)


# camera is moving together with the player
class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # moving obj (all sprites in for loop) on the delta
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # updating delta of coords (target is the main object, player, for example)
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = 0
        # camera moves up and down only if player is high enough (probably on the platform)
        if player.rect.y < 0 or player.rect.y > height - 100 or player.rect.y - terrain.rect.y < 650:
            self.dy = -(target.rect.y + target.rect.h // 2 - height // 2 - 150)


# func with several loops for main menu, settings menu
def menu(pause=False):
    global menu_is_on
    if menu_is_on:
        return
    else:
        menu_is_on = True
    delt_width = 75

    def start():
        return 'start'

    # settings loop
    def settings():
        # switching global flag and changing button image
        def sound_effect_switch():
            global effects_on
            effects_on = not effects_on
            label = f"Эффекты {'вкл' if effects_on else 'выкл'}"

            canvas = pygame.Surface((315, 100))
            canvas.fill((181, 109, 2))
            text = render_text(label)
            canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                               canvas.get_height() // 2 - text.get_height() // 2))

            effects_button.image = canvas

        # switching global flag and changing button image
        def music_switch():
            global music_on
            music_on = not music_on
            label = f"Музыка {'вкл' if music_on else 'выкл'}"
            canvas = pygame.Surface((315, 100))
            canvas.fill((181, 109, 2))
            text = render_text(label)
            canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                               canvas.get_height() // 2 - text.get_height() // 2))

            music_button.image = canvas
            if not music_on:
                for mu in music.values():
                    mu.stop()
            else:
                music['main'].play(-1)

        running = True
        pos = (0, 0)

        canvas = pygame.Surface((315, 100))
        canvas.fill((181, 109, 2))
        text = render_text(f"Музыка вкл")
        canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                           canvas.get_height() // 2 - text.get_height() // 2))

        music_button = Button(width // 2 - delt_width, height // 4, 315, 100, canvas,
                              music_switch, None, settings_buttons_group)

        canvas = pygame.Surface((315, 100))
        canvas.fill((181, 109, 2))
        text = render_text(f"Эффекты вкл")
        canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                           canvas.get_height() // 2 - text.get_height() // 2))

        effects_button = Button(width // 2 - delt_width, height // 4 * 2, 315, 100,
                                canvas, sound_effect_switch,
                                None, settings_buttons_group)

        canvas = pygame.Surface((315, 100))
        canvas.fill((181, 109, 2))
        text = render_text('Назад')
        canvas.blit(text, (
            canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))

        Button(width // 2 - delt_width, height // 4 * 3, 315, 100, canvas, lambda: 'back', None, settings_buttons_group)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for btn in settings_buttons_group:
                        if btn.rect.collidepoint(pos):
                            running = btn.run() != 'back'
            screen.fill((219, 146, 72, 100))
            settings_buttons_group.update(pos)
            settings_buttons_group.draw(screen)
            pygame.display.flip()
            clock.tick(fps)

    # main menu loop
    running = True
    pos = (0, 0)
    label = 'Продолжить'
    canvas = pygame.Surface((200, 100))
    canvas.fill((181, 109, 2))
    text = render_text(label)
    canvas.blit(text,
                (
                    canvas.get_width() // 2 - text.get_width() // 2,
                    canvas.get_height() // 2 - text.get_height() // 2))
    Button(width // 2 - delt_width, height // 4, 200, 100, canvas, start, None, button_group)

    canvas = pygame.Surface((200, 100))
    canvas.fill((181, 109, 2))
    text = render_text('Настройки')
    canvas.blit(text,
                (canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))
    Button(width // 2 - delt_width, height // 4 * 2, 200, 100, canvas, settings, None, button_group)

    canvas = pygame.Surface((200, 100))
    canvas.fill((181, 109, 2))
    text = render_text('Выход')
    canvas.blit(text,
                (canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))
    Button(width // 2 - delt_width, height // 4 * 3, 200, 100, canvas, exit_game, 'exit', button_group)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for btn in button_group:
                    if btn.rect.collidepoint(pos):
                        running = btn.run() != 'start'
        data = pygame.key.get_pressed()
        # if esc button is pressed break the loop and continue the game
        if data[9]:
            running = False
        screen.fill((219, 146, 72))
        button_group.update(pos)

        button_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    button_group.empty()
    settings_buttons_group.empty()
    # bug?
    menu_is_on = False
    # returns 1 not to break the main loop (note comments below)
    return 1


# generating all products from the .dat file
# it makes adding products far easier
with open('data/data_files/products.dat', mode='r', encoding='utf-8') as f:
    for i in f.readlines():
        # products params are joined with raw str '\t'
        # get params
        data = i.split(r'\t')
        # load image of the path from the file
        image = load_image(data[2], size=(50, 90))
        products[data[0]] = Product(0, 0, data[1], image, int(data[3]), data[4].split(r'\n'))
# default images
# rarely used, only images with general meaning
images = {'pause_button': load_image('data/other/pause_button.png', size=(50, 50)),
          'right_arrow': load_image('data/objects/arrow_button_right.png', size=(50, 50)),
          'left_arrow': load_image('data/objects/arrow_button_left.png', size=(50, 50)),
          'exit_sign': load_image('data/objects/exit_sign.png', size=(100, 50)),
          'room': load_image('data/inside/room.png', size=size),
          'radio': load_image('data/objects/radio.png'),
          'monitor': load_image('data/objects/monitor.png', size=(150, 100))}
images['pause_button'].set_alpha(100)
fps = 30
running = True
clock = pygame.time.Clock()
info_clock = pygame.time.Clock()
pos = (0, 0)

# menu func call is commented in multi mode and active in the sibgle mode
# menu()

backgr = pygame.sprite.Sprite(background_group)
backgr.image = load_image('data/textures/background.png', size=size)
backgr.rect = backgr.image.get_rect()

# player = Player(3850, 1050, input('enter role:     '), player_group)
# role = 'volunteer'

# generating all objects
player = Player(3850, 1000, role, player_group)
player.id = internal_id
player.name = player_name
terrain = Terrain(0, 0, all_sprites, terrain_group)
bank = Bank(350, 875, all_sprites, building_group)
home = MainHouse(3710, 700, building_group, all_sprites)
pharmacy = Pharmacy(5050, 675, building_group, all_sprites)
shop = Shop(5750, 665, building_group, all_sprites)
second_shop = SecondShop(7250, 750, building_group, all_sprites)
hospital = Hospital(2200, 800, building_group, all_sprites)
volunteer = Volunteers(1000, 790, building_group, all_sprites)

pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)

# print("client connected to server")

# starting connection and cleaning threads
thread = threading.Thread(target=operate_player_data)
thread.start()
cleaning_thread = threading.Thread(target=clean_params)
cleaning_thread.start()
# thread.join(0.01)
connect_tick = 0

camera = Camera()
camera.update(player)

scanner_on = False
arrest_rate = 0

# home.enter()

# all exceptions in the loop cause quit and all of exit_game func
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                pos = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in button_group:
                    if btn.rect.collidepoint(event.pos):
                        btn.run()
                        button_group.empty()
                        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
            if event.type == pygame.KEYUP:
                # disable scanner on KEYUP
                if player.role == 'policeman' and event.key == 99:
                    scanner_on = False
                if event.key == 9:  # TAB
                    eq = Equipment(player)
                    eq.enter()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
            # enable scanner on KEYDOWN
            if event.type == pygame.KEYDOWN:
                if player.role == 'policeman' and event.key == 99:
                    scanner_on = True

        data = pygame.key.get_pressed()

        # if any(data):
        # print(data.index(1))

        player.set_moving(False)
        # checking keyboard input
        if data[27]:
            menu(pause=True)
            button_group.empty()
            pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
        if data[101]:
            if near_building:
                player.inside = True
                if effects_on:
                    sounds['open_door'].play()
                near_building.enter()
                if effects_on:
                    sounds['close_door'].play()
                player.inside = False
                pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, None, button_group)
        if data[51]:
            if player.role == 'policeman':
                for i in remote_players:
                    try:
                        if pygame.sprite.collide_mask(i, player):
                            arrest_rate += 1
                            print(arrest_rate)
                            # score is changed according to the role of arrested player
                            if arrest_rate >= 60:
                                caught_ids.append(i.id)
                                if i.infected == 3:
                                    score += 100
                                elif i.role == 'policeman':
                                    score -= 120
                                elif i.role == 'volunteer':
                                    score -= 100
                                elif i.infected == 2:
                                    score -= 100
                                elif i.infected == 1:
                                    score -= 25
                                arrest_rate = 0
                    # AttrErr is risen if there were an error during RemotePlayer init
                    except AttributeError:
                        # we delete the instance with a trouble
                        if i.id in player_params.keys():
                            del player_params[i.id]
                            i.kill()
                    except Exception as e:
                        print(e)
        # check keyboard moving input
        if data[97]:
            player.move_left()
            player.set_moving(True)
        if data[100]:
            player.move_right()
            player.set_moving(True)
        if data[32]:
            player.jump()
        screen.fill((0, 0, 0))
        camera.update(player)
        # the same problem (AttrErr), watch the comment above
        for sprite in all_sprites:
            try:
                camera.apply(sprite)
            except AttributeError:
                sprite.kill()
        for sprite in remote_players:
            try:
                camera.apply(sprite)
            except AttributeError:
                sprite.kill()
        camera.apply(player)

        all_sprites.update()
        player_group.update()
        button_group.update(pos)

        remote_players.update(scanner_on)

        background_group.draw(screen)
        # the same problem (AttrErr), watch the comment above
        try:
            all_sprites.draw(screen)
        except AttributeError:
            pass
        terrain_group.draw(screen)
        button_group.draw(screen)
        screen.blit(player.render_info(), (0, 0))
        player_group.draw(screen)
        # the same problem (AttrErr), watch the comment above
        try:
            remote_players.draw(screen)
        except AttributeError:
            pass

        if near_building_message and near_building:
            screen.blit(render_text(near_building_message), (0, height - 50))
        pygame.display.flip()
        clock.tick(fps)
        connect_tick += 1
        if global_exit:
            break
        # if player is arrested, we load the exit interface
        if arrested:
            screen.fill((0, 0, 0))
            text = render_text('Вы арестованы за нарушение карантина!!!')
            logging.info('arrested')
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
            pygame.display.flip()
            score -= 50
            for i in range(3):
                clock.tick(1)
            break
# if any other error we print and set the exit code -7 (game client error) for launcher
except Exception as e:
    print(e)
    error_code = -7
finally:
    # if we break the mainloop or got any exception
    # we safely exit the game
    exit_game()
