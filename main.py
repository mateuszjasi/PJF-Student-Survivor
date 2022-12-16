import random

import pygame
from sys import exit
from random import randint


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_stand = pygame.image.load('graphics/player.png').convert_alpha()
        self.image = self.player_stand
        self.rect = self.player_stand.get_rect(center=(800, 450))
        self.speed = 5

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
                self.rect.right += self.speed
        if keys[pygame.K_LEFT]:
            if self.rect.left > 0:
                self.rect.left -= self.speed

    def update(self):
        self.player_input()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('graphics/enemy.png').convert_alpha()
        self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255), 100), special_flags=pygame.BLEND_ADD)
        if randint(0, 2):
            self.rect = self.image.get_rect(center=(random.choice([-50, screen.get_width() + 50]), randint(0, screen.get_height())))
        else:
            self.rect = self.image.get_rect(center=(randint(0, screen.get_width()), random.choice([-50, screen.get_height() + 50])))
        self.movement_speed = 2

    def move_toward_player(self):
        if player.sprite.rect.centerx - self.rect.centerx != 0:
            if player.sprite.rect.centerx > self.rect.centerx:
                self.rect.centerx += self.movement_speed
            if player.sprite.rect.centerx < self.rect.centerx:
                self.rect.centerx -= self.movement_speed
        if player.sprite.rect.centery - self.rect.centery != 0:
            if player.sprite.rect.centery > self.rect.centery:
                self.rect.centery += self.movement_speed
            if player.sprite.rect.centery < self.rect.centery:
                self.rect.centery -= self.movement_speed
        # overcomplicated
        #dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
        #dist = math.hypot(dx, dy)
        #if dist:
        #    dx, dy = dx / dist, dy / dist
        #    self.rect.x += dx * self.movement_speed
        #    self.rect.y += dy * self.movement_speed

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
                    #overcomplicated
                    #dx, dy = enemy.rect.centerx - self.rect.centerx, enemy.rect.centery - self.rect.centery
                    #dist = math.hypot(dx, dy)
                    #if dist:
                    #    if self.rect.centerx > enemy.rect.centerx:
                    #        dx /= dist
                    #        self.rect.x -= dx * 2 * self.movement_speed
                    #        enemy.rect.x += dx * enemy.movement_speed
                    #    if self.rect.centery > enemy.rect.centery:
                    #        dy /= dist
                    #        self.rect.y -= dy * 2 * self.movement_speed
                    #        enemy.rect.y += dy * enemy.movement_speed

    def update(self):
        self.move_toward_player()
        self.prevent_overlap()


def enemy_hit():
    if pygame.sprite.spritecollide(player.sprite, enemies, False):
        enemies.empty()
        player.remove()
        return False
    return True


pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Dzikie fotele w twojej okolicy')
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)
game_active = False

player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()

# Intro screen
game_message = test_font.render('Press space to run', False, 'black')
game_message_rect = game_message.get_rect(center=(800, 600))

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
        game_active = enemy_hit()
    else:
        # menu
        screen.fill('lightgrey')
        screen.blit(game_message, game_message_rect)

    pygame.display.update()
    clock.tick(60)
