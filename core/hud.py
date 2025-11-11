import pygame
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
SPELL_ICONS_DIR = os.path.join(ASSETS_DIR, "spells")

class HUD:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.font = pygame.font.Font(None, 24)
        self.big = pygame.font.Font(None, 36)

        # cache de ícones carregados (Surface)
        self.icon_cache = {}

    def _load_icon(self, spell_name, size=(48,48)):
        """Tenta carregar assets/spells/<spell_name>.png; se não, cria placeholder."""
        if spell_name in self.icon_cache:
            return self.icon_cache[spell_name]

        path = os.path.join(SPELL_ICONS_DIR, f"{spell_name}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)
                self.icon_cache[spell_name] = img
                return img
            except Exception:
                pass

        # retângulo
        surf = pygame.Surface(size, pygame.SRCALPHA)
        # escolha de cores
        h = abs(hash(spell_name)) % 255
        color = ((100 + h) % 255, (60 + 2*h) % 255, (120 + 3*h) % 255)
        pygame.draw.rect(surf, color, (0,0,size[0], size[1]), border_radius=8)
        # letter
        label = self.font.render(spell_name[0].upper(), True, (255,255,255))
        surf.blit(label, (size[0]//2 - label.get_width()//2, size[1]//2 - label.get_height()//2))
        self.icon_cache[spell_name] = surf
        return surf

    def draw_bar(self, surface, x, y, width, height, value, max_value, color_fg=(0,255,0)):
        # placa
        pygame.draw.rect(surface, (30,30,30), (x-6, y-6, width+12, height+12), border_radius=8)
        pygame.draw.rect(surface, (120,0,0), (x, y, width, height), border_radius=6)
        pct = max(0.0, min(1.0, value / max_value if max_value else 0))
        fg_w = int(pct * width)
        pygame.draw.rect(surface, color_fg, (x, y, fg_w, height), border_radius=6)
        # numérico
        txt = f"{int(value)}/{int(max_value)}"
        text_surf = self.font.render(txt, True, (230,230,230))
        surface.blit(text_surf, (x + width + 8, y - 2))

    def draw_spell_cooldowns(self, surface, spells_cfg, player, xpos, ypos):
        """
        Desenha ícones dos feitiços e uma sobreposição indicando cooldown.
        spells_cfg: dict ordenado ou insertion-ordered com spell_name -> cfg
        """
        gap = 12
        icon_size = 48
        i = 0
        now = pygame.time.get_ticks()
        for name, cfg in spells_cfg.items():
            x = xpos + i * (icon_size + gap)
            y = ypos
            icon = self._load_icon(name, size=(icon_size, icon_size))
            surface.blit(icon, (x, y))

            # cooldown overlay
            last = player.last_cast.get(name, -99999999)
            cooldown_ms = cfg.get("cooldown_ms", 500)
            elapsed = now - last
            if elapsed < cooldown_ms:
                pct = elapsed / cooldown_ms
                # draw top-to-bottom mask for remaining cooldown
                remaining_h = int((1.0 - pct) * icon_size)
                overlay = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                overlay.fill((0,0,0,180))
                # cut bottom part so only top remaining shows
                # draw only top 'remaining_h' area
                mask_rect = pygame.Rect(0, 0, icon_size, remaining_h)
                surface.blit(overlay, (x, y), area=mask_rect)

                # show time left (s)
                left_s = max(0, (cooldown_ms - elapsed) // 1000)
                ttxt = self.font.render(str(left_s + 1 if left_s>=0 else 0), True, (255,255,255))
                surface.blit(ttxt, (x + icon_size//2 - ttxt.get_width()//2, y + icon_size//2 - ttxt.get_height()//2))

            # custo mana itens
            mtxt = f"{int(cfg.get('mana',0))}"
            m_surf = self.font.render(mtxt, True, (180,180,255))
            surface.blit(m_surf, (x+4, y+icon_size-18))

            i += 1

    def draw(self, surface, player, enemy, spells_cfg):
        # barras do jogador "esquerda"
        self.draw_bar(surface, 50, 40, 300, 20, player.hp, player.max_hp, color_fg=(60,220,100))
        self.draw_bar(surface, 50, 68, 300, 14, player.mana, player.max_mana, color_fg=(100,170,255))
        surface.blit(self.font.render(str(player.name), True, (230,230,230)), (50, 12))

        # barras do jogador "direita"
        x = self.screen_width - 350
        self.draw_bar(surface, x, 40, 300, 20, enemy.hp, enemy.max_hp, color_fg=(230,80,80))
        self.draw_bar(surface, x, 68, 300, 14, enemy.mana, enemy.max_mana, color_fg=(100,170,255))
        surface.blit(self.font.render(str(enemy.name), True, (230,230,230)), (x, 12))

        # feitiços e esperas
        self.draw_spell_cooldowns(surface, spells_cfg, player, 40, self.font.get_height() + 120)
