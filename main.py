import random
import pygame
import math
from sys import exit
from random import randint


def main_menu():
    screen.fill('lightgrey')
    start_game_button.process()


def pause_menu():
    customButton.process()


def game_update():
    screen.fill('darkgrey')
    player.draw(screen)
    player.update()
    enemies.draw(screen)
    enemies.update()
    bullets.draw(screen)
    bullets.update()
    global bullet_cooldown_tracker
    bullet_cooldown_tracker += 1
    # game_active = enemy_hit()


def start_game():
    global game_active
    game_active = True
    player.add(Player())


def enemy_hit():
    if pygame.sprite.spritecollide(player.sprite, enemies, False):
        enemies.empty()
        bullets.empty()
        player.remove()
        return False
    return True


class Button:
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.alreadyPressed = False
        self.fillColors = {
            'normal': (255, 0, 0),
            'hover': (200, 0, 0),
            'pressed': (100, 0, 0),
        }
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonRect.center = (self.x, self.y)
        self.buttonSurf = button_font.render(buttonText, True, (0, 0, 0))
        self.alreadyPressed = False

    def process(self):
        mouse_position = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mouse_position):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed()[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 10
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = player.sprite.rect.centerx
        self.y = player.sprite.rect.centery
        self.angle = math.atan2(self.y - mouse_y, self.x - mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
        self.image = pygame.Surface([10, 10])
        self.image.fill((255, 255, 255))
        self.image.set_colorkey((255, 255, 255))
        pygame.draw.circle(self.image, (0, 0, 0), (self.image.get_width() / 2, self.image.get_height() / 2), 5)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self):
        self.rect.x -= int(self.x_vel)
        self.rect.y -= int(self.y_vel)

    def check_outside(self):
        if self.rect.left > screen.get_width() or self.rect.right < 0:
            self.kill()
        if self.rect.top > screen.get_height() or self.rect.bottom < 0:
            self.kill()

    def update(self):
        self.move()
        self.check_outside()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.walking_right = False
        self.walking_left = False
        self.facing_right = True
        self.speed = 3
        self.bullet_cooldown = 10
        self.walking_animation = [pygame.image.load("graphics/player_walk_0.png"),
                                  pygame.image.load("graphics/player_walk_1.png"),
                                  pygame.image.load("graphics/player_walk_2.png"),
                                  pygame.image.load("graphics/player_walk_3.png")]
        self.player_weapon = pygame.image.load("graphics/weapon.png").convert_alpha()
        self.rect = self.walking_animation[0].get_rect(center=(800, 450))
        self.image = self.walking_animation[0]
        self.animation_count = 0

    def handle_weapon(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        if mouse_x < self.rect.centerx:
            player_weapon_copy = pygame.transform.flip(self.player_weapon, False, True)
        else:
            player_weapon_copy = self.player_weapon
        player_weapon_copy = pygame.transform.rotate(player_weapon_copy, angle)
        screen.blit(player_weapon_copy, (self.rect.centerx - int(player_weapon_copy.get_width() / 2),
                                         self.rect.centery + 5 - int(player_weapon_copy.get_height() / 2)))

    def walking(self):
        if self.animation_count < 15.0:
            self.animation_count += 1
        else:
            self.animation_count = 0
        if self.walking_right:
            self.image = self.walking_animation[self.animation_count // 4]
            self.walking_right = False
        elif self.walking_left:
            self.image = pygame.transform.flip(self.walking_animation[self.animation_count // 4], True, False)
            self.walking_left = False
        elif self.facing_right:
            self.image = self.walking_animation[0]
        else:
            self.image = pygame.transform.flip(self.walking_animation[0], True, False)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.rect.top > 0:
                self.rect.top -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.rect.bottom < screen.get_height():
                self.rect.bottom += self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.rect.right < screen.get_width():
                self.walking_right = True
                self.walking_left = False
                self.facing_right = True
                self.rect.right += self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.rect.left > 0:
                self.walking_right = False
                self.walking_left = True
                self.facing_right = False
                self.rect.left -= self.speed

    def update(self):
        self.player_input()
        self.walking()
        self.handle_weapon()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.movement_speed = 1
        self.walking_animation = [pygame.image.load("graphics/enemy_animation_0.png"),
                                  pygame.image.load("graphics/enemy_animation_1.png"),
                                  pygame.image.load("graphics/enemy_animation_2.png"),
                                  pygame.image.load("graphics/enemy_animation_3.png")]
        self.image = self.walking_animation[0]
        self.animation_count = 0
        if randint(0, 2):
            self.rect = self.image.get_rect(
                center=(random.choice([-50, screen.get_width() + 50]), randint(0, screen.get_height())))
        else:
            self.rect = self.image.get_rect(
                center=(randint(0, screen.get_width()), random.choice([-50, screen.get_height() + 50])))

    def move_toward_player(self):
        if self.animation_count + 1 < 16.0:
            self.animation_count += 1
        else:
            self.animation_count = 0
        self.image = self.walking_animation[self.animation_count // 4]
    #    dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
    #    dist = math.hypot(dx, dy)
    #    if dist:
    #        dx, dy = dx / dist, dy / dist
    #        self.rect.x += dx * self.movement_speed
    #        self.rect.y += dy * self.movement_speed
        if player.sprite.rect.centerx != self.rect.centerx:
            if player.sprite.rect.centerx > self.rect.centerx:
                self.rect.centerx += self.movement_speed
            if player.sprite.rect.centerx < self.rect.centerx:
                self.rect.centerx -= self.movement_speed
        if player.sprite.rect.centery != self.rect.centery:
            if player.sprite.rect.centery > self.rect.centery:
                self.rect.centery += self.movement_speed
            if player.sprite.rect.centery < self.rect.centery:
                self.rect.centery -= self.movement_speed

    def prevent_overlap(self):
        for enemy in enemies:
            if self != enemy:
                if self.rect.colliderect(enemy.rect):
                    if enemy.rect.centerx - self.rect.centerx != 0:
                        if enemy.rect.centerx > self.rect.centerx:
                            self.rect.centerx -= self.movement_speed
                        if enemy.rect.centerx < self.rect.centerx:
                            self.rect.centerx += self.movement_speed
                    if enemy.rect.centery - self.rect.centery != 0:
                        if enemy.rect.centery > self.rect.centery:
                            self.rect.centery -= self.movement_speed
                        if enemy.rect.centery < self.rect.centery:
                            self.rect.centery += self.movement_speed

    def suicide(self):
        for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                bullet.kill()
                self.kill()
                break

    def update(self):
        self.move_toward_player()
        self.prevent_overlap()
        self.suicide()


def test():
    print("test")


pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Dzikie fotele w twojej okolicy')
clock = pygame.time.Clock()
button_font = pygame.font.Font(None, 40)

start_game_button = Button(800, 600, 200, 100, "Start", start_game)

customButton = Button(30, 30, 400, 100, 'TestButton', test)

player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_timer, 150)

game_active = False
game_pause = False
bullet_cooldown_tracker = 0
max_enemies = 20

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if game_pause:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_pause = False
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_pause = True
                if pygame.mouse.get_pressed()[0] and bullet_cooldown_tracker >= player.sprite.bullet_cooldown:
                    bullets.add(PlayerBullet())
                    bullet_cooldown_tracker = 0
                if event.type == spawn_timer and len(enemies) < max_enemies:
                    enemies.add(Enemy())
    if game_active:
        if game_pause:
            pause_menu()
        else:
            game_update()
    else:
        main_menu()

    pygame.display.update()
    clock.tick(60)
