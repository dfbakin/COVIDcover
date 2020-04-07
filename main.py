import pygame

pygame.init()

size = width, height = 1080, 720
screen = pygame.display.set_mode(size)

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
building_group = pygame.sprite.Group()
settings_buttons_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()

building_collide_step = 0
near_building_message = None
near_building = None
gravity = 1


def load_image(path, colorkey=None, size=None):
    image = pygame.image.load(path).convert_alpha()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    # else:
    # image = image.convert_alpha()
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


def check_near_building(player):
    global near_building, near_building_message
    near_building, near_building_message = None, None
    for building in building_group:
        if pygame.sprite.collide_mask(player, building):
            near_building = building
            near_building_message = f'Press [E] to enter the {building.name}'


def render_text(line, size=50):
    font = pygame.font.Font(None, size)
    text = font.render(line, 1, (255, 255, 255))
    return text


class Player(pygame.sprite.Sprite):
    speed = 5
    jump_power = 15

    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.frames = {'left': [], 'right': []}
        for i in range(1):
            self.frames['left'].append(
                load_image(f'data/characters/player_left_{i + 1}.png', size=(30, 80)))
        for i in range(1):
            self.frames['right'].append(
                load_image(f'data/characters/player_right_{i + 1}.png', size=(30, 80)))

        self.image = self.frames['right'][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        self.prev_coords = x, y
        self.is_moving = False
        self.grav = 0
        self.is_jumping = False
        self.clock = pygame.time.Clock()

        self.health = 100
        self.hazard_risk = 0
        self.danger_level = 1
        self.hazard_timer = 0

    def set_position(self, pos):
        self.rect.x, self.rect.y = pos

    def set_moving(self, value):
        self.is_moving = value

    def get_coords(self):
        return self.rect.x, self.rect.y

    def is_obstacle(self):
        return False

    def move_left(self):
        self.image = self.frames['left'][0]

        self.prev_coords = self.get_coords()
        self.rect.x -= Player.speed
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
        self.image = self.frames['right'][0]
        self.prev_coords = self.get_coords()
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
            if self.grav < -16:
                self.health -= abs(self.grav) - 10
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]
            self.grav = -5
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.grav = Player.jump_power
            self.is_jumping = True

    def render_info(self):
        canvas = pygame.Surface((width, 80))
        font = pygame.font.Font(None, 30)
        canvas.blit(font.render(f'Health: {self.health}%, Risk of infection: {self.hazard_risk}%', 1, (255, 255, 255)),
                    (0, 0))
        return canvas

    def update(self, *args):
        self.danger_level = 1 - (100 - self.health) / 100
        self.hazard_timer += self.clock.tick()
        if self.hazard_timer > 1000 * self.danger_level:
            self.hazard_risk += 1
            self.hazard_timer = 0
        self.move_down(self.grav)
        self.grav -= gravity

        if self.health <= 0:
            self.health = 0
        if self.hazard_risk >= 100:
            self.hazard_risk = 100
        if self.health == 0 or self.hazard_risk == 100:
            screen.fill((0, 0, 0))
            # background_group.draw(screen)
            screen.blit(self.render_info(), (0, 0))
            text = render_text('You died!!!')
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
            pygame.display.flip()
            for i in range(5):
                self.clock.tick(1)
            quit()


