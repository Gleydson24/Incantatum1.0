import pygame
import sys
import math

# --- Configurações Iniciais ---
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Encantatun - Luta de Varinhas"

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 70, 70)

# --- Inicializa o Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption(SCREEN_TITLE)

# --- Carrega a Imagem de Fundo ---
try:
    background_image = pygame.image.load('imagens/minha_arte_de_fundo.jpg').convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Erro ao carregar a imagem de fundo: {e}")
    print("Certifique-se de que 'minha_arte_de_fundo.jpg' está na mesma pasta do script.")
    background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_image.fill(BLACK)


# --- Configurações do Botão ---
button_width = 250
button_height = 65
button_x = (SCREEN_WIDTH - button_width) // 2
button_y = SCREEN_HEIGHT - 100
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

# Fonte para o texto do botão
font = pygame.font.Font(None, 40)
text_surface = font.render("Começar", True, WHITE)
text_rect = text_surface.get_rect(center=button_rect.center)

# --- Variáveis para o Efeito de Pulso ---
pulse_radius = 0
pulse_alpha = 255
pulse_speed = 7
max_coverage_radius = int(math.hypot(SCREEN_WIDTH, SCREEN_HEIGHT)) + 100

game_state = 'menu'

# --- Loop Principal do Jogo ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == 'menu' and button_rect.collidepoint(event.pos):
                    game_state = 'transition'
                    pulse_radius = 0
                    pulse_alpha = 255

    # --- Lógica do Jogo ---
    if game_state == 'transition':
        pulse_radius += pulse_speed

        normalized_radius = pulse_radius / max_coverage_radius
        pulse_alpha = max(0, 255 - int(255 * normalized_radius * 0.8))

        pulse_alpha = max(0, pulse_alpha)

        if pulse_radius >= max_coverage_radius:
            game_state = 'next_screen' # colocar o link

    # --- Desenho na Tela ---
    screen.blit(background_image, (0, 0))

    if game_state == 'menu':
        # Desenha o botão
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=15)
        screen.blit(text_surface, text_rect)

    if game_state == 'transition':
        # Desenha o efeito de pulso branco
        pulse_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(pulse_surface, (WHITE[0], WHITE[1], WHITE[2], pulse_alpha), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), pulse_radius)
        screen.blit(pulse_surface, (0, 0))

    pygame.display.flip()

    # --- Controle de FPS ---
    clock.tick(60)

# --- Finaliza o Pygame ---
pygame.quit()
sys.exit()