import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYER_DIR = os.path.join(BASE_DIR, "assets", "player")

class Player:
    def __init__(self, x, y, floor_rect, screen_height=None):
        self.speed = 1.7
        self.floor_rect = floor_rect

        if screen_height:
            scale_factor = screen_height / 768
        else:
            scale_factor = 1

        def scale(img):
            width = int(128 * scale_factor)
            height = int(128 * scale_factor)
            return pygame.transform.scale(img, (width, height))

        self.idle_frames = [
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "idle1.png")).convert_alpha()),
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "idle2.png")).convert_alpha()),
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "idle3.png")).convert_alpha()),
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "idle4.png")).convert_alpha())
        ]
        self.walk_frames = [
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "walk1.png")).convert_alpha()),
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "walk2.png")).convert_alpha()),
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "walk3.png")).convert_alpha()),
            scale(pygame.image.load(os.path.join(PLAYER_DIR, "walk4.png")).convert_alpha())
        ]

        self.base_image = self.idle_frames[0]
        self.rect = self.base_image.get_rect(midbottom=(x, floor_rect.top))

        self.current_frame = 0
        self.frame_count = 0
        self.frame_delay = 10
        self.idle_delay = 40

        self.is_walking = False
        self.facing_left = False
        self.direction = 'right'

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.facing_left = True
            self.direction = 'left'
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.facing_left = False
            self.direction = 'right'

        if keys[pygame.K_UP]:
            dy = -self.speed
        elif keys[pygame.K_DOWN]:
            dy = self.speed

        new_rect = self.rect.move(dx, dy)

        new_rect.bottom = self.floor_rect.top

        if new_rect.left < self.floor_rect.left:
            new_rect.left = self.floor_rect.left
        if new_rect.right > self.floor_rect.right:
            new_rect.right = self.floor_rect.right

        self.rect = new_rect
        self.is_walking = (dx != 0 or dy != 0)

    def update_animation(self):
        delay = self.frame_delay if self.is_walking else self.idle_delay
        self.frame_count += 1
        if self.frame_count >= delay:
            self.frame_count = 0
            self.current_frame += 1
            if self.is_walking:
                self.base_image = self.walk_frames[self.current_frame % len(self.walk_frames)]
            else:
                self.base_image = self.idle_frames[self.current_frame % len(self.idle_frames)]

    def draw(self, screen):
        image_to_draw = pygame.transform.flip(self.base_image, True, False) if self.facing_left else self.base_image
        screen.blit(image_to_draw, self.rect)
