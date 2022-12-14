import pygame
from sys import exit


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


pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Idk')
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)
game_active = False
start_time = 0

player = pygame.sprite.GroupSingle()
player.add(Player())

# Intro screen
game_message = test_font.render('Press space to run', False, 'black')
game_message_rect = game_message.get_rect(center=(800, 600))

# enemy spawn timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == obstacle_timer:
                # spawn enemy
                pass
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # game start
                game_active = True

    if game_active:
        # game
        screen.fill('darkgrey')
        player.draw(screen)
        player.update()
    else:
        # menu
        screen.fill('lightgrey')
        screen.blit(game_message, game_message_rect)

    pygame.display.update()
    clock.tick(60)
