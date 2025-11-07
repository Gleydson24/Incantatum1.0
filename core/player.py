import pygame
import os
import random
from core.spell import Spell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_ASSETS = os.path.join(BASE_DIR, "..", "assets", "player")

class Player:
    def __init__(self, x, y, floor_rect, screen_height=None):
        self.floor_rect = floor_rect
        self.speed = 4.0
        self.vx = 0
        self.vy = 0
        self.jump_power = -12
        self.gravity = 0.65

        if screen_height:
            self.scale = screen_height / 768
        else:
            self.scale = 1

        def load_frame(fname):
            path = os.path.join(PLAYER_ASSETS, fname)
            try:
                img = pygame.image.load(path).convert_alpha()
                w = int(128 * self.scale)
                h = int(128 * self.scale)
                return pygame.transform.smoothscale(img, (w, h))
            except Exception:
                s = pygame.Surface((int(128*self.scale), int(128*self.scale)), pygame.SRCALPHA)
                s.fill((80,80,120))
                return s

        # animation frames
        self.idle_frames = [load_frame(f"idle{i}.png") for i in range(1,5)]
        self.walk_frames = [load_frame(f"walk{i}.png") for i in range(1,5)]
        self.base_image = self.idle_frames[0]
        self.rect = self.base_image.get_rect(midbottom=(x, floor_rect.top))

        # animation timers
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay_walk = 80
        self.frame_delay_idle = 180

        # stats
        self.hp = 100
        self.max_hp = 100
        self.mana = 100
        self.max_mana = 100
        self.mana_regen_per_sec = 12.0

        # cooldowns: map spell_name -> last_cast_time(ms)
        self.last_cast = {}
        # individual cast cooldown default (ms) can be provided externally
        # combo system
        self.combo_count = 0
        self.combo_timer_ends = 0  # ms when combo expires
        self.combo_window_ms = 2500  # time to chain next hit

        # shield
        self.shield_active = False
        self.shield_ends_at = 0

        # attack control
        self.is_walking = False
        self.facing_left = False
        self.name = "Player"

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.facing_left = True
            self.is_walking = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.facing_left = False
            self.is_walking = True
        else:
            self.is_walking = False

        new_rect = self.rect.move(int(self.vx), 0)
        if new_rect.left < self.floor_rect.left:
            new_rect.left = self.floor_rect.left
        if new_rect.right > self.floor_rect.right:
            new_rect.right = self.floor_rect.right
        self.rect = new_rect

    def try_jump(self):
        if abs(self.rect.bottom - self.floor_rect.top) <= 6:
            self.vy = self.jump_power

    def apply_gravity(self):
        self.vy += self.gravity
        self.rect.y += int(self.vy)
        if self.rect.bottom >= self.floor_rect.top:
            self.rect.bottom = self.floor_rect.top
            self.vy = 0

    def update_animation(self, dt):
        delay = self.frame_delay_walk if self.is_walking else self.frame_delay_idle
        self.frame_timer += dt
        if self.frame_timer >= delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % 4
            if self.is_walking:
                self.base_image = self.walk_frames[self.current_frame]
            else:
                self.base_image = self.idle_frames[self.current_frame]

        # shield expire
        if self.shield_active and pygame.time.get_ticks() >= self.shield_ends_at:
            self.shield_active = False

        # combo expire
        if self.combo_count > 0 and pygame.time.get_ticks() >= self.combo_timer_ends:
            self.combo_count = 0

    def draw(self, screen):
        image = pygame.transform.flip(self.base_image, True, False) if self.facing_left else self.base_image
        screen.blit(image, self.rect)
        if self.shield_active:
            r = pygame.Rect(self.rect.left-6, self.rect.top-6, self.rect.width+12, self.rect.height+12)
            surf = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (100,180,255,120), surf.get_rect(), 6)
            screen.blit(surf, (r.left, r.top))

    def can_cast(self, spell_name, cfg=None):
        """
        cfg: optional dict with keys 'mana' and 'cooldown_ms'
        returns True if enough mana and cooldown expired
        """
        now = pygame.time.get_ticks()
        if cfg is None:
            cfg = Spell.config(spell_name) or {}

        cooldown_ms = cfg.get("cooldown_ms", 200)
        mana_cost = cfg.get("mana", 0)
        last = self.last_cast.get(spell_name, -9999999)
        if now - last < cooldown_ms:
            return False
        if self.mana < mana_cost:
            return False
        return True

    def cast_spell(self, spell_name, cfg=None, direction=None):
        """
        Attempts to cast; deducts mana and registers cooldown.
        Returns Spell object or None (for non-projectile spells like protego).
        """
        now = pygame.time.get_ticks()
        if cfg is None:
            cfg = Spell.config(spell_name) or {}

        if not self.can_cast(spell_name, cfg):
            return None

        mana_cost = cfg.get("mana", 0)
        self.mana = max(0, self.mana - mana_cost)
        cooldown_ms = cfg.get("cooldown_ms", 200)
        self.last_cast[spell_name] = now

        # shield spells handled here
        if cfg.get("type") == "shield" or spell_name == "protego":
            self.activate_shield(duration_ms=cfg.get("shield_ms", 800))
            return None

        # projectile
        dirx = -1 if self.facing_left else 1
        if direction is not None:
            dirx = direction

        sx = self.rect.centerx + (dirx * (self.rect.width // 2 + 6))
        sy = self.rect.centery - 6
        speed = cfg.get("speed", 8)
        radius = cfg.get("radius", 8)
        damage = cfg.get("damage", 10)
        color = cfg.get("color", (200,200,200))

        s = Spell(sx, sy, dirx * speed, 0, radius, damage, color, owner="player")
        s.owner = "player"
        return s

    def register_hit(self):
        """
        Called when this player's attack lands on the opponent.
        Increments combo and sets combo timer.
        """
        self.combo_count += 1
        now = pygame.time.get_ticks()
        self.combo_timer_ends = now + self.combo_window_ms

    def apply_combo_bonus(self, base_damage):
        """
        Apply combo multiplier and critical chance.
        combo adds 15% damage per hit (stacking), up to a cap.
        Critical chance 10% doubles damage.
        """
        combo_mult = 1.0 + min(self.combo_count, 6) * 0.15  # cap at +90% if many
        damage = base_damage * combo_mult
        # critical
        if random.random() < 0.10:
            damage = int(damage * 2.0)
            critical = True
        else:
            damage = int(damage)
            critical = False
        return damage, critical

    def activate_shield(self, duration_ms=800):
        self.shield_active = True
        self.shield_ends_at = pygame.time.get_ticks() + duration_ms

    def regen_mana(self, dt):
        # dt in ms
        self.mana += (self.mana_regen_per_sec * (dt / 1000.0))
        if self.mana > self.max_mana:
            self.mana = self.max_mana