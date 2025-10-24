import pygame as pg
import math
import random


class SpecterBride:
    def __init__(self, pos=(400, 300)):
        # === Basic stats ===
        self.name = "Specter Bride"
        self.pos = pg.Vector2(pos)
        self.max_health = 120
        self.health = self.max_health
        self.alive = True
        self.projectiles = []
        self.just_attacked = False

        # === Load image ===
        self.image = pg.image.load("Art/Specter_Bride.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (160, 160))
        self.rect = self.image.get_rect(center=self.pos)

        # === Movement + attack timers ===
        self.float_timer = 0
        self.attack_cooldown = 0.75
        self.attack_timer = random.uniform(0.25, 0.25)

        # === Dash variables ===
        self.dashing = False
        self.dash_cooldown = random.uniform(3.0, 6.0)
        self.dash_timer = self.dash_cooldown
        self.dash_speed = 700
        self.dash_duration = 0.2
        self.dash_time_left = 0

        # === Fade-in effect ===
        self.alpha = 0
        self.fade_in_speed = 200

    def update(self, dt, player):
        if not self.alive:
            return

        # === Fade in ===
        if self.alpha < 255:
            self.alpha += self.fade_in_speed * dt
            if self.alpha > 255:
                self.alpha = 255

        # === Floating motion ===
        self.float_timer += dt
        self.pos.x += math.sin(pg.time.get_ticks() * 0.001) * 40 * dt
        self.pos.y += math.cos(pg.time.get_ticks() * 0.0015) * 20 * dt
        self.rect.center = self.pos

        # === Attack logic ===
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.attack(player)
            self.attack_timer = self.attack_cooldown

        # === Dash logic ===
        self.handle_dash(dt, player)

        # === Update projectiles ===
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.alive:
                self.projectiles.remove(proj)

    def handle_dash(self, dt, player):
        self.dash_timer -= dt
        if not self.dashing and self.dash_timer <= 0:
            # Start dash toward or away from player
            direction = (pg.Vector2(player.pos) - self.pos).normalize()
            if random.random() < 0.5:  # 50% chance to dash away
                direction = -direction
            self.vel = direction * self.dash_speed
            self.dashing = True
            self.dash_time_left = self.dash_duration
            self.alpha = 120

        if self.dashing:
            self.pos += self.vel * dt
            self.rect.center = self.pos
            self.dash_time_left -= dt
            if self.dash_time_left <= 0:
                self.dashing = False
                self.vel = pg.Vector2(0, 0)
                self.alpha = 255
                self.dash_timer = random.uniform(3.0, 6.0)

    def attack(self, player):
        """Launch a slow homing wisp toward the player."""
        direction = (pg.Vector2(player.pos) - self.pos).normalize()
        self.projectiles.append(WispProjectile(self.pos, direction))
        self.just_attacked = True

    def draw(self, canvas):
        if not self.alive:
            return

        # --- Glow effect ---
        glow_radius = 90
        glow_surf = pg.Surface((glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
        pg.draw.circle(glow_surf, (200, 200, 255, 40),
                       (glow_radius, glow_radius), glow_radius)
        canvas.blit(glow_surf, (self.pos.x - glow_radius, self.pos.y - glow_radius))

        # --- Boss sprite ---
        image = self.image.copy()
        image.set_alpha(self.alpha)
        canvas.blit(image, self.rect)

        # --- Projectiles ---
        for proj in self.projectiles:
            proj.draw(canvas)

        # --- Health bar (same style as Pump-King) ---
        bar_width = 600
        bar_height = 20
        x, y = 100, 750

        # Background (empty)
        pg.draw.rect(canvas, (50, 0, 0), (x, y, bar_width, bar_height))
        # Filled portion
        pg.draw.rect(canvas, (255, 80, 80),
                     (x, y, bar_width * (self.health / self.max_health), bar_height))
        # Border
        pg.draw.rect(canvas, (0, 0, 0), (x, y, bar_width, bar_height), 2)

        # Boss name text
        font = pg.font.Font(None, 48)
        text = font.render("Specter Bride", True, (255, 200, 0))
        text_rect = text.get_rect(center=(x + bar_width // 2, y - 25))
        canvas.blit(text, text_rect)

    def take_damage(self, amount):
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def reset(self):
        """Reset between fights."""
        self.health = self.max_health
        self.alive = True
        self.projectiles.clear()
        self.attack_timer = random.uniform(1.0, 2.0)
        self.just_attacked = False
        self.dashing = False
        self.dash_timer = random.uniform(3.0, 6.0)
        self.alpha = 0


# === Simple projectile class for Specter Bride attacks ===
class WispProjectile:
    # --- Load once, globally ---
    wisp_image = None

    def __init__(self, pos, direction):
        self.pos = pg.Vector2(pos)
        self.vel = direction * 150
        self.alive = True
        self.lifetime = 3.0
        self.radius = 12

        # Load wisp image once
        if WispProjectile.wisp_image is None:
            img = pg.image.load("Art/whisp.png").convert_alpha()
            WispProjectile.wisp_image = pg.transform.scale(img, (48, 48))

        self.image = WispProjectile.wisp_image
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # --- Trail system ---
        self.trail = []  # list of (pos, life)
        self.trail_timer = 0.0
        self.trail_interval = 0.05  # seconds between new trail points

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if self.lifetime <= 0:
            self.alive = False

        # --- Trail logic ---
        self.trail_timer += dt
        if self.trail_timer >= self.trail_interval:
            self.trail.append([self.pos.copy(), 0.6])  # (position, lifetime)
            self.trail_timer = 0.0

        # Fade old trail particles
        for t in self.trail:
            t[1] -= dt
        self.trail = [t for t in self.trail if t[1] > 0]

    def draw(self, surface):
        # --- Draw trail ---
        for pos, life in self.trail:
            alpha = int(180 * (life / 0.6))
            scale = 0.6 + 0.4 * (life / 0.6)
            w, h = self.image.get_size()
            trail_img = pg.transform.smoothscale(self.image, (int(w * scale), int(h * scale)))
            trail_img.set_alpha(alpha)
            rect = trail_img.get_rect(center=(int(pos.x), int(pos.y)))
            surface.blit(trail_img, rect)

        # --- Draw main wisp ---
        surface.blit(self.image, self.rect)
