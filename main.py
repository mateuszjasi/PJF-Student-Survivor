import pygame
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
    def __init__(self, type):
        super().__init__()
        if type:
            pass
        self.image = pygame.image.load('graphics/enemy.png').convert()
        self.rect = self.image.get_rect(center=(randint(-100, 1700), randint(-100, 1000)))
        # if randint(0, 2):
        #    self.rect = self.image.get_rect(center=(-50, randint(0, 1000)))
        # else:
        #     self.rect = self.image.get_rect(center=(randint(0, 1600), -50))

    def update(self):
        pass


def enemy_hit():
    if pygame.sprite.spritecollide(player.sprite, enemies, False):
        enemies.empty()
        player.remove()
        return False
    return True


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

# enemy spawn timer
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
                enemies.add(Enemy('???'))
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
