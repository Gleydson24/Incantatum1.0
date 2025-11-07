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

    # prefer defensives when low hp
    if enemy.hp < enemy.max_hp * 0.35:
        if enemy.can_cast("protego", spells_cfg.get("protego")):
            return {"type": "shield"}

    # if very close, chance to use heavy
    if dist < 160:
        # chance for close heavy attack (if has 'stupefy' or 'sectum' else use incendio)
        if enemy.can_cast("incendio", spells_cfg.get("incendio")) and random.random() < 0.45:
            return {"type": "cast", "spell": "incendio", "dir": -1 if enemy.facing_left else 1}
        # else melee idle (move away sometimes)
        if random.random() < 0.25:
            # step back
            return {"type": "move", "dir": 1 if enemy.facing_left else -1}
        return {"type": "idle"}

    # mid distance favors ranged
    if dist < 420:
        if enemy.can_cast("expelliarmus", spells_cfg.get("expelliarmus")) and random.random() < 0.8:
            return {"type": "cast", "spell": "expelliarmus", "dir": -1 if enemy.facing_left else 1}
        if random.random() < 0.3:
            # small reposition
            return {"type": "move", "dir": -1 if enemy.rect.centerx > player.rect.centerx else 1}

    # far: approach
    if dist >= 420:
        if random.random() < 0.9:
            return {"type": "move", "dir": -1 if enemy.rect.centerx > player.rect.centerx else 1}
        else:
            return {"type": "idle"}

    return {"type": "idle"}