import pygame
import sys
import math
import os
import random
from core.transitions import fade_out, fade_in
from tela_selecao_personagem import iniciar_selecao  # mantém fluxo antigo

# --- Configurações Iniciais ---
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Incantatum - Luta de Varinhas"

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (40, 40, 70)
BUTTON_HOVER = (80, 80, 140)

# --- Inicializa o Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

# --- Paths robustos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "imagens", "minha_arte_de_fundo.jpg")

# Carrega background com fallback
def load_background(path, size):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, size)
    except Exception:
        surf = pygame.Surface(size)
        for y in range(size[1]):
            t = y / size[1]
            r = int(8 + 20 * t)
            g = int(12 + 18 * t)
            b = int(20 + 30 * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (size[0], y))
        return surf

background_image = load_background(IMAGE_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Configurações do Botão ---
button_width = 300
button_height = 80
button_x = (SCREEN_WIDTH - button_width) // 2
button_y = SCREEN_HEIGHT - 180
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

# Fonte para o texto do botão
font = pygame.font.Font(None, 48)
text_surface = font.render("Começar", True, WHITE)
text_rect = text_surface.get_rect(center=button_rect.center)

# --- Partículas (neblina mágica) ---
class Particle:
    def __init__(self, x, y, vx, vy, size, life, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.life = life
        self.max_life = life
        self.color = color

    def update(self, dt_ms):
        dt = dt_ms / 1000.0
        self.x += self.vx * dt_ms
        self.y += self.vy * dt_ms
        self.life -= dt_ms
        self.vx *= 0.999

    def draw(self, surf):
        alpha = max(0, int(200 * (self.life / self.max_life)))
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))

particles = []

def spawn_particle_alt():
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT // 2)
    vx = (random.random() - 0.5) * 0.02 * 1000  # scaled for dt usage
    vy = (0.02 + random.random() * 0.04) * 1000
    size = 6 + int(random.random() * 10)
    life = 2000 + int(random.random() * 2000)
    color = (150, 120, 255)
    particles.append(Particle(x, y, vx, vy, size, life, color))

# --- Efeito de pulsação do botão ---
pulse = 0.0
pulse_dir = 1

game_state = 'menu'
running = True

# fade in at start
fade_in(screen, color=(0,0,0), speed=18)

while running:
    dt_ms = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and game_state == 'menu' and button_rect.collidepoint(event.pos):
                fade_out(screen, color=(0,0,0), speed=12)
                iniciar_selecao(screen)  # retorna ao menu quando a seleção/luta terminar
                fade_in(screen, color=(0,0,0), speed=12)

    # spawn particles occasionally
    if random.random() < 0.12:
        spawn_particle_alt()

    # update particles
    for p in particles[:]:
        p.update(dt_ms)
        if p.life <= 0:
            particles.remove(p)

    # pulse update
    dt = dt_ms / 1000.0
    pulse += dt * 2.2 * pulse_dir
    if pulse > 1.0:
        pulse = 1.0
        pulse_dir = -1
    elif pulse < 0.0:
        pulse = 0.0
        pulse_dir = 1

    # draw background
    screen.blit(background_image, (0, 0))

    # draw particles
    for p in particles:
        p.draw(screen)

    # button hover effect
    mouse = pygame.mouse.get_pos()
    hovered = button_rect.collidepoint(mouse)
    color = BUTTON_HOVER if hovered else BUTTON_COLOR

    # draw button with subtle glow based on pulse
    glow_surf = pygame.Surface((button_width+40, button_height+40), pygame.SRCALPHA)
    glow_alpha = int(80 + 120 * pulse)
    pygame.draw.ellipse(glow_surf, (120,120,220, glow_alpha), glow_surf.get_rect())
    screen.blit(glow_surf, (button_x-20, button_y-20), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.rect(screen, color, button_rect, border_radius=18)
    screen.blit(text_surface, text_rect)

    # small hint
    hint = pygame.font.Font(None, 24).render("Clique para começar", True, (200,200,200))
    screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, button_y + button_height + 14))

    pygame.display.flip()

fade_out(screen, color=(0,0,0), speed=18)
pygame.quit()
sys.exit()
