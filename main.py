import pygame
import math
from sys import exit
from random import randint


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_stand = pygame.image.load('graphics/player.png').convert()
        self.image = self.player_stand
        self.rect = self.player_stand.get_rect(center=(800, 450))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= 2
        if keys[pygame.K_DOWN]:
            self.rect.y += 2
        if keys[pygame.K_RIGHT]:
            self.rect.x += 2
        if keys[pygame.K_LEFT]:
            self.rect.x -= 2

    def update(self):
        self.player_input()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('graphics/enemy.png').convert()
        self.rect = self.image.get_rect(center=(randint(-100, 1700), randint(-100, 1000)))
        self.movement_speed = 1.5
        # if randint(0, 2):
        #    self.rect = self.image.get_rect(center=(-50, randint(0, 1000)))
        # else:
        #    self.rect = self.image.get_rect(center=(randint(0, 1600), -50))

    def move_toward_player(self):
        dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.movement_speed
            self.rect.y += dy * self.movement_speed

    def update(self):
        self.move_toward_player()


def enemy_hit():
    if pygame.sprite.spritecollide(player.sprite, enemies, False):
        enemies.empty()
        player.remove()
        return False
    return True


def prevent_overlap():
    pass
    # need adjustment
    # for enemy1 in enemies:
    #    for enemy2 in enemies:
    #        if enemy1 != enemy2:
    #            if enemy1.rect.colliderect(enemy2.rect):
    #                if enemy1.rect.bottom > enemy2.rect.top:
    #                    overlap = enemy1.rect.bottom - enemy2.rect.top
    #                    enemy1.rect.bottom -= overlap
    #                if enemy1.rect.top < enemy2.rect.bottom:
    #                    overlap = enemy2.rect.bottom - enemy1.rect.top
    #                    enemy1.rect.top += overlap
    #                if enemy1.rect.left < enemy2.rect.right:
    #                    overlap = enemy1.rect.left - enemy2.rect.right
    #                    enemy1.rect.left -= overlap
    #                if enemy1.rect.right > enemy2.rect.left:
    #                    overlap = enemy2.rect.left - enemy1.rect.right
    #                    enemy1.rect.right += overlap


pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Idk')
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
pygame.time.set_timer(spawn_timer, 1500)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == spawn_timer:
                # spawn enemy
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
        prevent_overlap()
        # game_active = enemy_hit()
    else:
        # menu
        screen.fill('lightgrey')
        screen.blit(game_message, game_message_rect)

    pygame.display.update()
    clock.tick(60)
