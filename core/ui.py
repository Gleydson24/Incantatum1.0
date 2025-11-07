import pygame
import os
import sys
from core.transitions import fade_in, fade_out

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')

class Button:
    def __init__(self, rect, text, font, base_color, hover_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        label = self.font.render(self.text, True, (255, 255, 255))
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

class BaseScreen:
    def __init__(self, screen, bg_file):
        self.screen = screen
        bg_path = os.path.join(ASSETS_DIR, 'backgrounds', bg_file)
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, (960, 540))

class MenuScreen(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen, 'menu.png')
        self.font = pygame.font.Font(None, 60)
        self.button = Button((380, 400, 200, 60), "Iniciar", self.font, (80, 80, 180), (130, 130, 250))

    def run(self):
        fade_in(self.screen)
        running = True
        while running:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and self.button.hovered:
                    fade_out(self.screen)
                    return "char_select"

            self.button.update(mouse)
            self.screen.blit(self.bg, (0, 0))
            title = self.font.render("INCANTATUM", True, (255, 255, 255))
            self.screen.blit(title, (330, 100))
            self.button.draw(self.screen)
            pygame.display.update()

class CharacterSelectScreen(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen, 'select.png')
        self.font = pygame.font.Font(None, 40)
        self.characters = ["wizard1.png", "wizard2.png"]

    def run(self):
        fade_in(self.screen)
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, char in enumerate(self.characters):
                        if 200 + i * 300 < mouse[0] < 400 + i * 300 and 200 < mouse[1] < 400:
                            fade_out(self.screen)
                            return f"selected:{char}"

            self.screen.blit(self.bg, (0, 0))
            title = self.font.render("Escolha seu Personagem", True, (255, 255, 255))
            self.screen.blit(title, (250, 100))
            for i, char in enumerate(self.characters):
                img = pygame.image.load(os.path.join(ASSETS_DIR, 'characters', char)).convert_alpha()
                img = pygame.transform.scale(img, (150, 150))
                rect = img.get_rect(center=(300 + i * 300, 300))
                self.screen.blit(img, rect)
            pygame.display.update()

class OpponentSelectScreen(CharacterSelectScreen):
    def run(self):
        fade_in(self.screen)
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, char in enumerate(self.characters):
                        if 200 + i * 300 < mouse[0] < 400 + i * 300 and 200 < mouse[1] < 400:
                            fade_out(self.screen)
                            return f"selected:{char}"

            self.screen.blit(self.bg, (0, 0))
            title = self.font.render("Escolha o Oponente", True, (255, 255, 255))
            self.screen.blit(title, (280, 100))
            for i, char in enumerate(self.characters):
                img = pygame.image.load(os.path.join(ASSETS_DIR, 'characters', char)).convert_alpha()
                img = pygame.transform.scale(img, (150, 150))
                rect = img.get_rect(center=(300 + i * 300, 300))
                self.screen.blit(img, rect)
            pygame.display.update()

class DuelScreen(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen, 'duel.png')
        self.font = pygame.font.Font(None, 50)
        self.hp_player = 100
        self.hp_enemy = 100

    def run(self, player, enemy):
        fade_in(self.screen)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.hp_enemy -= 10
                    if self.hp_enemy <= 0:
                        fade_out(self.screen)
                        return "victory"

            self.screen.blit(self.bg, (0, 0))
            player_img = pygame.image.load(os.path.join(ASSETS_DIR, 'characters', player)).convert_alpha()
            enemy_img = pygame.image.load(os.path.join(ASSETS_DIR, 'characters', enemy)).convert_alpha()
            self.screen.blit(pygame.transform.scale(player_img, (200, 200)), (150, 250))
            self.screen.blit(pygame.transform.scale(enemy_img, (200, 200)), (610, 250))

            pygame.draw.rect(self.screen, (255, 0, 0), (150, 100, self.hp_player * 2, 20))
            pygame.draw.rect(self.screen, (0, 255, 0), (610, 100, self.hp_enemy * 2, 20))
            pygame.display.update()

class VictoryScreen(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen, 'victory.png')
        self.font = pygame.font.Font(None, 60)

    def run(self):
        fade_in(self.screen)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    fade_out(self.screen)
                    return "menu"

            self.screen.blit(self.bg, (0, 0))
            text = self.font.render("Vitória! Pressione ENTER", True, (255, 255, 255))
            self.screen.blit(text, (250, 250))
            pygame.display.update()