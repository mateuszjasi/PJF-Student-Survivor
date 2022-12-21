import random
import pygame
import math
from sys import exit
from random import randint


def main_menu():
    screen.fill('lightgrey')
    start_game_button.process()
    open_shop_button.process()


def shop():
    screen.fill('lightgrey')
    close_shop_button.process()


def pause_menu():
    unpause_game_button.process()
    end_game_button.process()


def death_screen_menu():
    death_screen_button.process()


def end_game():
    global game_active, game_pause, death_screen, minutes, seconds
    enemies.empty()
    bullets.empty()
    drops.empty()
    player.remove()
    minutes, seconds = 0, 0
    game_active, game_pause, death_screen = False, False, False


def clock_update():
    global minutes, seconds
    if seconds >= 60:
        minutes += 1
        seconds = 0
    time_label = progress_bar_font.render("{:02}:{:02}".format(minutes, seconds), True, (0, 0, 0))
    time_label_rect = time_label.get_rect(center=(screen.get_width() / 2, 50))
    screen.blit(time_label, time_label_rect)


def game_update():
    screen.fill('darkgrey')
    drops.draw(screen)
    enemies.draw(screen)
    enemies.update()
    bullets.draw(screen)
    bullets.update()
    player.draw(screen)
    player.update()


def start_game():
    global game_active
    game_active = True
    player.add(Player(5, 3, 3, 30, 10, 10, 500, 100))


def open_shop():
    global upgrade_shop
    upgrade_shop = True


def close_shop():
    global upgrade_shop
    upgrade_shop = False


def pause_game():
    global game_pause
    game_pause = True


def unpause_game():
    global game_pause
    game_pause = False


def player_died():
    global death_screen
    death_screen = True
    screen.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGBA_MIN)


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


