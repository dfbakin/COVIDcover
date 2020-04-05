import pygame

pygame.init()

size = width, height = 1080, 720
screen = pygame.display.set_mode(size)

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(path, colorkey=None, size=None):
    image = pygame.image.load(path).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image


def check_collisions(player):
    for i in all_sprites:
        if i.is_obstacle():
            if pygame.sprite.collide_mask(player, i):
                return True
    return False


class Player(pygame.sprite.Sprite):
    speed = 10

    def __init__(self, x, y, *groups):
        super().__init__(groups)

        self.image = load_image('data/characters/player_left_1.png', colorkey=(255, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        self.prev_coords = x, y
        self.is_moving = False

    def set_moving(self, value):
        self.is_moving = value

    def get_coords(self):
        return self.rect.x, self.rect.y

    def move_left(self):
        self.prev_coords = self.get_coords()
        self.rect.x -= Player.speed
        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def move_right(self):
        self.prev_coords = self.get_coords()
        self.rect.x += Player.speed
        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


fps = 60
running = True
clock = pygame.time.Clock()
camera = Camera()
camera.update(player)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    data = pygame.key.get_pressed()
    player.set_moving(False)
    if data[119]:
        player.move_up()
        player.set_moving(True)
    if data[115]:
        player.move_down()
        player.set_moving(True)
    if data[97]:
        player.move_left()
        player.set_moving(True)
    if data[100]:
        player.move_right()
        player.set_moving(True)

    screen.fill((0, 0, 0))
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(fps)
