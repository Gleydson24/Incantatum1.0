import random
import pygame

def decide_enemy_action(enemy, player, spells_cfg):
    """
    Decide action for the enemy.
    Returns a dict with keys:
      - 'type': 'move' | 'cast' | 'shield' | 'idle'
      - 'dir': -1/1 for move or cast direction (optional)
      - 'spell': spell name to cast (optional)
    Simple rules:
      - If enemy low hp (<35%) and can cast protego -> shield
      - If at medium distance, cast ranged (expelliarmus/incendio) if available
      - Occasionally move left/right to approach/retreat
    """
    now = pygame.time.get_ticks()
    dist = abs(enemy.rect.centerx - player.rect.centerx)

    # jogadas defensivas
    if enemy.hp < enemy.max_hp * 0.35:
        if enemy.can_cast("protego", spells_cfg.get("protego")):
            return {"type": "shield"}

    # quando fica muito perto
    if dist < 160:
        # corpo a corpo
        if enemy.can_cast("incendio", spells_cfg.get("incendio")) and random.random() < 0.45:
            return {"type": "cast", "spell": "incendio", "dir": -1 if enemy.facing_left else 1}
        # afastamento
        if random.random() < 0.25:
            # passo para trás
            return {"type": "move", "dir": 1 if enemy.facing_left else -1}
        return {"type": "idle"}

    # média distância
    if dist < 420:
        if enemy.can_cast("expelliarmus", spells_cfg.get("expelliarmus")) and random.random() < 0.8:
            return {"type": "cast", "spell": "expelliarmus", "dir": -1 if enemy.facing_left else 1}
        if random.random() < 0.3:
            # passo para trás
            return {"type": "move", "dir": -1 if enemy.rect.centerx > player.rect.centerx else 1}

    # abordade: longe
    if dist >= 420:
        if random.random() < 0.9:
            return {"type": "move", "dir": -1 if enemy.rect.centerx > player.rect.centerx else 1}
        else:
            return {"type": "idle"}

    return {"type": "idle"}
