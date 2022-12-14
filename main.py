import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Jeszcze nie wiem')
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update()
