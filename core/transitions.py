import pygame

def fade_in(screen, color=(0,0,0), speed=10):
    w, h = screen.get_size()
    fade = pygame.Surface((w,h))
    for alpha in range(255, -1, -speed):
        fade.set_alpha(alpha)
        fade.fill(color)
        screen.blit(fade, (0,0))
        pygame.display.flip()

def fade_out(screen, color=(0,0,0), speed=10):
    w, h = screen.get_size()
    fade = pygame.Surface((w,h))
    for alpha in range(0, 256, speed):
        fade.set_alpha(alpha)
        fade.fill(color)
        screen.blit(fade, (0,0))
        pygame.display.flip()