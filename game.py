import pygame
import os
from core.player import Player

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Incantatum - Gameplay")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(BASE_DIR, "assets", "map.png")
map_img = pygame.image.load(MAP_PATH).convert()
map_bg = pygame.transform.scale(map_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Chão e barreira lateral
floor_rect = pygame.Rect(5, 729, 1400, 88)

player = Player(15, floor_rect.top - 20, floor_rect)

clock = pygame.time.Clock()
FPS = 60

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    player.handle_input()
    player.update_animation()

    screen.blit(map_bg, (0, 0))
    player.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