class Terrain(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/textures/city_terrain.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def is_obstacle(self):
        return True


class Bank(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = load_image('data/textures/bank.png', size=(250, 150))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

        self.name = 'Bank'

    def is_obstacle(self):
        return False

    def enter(self):
        pass


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image, func, *groups):
        groups = list(groups)
        super().__init__(groups)
        self.h = h
        self.w = w
        # self.image = pygame.transform.scale(image, (self.w, self.h))
        self.image = image
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


class Camera:
    def __init__(self):
        self.dx = 0
        # self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        # obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        # self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def exit_game():
    quit()


def menu(pause=False):
    delt_width = 75

    def start():
        return 'start'

    def settings():
        def sound_effect_switch():
            return
            global effects_on
            effects_on = not effects_on
            label = f"Sound effects {'on' if effects_on else 'off'}"

            canvas = pygame.Surface((315, 100))
            canvas.fill((181, 109, 2))
            text = render_text(label)
            canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                               canvas.get_height() // 2 - text.get_height() // 2))

            effects_button.image = canvas

        def music_switch():
            return
            global music_on
            music_on = not music_on
            label = f"Music {'on' if music_on else 'off'}"
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
                music['main_track'].play(-1)

        running = True

        canvas = pygame.Surface((315, 100))
        canvas.fill((181, 109, 2))
        # text = render_text(f"Music {'on' if music_on else 'off'}")
        text = render_text(f"Music on/off")
        canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                           canvas.get_height() // 2 - text.get_height() // 2))

        music_button = Button(width // 2 - delt_width, height // 4, 315, 100, canvas,
                              music_switch, settings_buttons_group)

        canvas = pygame.Surface((315, 100))
        canvas.fill((181, 109, 2))
        # text = render_text(f"Sound effects {'on' if effects_on else 'off'}")
        text = render_text(f"Sound effects on/off")
        canvas.blit(text, (canvas.get_width() // 2 - text.get_width() // 2,
                           canvas.get_height() // 2 - text.get_height() // 2))

        effects_button = Button(width // 2 - delt_width, height // 4 * 2, 315, 100,
                                canvas, sound_effect_switch,
                                settings_buttons_group)

        canvas = pygame.Surface((315, 100))
        canvas.fill((181, 109, 2))
        text = render_text('Back')
        canvas.blit(text, (
            canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))

        Button(width // 2 - delt_width, height // 4 * 3, 315, 100, canvas, lambda: 'back', settings_buttons_group)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    for btn in button_group:
                        btn.check_selection(pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for btn in settings_buttons_group:
                        if btn.rect.collidepoint(pos):
                            running = btn.run() != 'back'
            screen.fill((219, 146, 72))
            settings_buttons_group.draw(screen)
            pygame.display.flip()
            clock.tick(fps)

    running = True
    label = 'Resume' if pause else 'Start'

    canvas = pygame.Surface((200, 100))
    canvas.fill((181, 109, 2))
    text = render_text(label)
    canvas.blit(text,
                (canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))
    Button(width // 2 - delt_width, height // 4, 200, 100, canvas, start, button_group)

    canvas = pygame.Surface((200, 100))
    canvas.fill((181, 109, 2))
    text = render_text('Settings')
    canvas.blit(text,
                (canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))
    Button(width // 2 - delt_width, height // 4 * 2, 200, 100, canvas, settings, button_group)

    canvas = pygame.Surface((200, 100))
    canvas.fill((181, 109, 2))
    text = render_text('Back')
    canvas.blit(text,
                (canvas.get_width() // 2 - text.get_width() // 2, canvas.get_height() // 2 - text.get_height() // 2))
    Button(width // 2 - delt_width, height // 4 * 3, 200, 100, canvas, exit_game, button_group)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                for btn in button_group:
                    btn.check_selection(pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for btn in button_group:
                    if btn.rect.collidepoint(pos):
                        running = btn.run() != 'start'
        screen.fill((219, 146, 72))
        button_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    button_group.empty()
    settings_buttons_group.empty()


images = {'pause_button': load_image('data/other/pause_button.png', size=(50, 50))}
fps = 60
running = True
clock = pygame.time.Clock()

# menu()

player = Player(200, 150, player_group, all_sprites)
terrain = Terrain(0, 0, all_sprites)
bank = Bank(350, 275, all_sprites, building_group)

pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)

camera = Camera()
camera.update(player)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in button_group:
                if btn.rect.collidepoint(event.pos):
                    btn.run()
                    pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)
    data = pygame.key.get_pressed()
    # if any(data):
    # print(data.index(1))
    player.set_moving(False)
    if data[27]:
        menu(pause=True)
        pause_button = Button(width - 50, 0, 50, 50, images['pause_button'], menu, button_group)
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
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.update()
    all_sprites.draw(screen)
    button_group.draw(screen)
    player_group.draw(screen)
    if near_building_message and near_building:
        screen.blit(render_text(near_building_message), (0, height - 50))
    screen.blit(player.render_info(), (0, 0))
    pygame.display.flip()
    clock.tick(fps)
