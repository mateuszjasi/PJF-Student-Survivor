import random
import pygame
import math
from sys import exit
from random import randint

pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Dzikie fotele w twojej okolicy')
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)
# Intro screen
game_message = test_font.render('Press space to run', False, 'black')
game_message_rect = game_message.get_rect(center=(800, 600))


def enemy_hit():
    if pygame.sprite.spritecollide(player.sprite, enemies, False):
        enemies.empty()
        bullets.empty()
        player.remove()
        return False
    return True


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = player.sprite.rect.centerx
        self.y = player.sprite.rect.centery
        self.speed = 10
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
        self.walking_animation = [pygame.image.load("graphics/player_walk_0.png"),
                                  pygame.image.load("graphics/player_walk_1.png"),
                                  pygame.image.load("graphics/player_walk_2.png"),
                                  pygame.image.load("graphics/player_walk_3.png")]
        self.player_weapon = pygame.image.load("graphics/weapon.png").convert_alpha()
        self.rect = self.walking_animation[0].get_rect(center=(800, 450))
        self.image = self.walking_animation[0]
        self.animation_count = 0
        self.walking_right = False
        self.walking_left = False
        self.facing_right = True
        self.speed = 5

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
        if keys[pygame.K_UP]:
            if self.rect.top > 0:
                self.rect.top -= self.speed
        if keys[pygame.K_DOWN]:
            if self.rect.bottom < screen.get_height():
                self.rect.bottom += self.speed
        if keys[pygame.K_RIGHT]:
            if self.rect.right < screen.get_width():
                self.walking_right = True
                self.walking_left = False
                self.facing_right = True
                self.rect.right += self.speed
        if keys[pygame.K_LEFT]:
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
        self.movement_speed = 2

    def move_toward_player(self):
        if self.animation_count + 1 < 16.0:
            self.animation_count += 1
        else:
            self.animation_count = 0
        self.image = self.walking_animation[self.animation_count // 4]
        # overcomplicated
        # dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
        # dist = math.hypot(dx, dy)
        # if dist:
        #    dx, dy = dx / dist, dy / dist
        #    self.rect.x += dx * self.movement_speed
        #    self.rect.y += dy * self.movement_speed
        if player.sprite.rect.centerx > self.rect.centerx:
            self.rect.centerx += self.movement_speed
        elif player.sprite.rect.centerx < self.rect.centerx:
            self.rect.centerx -= self.movement_speed
        if player.sprite.rect.centery > self.rect.centery:
            self.rect.centery += self.movement_speed
        elif player.sprite.rect.centery < self.rect.centery:
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


game_active = False

player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Enemy spawn timer
spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_timer, 150)

max_enemies = 20

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == spawn_timer:
                # spawn enemy
                if len(enemies) < max_enemies:
                    enemies.add(Enemy())
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bullets.add(PlayerBullet())
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # game start
                player.add(Player())
                game_active = True

    if game_active:
        # game
        screen.fill('darkgrey')
        player.draw(screen)
        player.update()
        enemies.draw(screen)
        enemies.update()
        bullets.draw(screen)
        bullets.update()
        game_active = enemy_hit()
    else:
        # menu
        screen.fill('lightgrey')
        screen.blit(game_message, game_message_rect)

    pygame.display.update()
    clock.tick(60)