class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        self.image = pygame.image.load("graphics/drop.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move_to_player(self):
        dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * 5
            self.rect.y += dy * 5

    def update(self):
        self.move_to_player()


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_damage, bullet_speed, bullet_range):
        super().__init__()
        self.speed = bullet_speed
        self.damage = bullet_damage
        self.range = bullet_range
        self.traveled = 0
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = player.sprite.rect.centerx
        self.y = player.sprite.rect.centery
        self.angle = math.atan2(self.y - mouse_y, self.x - mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
        self.distance = math.hypot(self.x_vel, self.y_vel)
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
        self.traveled += self.distance
        if self.traveled >= self.range:
            self.kill()

    def check_outside(self):
        if self.rect.left > screen.get_width() or self.rect.right < 0:
            self.kill()
        if self.rect.top > screen.get_height() or self.rect.bottom < 0:
            self.kill()

    def update(self):
        self.move()
        self.check_outside()


class Player(pygame.sprite.Sprite):
    def __init__(self, bullet_damage, speed, max_health, damage_cooldown, shoot_cooldown, bullet_speed,
                 bullet_range, pickup_range):
        super().__init__()
        self.walking_right = False
        self.walking_left = False
        self.facing_right = True
        self.damage = bullet_damage
        self.speed = speed
        self.max_health = max_health
        self.damage_cooldown = damage_cooldown
        self.shoot_cooldown = shoot_cooldown
        self.bullet_speed = bullet_speed
        self.bullet_range = bullet_range
        self.pickup_range = pickup_range
        self.level = 1
        self.max_exp = 10
        self.exp = 0
        self.health = self.max_health
        self.shoot_cooldown_tracker = 0
        self.damage_cooldown_tracker = 0
        self.walking_animation = [pygame.image.load("graphics/player_walk_0.png"),
                                  pygame.image.load("graphics/player_walk_1.png"),
                                  pygame.image.load("graphics/player_walk_2.png"),
                                  pygame.image.load("graphics/player_walk_3.png")]
        self.player_weapon = pygame.image.load("graphics/weapon.png").convert_alpha()
        self.rect = self.walking_animation[0].get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        self.image = self.walking_animation[0]
        self.animation_count = 0

    def show_stats(self):
        width = 200
        height = 40

        pygame.draw.rect(screen, (0, 0, 0), (10, 10, width + 10, height + 10), 5)
        health_bar = pygame.draw.rect(screen, (128, 128, 128), (15, 15, width, height))
        pygame.draw.rect(screen, (255, 0, 0), (15, 15, width * self.health / self.max_health, height))
        health_text = progress_bar_font.render(str(self.health) + " / " + str(self.max_health), False, (0, 0, 0))
        health_text_rect = health_text.get_rect(center=health_bar.center)
        screen.blit(health_text, health_text_rect)

        pygame.draw.rect(screen, (0, 0, 0), (10, height + 25, width + 10, height + 10), 5)
        exp_bar = pygame.draw.rect(screen, (128, 128, 128), (15, height + 30, width, height))
        pygame.draw.rect(screen, (0, 255, 0), (15, height + 30, width * self.exp / self.max_exp, height))
        exp_text = progress_bar_font.render("Lv: " + str(self.level), False, (0, 0, 0))
        exp_text_rect = exp_text.get_rect(center=exp_bar.center)
        screen.blit(exp_text, exp_text_rect)

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
        if self.animation_count + 1 < 16:
            self.animation_count += 1
        else:
            self.animation_count = 0
        if self.walking_right:
            self.image = self.walking_animation[self.animation_count // 4].copy()
            self.walking_right = False
        elif self.walking_left:
            self.image = pygame.transform.flip(self.walking_animation[self.animation_count // 4].copy(), True, False)
            self.walking_left = False
        elif self.facing_right:
            self.image = self.walking_animation[0].copy()
        else:
            self.image = pygame.transform.flip(self.walking_animation[0].copy(), True, False)
        if self.damage_cooldown_tracker:
            self.image.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)

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
        if pygame.mouse.get_pressed()[0] and not self.shoot_cooldown_tracker:
            self.shoot()

    def shoot(self):
        bullets.add(PlayerBullet(self.damage, self.bullet_speed, self.bullet_range))
        self.shoot_cooldown_tracker = self.shoot_cooldown

    def check_hit(self):
        if pygame.sprite.spritecollide(player.sprite, enemies, False) and not self.damage_cooldown_tracker:
            self.damage_cooldown_tracker = self.damage_cooldown
            self.health -= 1
        if self.health <= 0:
            player_died()

    def check_drop(self):
        for drop in drops:
            if math.hypot(self.rect.x - drop.rect.x, self.rect.y - drop.rect.y) < self.pickup_range:
                drop.update()
            if self.rect.colliderect(drop.rect):
                self.exp += drop.value
                drop.kill()

    def check_level_up(self):
        if self.exp >= self.max_exp:
            self.exp = 0
            self.level += 1
            self.max_exp = self.level * 10

    def update_trackers(self):
        if self.shoot_cooldown_tracker:
            self.shoot_cooldown_tracker -= 1
        if self.damage_cooldown_tracker:
            self.damage_cooldown_tracker -= 1

    def update(self):
        self.update_trackers()
        self.player_input()
        self.walking()
        self.handle_weapon()
        self.check_hit()
        self.check_drop()
        self.check_level_up()
        self.show_stats()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, health, speed, value):
        super().__init__()
        self.health = health
        self.speed = speed
        self.value = value
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
        if self.animation_count + 1 < 16:
            self.animation_count += 1
        else:
            self.animation_count = 0
        self.image = self.walking_animation[self.animation_count // 4]
        if player.sprite.rect.centerx != self.rect.centerx:
            if player.sprite.rect.centerx > self.rect.centerx:
                self.rect.centerx += self.speed
            if player.sprite.rect.centerx < self.rect.centerx:
                self.rect.centerx -= self.speed
        if player.sprite.rect.centery != self.rect.centery:
            if player.sprite.rect.centery > self.rect.centery:
                self.rect.centery += self.speed
            if player.sprite.rect.centery < self.rect.centery:
                self.rect.centery -= self.speed

    def prevent_overlap(self):
        for enemy in enemies:
            if self != enemy:
                if self.rect.colliderect(enemy.rect):
                    if enemy.rect.centerx - self.rect.centerx != 0:
                        if enemy.rect.centerx > self.rect.centerx:
                            self.rect.centerx -= self.speed
                        if enemy.rect.centerx < self.rect.centerx:
                            self.rect.centerx += self.speed
                    if enemy.rect.centery - self.rect.centery != 0:
                        if enemy.rect.centery > self.rect.centery:
                            self.rect.centery -= self.speed
                        if enemy.rect.centery < self.rect.centery:
                            self.rect.centery += self.speed

    def check_hit(self):
        for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                self.health -= bullet.damage
                bullet.kill()
        if self.health <= 0:
            drops.add(Drop(self.rect.centerx, self.rect.centery, self.value))
            self.kill()

    def update(self):
        self.move_toward_player()
        self.prevent_overlap()
        self.check_hit()


pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption('Dzikie fotele w twojej okolicy')
clock = pygame.time.Clock()
button_font = pygame.font.Font(None, 40)
progress_bar_font = pygame.font.Font(None, 50)

start_game_button = Button(screen.get_width() / 2, screen.get_height() / 2 + 200, 200, 100, "Start", start_game)
open_shop_button = Button(screen.get_width() / 2, screen.get_height() / 2 + 300, 200, 80, "Upgrades", open_shop)
close_shop_button = Button(screen.get_width() / 2, screen.get_height() / 2 + 400, 200, 100, "Return", close_shop)
unpause_game_button = Button(screen.get_width() / 2, screen.get_height() / 2 - 50, 200, 50, "Resume", unpause_game)
end_game_button = Button(screen.get_width() / 2, screen.get_height() / 2 + 50, 200, 50, "End", end_game)
death_screen_button = Button(screen.get_width() / 2, screen.get_height() / 2, 200, 50, "Back to menu", end_game)

player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
drops = pygame.sprite.Group()

clock_timer = pygame.USEREVENT + 1
pygame.time.set_timer(clock_timer, 1000)

spawn_timer = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_timer, 500)

minutes, seconds, frames = 0, 0, 0
game_active, game_pause, upgrade_shop, death_screen = False, False, False, False
max_enemies = 20

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if game_pause:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    unpause_game()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pause_game()
                if event.type == clock_timer:
                    seconds += 1
                if event.type == spawn_timer and len(enemies) < max_enemies:
                    enemies.add(Enemy(5, 1, 1))
    if game_active:
        if death_screen:
            death_screen_menu()
        elif game_pause:
            pause_menu()
        else:
            game_update()
            clock_update()
    elif upgrade_shop:
        shop()
    else:
        main_menu()

    pygame.display.update()
    clock.tick(60)
