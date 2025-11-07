import pygame
import math

DEFAULT_CONFIG = {
    "expelliarmus": {"speed": 12, "radius": 10, "damage": 18, "mana": 10, "color": (160,160,255)},
    "incendio": {"speed": 10, "radius": 12, "damage": 30, "mana": 20, "color": (255,120,60)},
    "protego": {"speed": 0, "radius": 0, "damage": 0, "mana": 8, "color": (100,180,255)}
}

class Spell:
    @staticmethod
    def config(name):
        return DEFAULT_CONFIG.get(name)

    def __init__(self, x, y, vx, vy, radius, damage, color, owner="player"):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = int(radius)
        self.damage = damage
        self.color = color
        self.owner = owner

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        surf = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (self.color[0], self.color[1], self.color[2], 220),
                           (self.radius*2, self.radius*2), self.radius)
        surface.blit(surf, (int(self.x - self.radius*2), int(self.y - self.radius*2)))

    def collides_with(self, player):
        px = player.rect.centerx
        py = player.rect.centery
        dist = math.hypot(self.x - px, self.y - py)
        hit_radius = (self.radius + max(player.rect.width, player.rect.height)*0.35)
        return dist < hit_radius