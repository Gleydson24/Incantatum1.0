import pygame
import os
import random
import time

from core.player import Player
from core.spell import Spell
from core.hud import HUD
from core.transitions import fade_in, fade_out
from core.enemy_ai import decide_enemy_action

FPS = 60
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MAP_PATH = os.path.join(ASSETS_DIR, "map.png")

# feitiços
SPELLS = {
    "expelliarmus": {"speed": 14, "radius": 10, "damage": 18, "mana": 18, "color": (160,160,255), "cooldown_ms": 800, "type": "proj"},
    "stupefy":      {"speed": 13, "radius": 12, "damage": 25, "mana": 25, "color": (200,200,110), "cooldown_ms": 1200, "type": "proj"},
    "protego":      {"speed": 0,  "radius": 0,  "damage": 0,  "mana": 10, "color": (100,180,255), "cooldown_ms": 1500, "type": "shield", "shield_ms": 900},
    "lumos":        {"speed": 18, "radius": 8,  "damage": 12, "mana": 12, "color": (255,255,200), "cooldown_ms": 500,  "type": "proj"},
    "incendio":     {"speed": 11, "radius": 14, "damage": 30, "mana": 30, "color": (255,120,60),  "cooldown_ms": 1800, "type": "proj"}
}

# mapeamento
KEY_SPELL_MAP = {
    pygame.K_q: "expelliarmus",
    pygame.K_w: "stupefy",
    pygame.K_e: "protego",
    pygame.K_r: "lumos",
    pygame.K_t: "incendio"
}

def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        s = pygame.Surface((200,200))
        s.fill((40,40,40))
        return s

def game_loop(screen, jogador_name, oponente_name, SCREEN_WIDTH=1366, SCREEN_HEIGHT=768):
    clock = pygame.time.Clock()

    # background
    if os.path.exists(MAP_PATH):
        background = safe_load_image(MAP_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(12 + 20 * t)
            g = int(10 + 12 * t)
            b = int(18 + 22 * t)
            pygame.draw.line(background, (r,g,b), (0,y), (SCREEN_WIDTH,y))

    floor_rect = pygame.Rect(5, SCREEN_HEIGHT - 140, SCREEN_WIDTH - 10, 120)

    # players
    player = Player(150, floor_rect.top - 10, floor_rect, screen_height=SCREEN_HEIGHT)
    enemy = Player(SCREEN_WIDTH - 150, floor_rect.top - 10, floor_rect, screen_height=SCREEN_HEIGHT)
    enemy.facing_left = True

    player.name = jogador_name
    enemy.name = oponente_name

    # HUD
    hud = HUD(SCREEN_WIDTH)

    spells_active = []
    running = True
    last_ai_think = pygame.time.get_ticks()
    AI_THINK_MS = 400

    # fade in
    fade_in(screen, color=(0,0,0), speed=12)

    # sobreposição mensagens
    message = ""
    message_timer = 0

    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = pause_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if not paused:
                        return

                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.try_jump()

                # feitiços "chave"
                if event.key in KEY_SPELL_MAP:
                    name = KEY_SPELL_MAP[event.key]
                    cfg = SPELLS.get(name)
                    if player.can_cast(name, cfg):
                        s = player.cast_spell(name, cfg)
                        if s:
                            s.owner = "player"
                            spells_active.append(s)
                        # shield handled inside cast_spell
                    else:
                        message = "Energia insuficiente ou cooldown!"
                        message_timer = now + 1000  # 1s

        # pensamento IA
        if now - last_ai_think >= AI_THINK_MS:
            last_ai_think = now
            action = decide_enemy_action(enemy, player, SPELLS)
            if action["type"] == "cast":
                spell_name = action.get("spell")
                cfg = SPELLS.get(spell_name)
                if enemy.can_cast(spell_name, cfg):
                    s = enemy.cast_spell(spell_name, cfg, direction=-1 if enemy.facing_left else 1)
                    if s:
                        s.owner = "enemy"
                        spells_active.append(s)
            elif action["type"] == "shield":
                if enemy.can_cast("protego", SPELLS.get("protego")):
                    enemy.cast_spell("protego", SPELLS.get("protego"))
            elif action["type"] == "move":
                dirx = action.get("dir", 0)
                enemy.vx = dirx * enemy.speed
                enemy.facing_left = True if dirx < 0 else False

        # física player e animação
        player.handle_input()
        player.apply_gravity()
        player.update_animation(dt)

        enemy.apply_gravity()
        enemy.update_animation(dt)
        enemy.rect.x += int(enemy.vx)
        enemy.vx = 0

        # atualização feitiços
        to_remove = []
        for i, s in enumerate(spells_active):
            s.update()
            if s.owner == "player":
                if enemy.shield_active and s.collides_with(enemy):
                    to_remove.append(i)
                    continue
                if s.collides_with(enemy):
                    # combo + crit
                    dmg, crit = player.apply_combo_bonus(s.damage)
                    enemy.hp = max(0, enemy.hp - dmg)
                    player.register_hit()
                    to_remove.append(i)
                    continue
            elif s.owner == "enemy":
                if player.shield_active and s.collides_with(player):
                    to_remove.append(i)
                    continue
                if s.collides_with(player):
                    dmg, crit = enemy.apply_combo_bonus(s.damage)
                    player.hp = max(0, player.hp - dmg)
                    enemy.register_hit()
                    to_remove.append(i)
                    continue

            if s.x < -300 or s.x > SCREEN_WIDTH + 300:
                to_remove.append(i)

        for idx in sorted(set(to_remove), reverse=True):
            spells_active.pop(idx)

        # regenerar mana
        player.regen_mana(dt)
        enemy.regen_mana(dt)

        # empate
        screen.blit(background, (0,0))
        pygame.draw.rect(screen, (28,28,28), floor_rect)

        player.draw(screen)
        enemy.draw(screen)

        # feitiços halo
        for s in spells_active:
            s.draw(screen)
            halo = pygame.Surface((s.radius*6, s.radius*6), pygame.SRCALPHA)
            pygame.draw.circle(halo, (s.color[0], s.color[1], s.color[2], 50), (s.radius*3, s.radius*3), s.radius*2)
            screen.blit(halo, (int(s.x - s.radius*3), int(s.y - s.radius*3)), special_flags=pygame.BLEND_ADD)

        # HUD (feitiços)
        spells_ordered = {
            "expelliarmus": SPELLS["expelliarmus"],
            "stupefy": SPELLS["stupefy"],
            "protego": SPELLS["protego"],
            "lumos": SPELLS["lumos"],
            "incendio": SPELLS["incendio"]
        }
        hud.draw(screen, player, enemy, spells_ordered)

        # sorteio de mensagem
        if message and now < message_timer:
            msg_s = pygame.font.Font(None, 28).render(message, True, (255,200,80))
            screen.blit(msg_s, (SCREEN_WIDTH//2 - msg_s.get_width()//2, SCREEN_HEIGHT - 80))

        # verificação final
        if player.hp <= 0 or enemy.hp <= 0:
            if player.hp <= 0 and enemy.hp <= 0:
                winner = "EMPATE!"
            elif enemy.hp <= 0:
                winner = f"{player.name} VENCEU!"
            else:
                winner = f"{enemy.name} VENCEU!"

            big_font = pygame.font.Font(None, 72)
            surface = big_font.render(winner, True, (255,255,255))
            screen.blit(surface, (SCREEN_WIDTH // 2 - surface.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - surface.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(1500)
            fade_out(screen, color=(0,0,0), speed=12)
            return

        pygame.display.flip()
