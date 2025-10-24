import pygame as pg
import random
import math

class DashParticle:
    """Small fading particle for the dash effect."""
    def __init__(self, pos, color=(255, 180, 50)):
        self.pos = pg.Vector2(pos)
        self.color = color
        self.radius = random.randint(3, 6)
        self.lifetime = 0.3
        self.age = 0
        self.velocity = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * 40

    def update(self, dt):
        self.age += dt
        self.pos += self.velocity * dt

    def draw(self, canvas):
        if self.age < self.lifetime:
            alpha = max(0, 255 * (1 - self.age / self.lifetime))
            surf = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
            pg.draw.circle(surf, (*self.color, int(alpha)), (self.radius, self.radius), self.radius)
            canvas.blit(surf, (self.pos.x - self.radius, self.pos.y - self.radius))

    @property
    def alive(self):
        return self.age < self.lifetime


class MiniScarecrow:
    def __init__(self, pos):
        self.image = pg.image.load("Art/boss3M.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (60, 80))
        self.pos = pg.Vector2(pos)
        self.rect = self.image.get_rect(center=pos)
        self.health = 20
        self.alive = True
        self.direction = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.speed = random.uniform(60, 100)
        self.lifetime = random.uniform(3, 5)  # seconds before disappearing
        self.age = 0
        self.damage = 10

    def update(self, dt, player):
        if not self.alive:
            return

        # Wander movement
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # Slight random steering
        if random.random() < 0.02:
            angle = random.uniform(-0.5, 0.5)
            self.direction = self.direction.rotate(math.degrees(angle))

        # Lifetime decay
        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False

        # Player collision damage
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, self.rect.topleft)


class ScarecrowLord:
    def __init__(self, pos=(400, 300)):
        self.name = "Scarecrow Lord"
        self.pos = pg.Vector2(pos)
        self.image = pg.image.load("Art/boss3.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (220, 220))
        self.rect = self.image.get_rect(center=self.pos)
        self.max_health = 1500
        self.health = self.max_health
        self.alive = True

        # Movement / dash
        self.velocity = pg.Vector2(0, 0)
        self.speed = 120
        self.dash_speed = 400
        self.dash_timer = 0
        self.dash_cooldown = random.uniform(1.5, 2.5)
        self.is_dashing = False
        self.dash_target = pg.Vector2(self.pos)
        self.dash_particles = []

        # Minion management
        self.minions = []
        self.summon_timer = 0
        self.summon_cooldown = 3  # seconds between summons

    def update(self, dt, player):
        if not self.alive:
            return

        # === Dash Logic ===
        self.dash_timer += dt
        if not self.is_dashing and self.dash_timer > self.dash_cooldown:
            self.is_dashing = True
            self.dash_target = pg.Vector2(player.pos)
            direction = (self.dash_target - self.pos).normalize()
            self.velocity = direction * self.dash_speed
            self.dash_timer = 0
            self.dash_cooldown = random.uniform(1.0, 2.0)
        elif self.is_dashing:
            # Move and create dash particles
            self.pos += self.velocity * dt
            self.rect.center = self.pos
            self.dash_particles.append([pg.Vector2(self.pos), 0.4])

            # Stop dashing if close to target
            if self.pos.distance_to(self.dash_target) < 30:
                self.is_dashing = False
                self.velocity *= 0

        # === Dash Particles ===
        for particle in self.dash_particles[:]:
            particle[1] -= dt
            if particle[1] <= 0:
                self.dash_particles.remove(particle)

        # === Summon Minions ===
        self.summon_timer += dt
        if self.summon_timer >= self.summon_cooldown:
            self.summon_timer = 0
            self.summon_cooldown = random.uniform(4, 6)
            for _ in range(random.randint(2, 4)):
                offset = pg.Vector2(random.randint(-80, 80), random.randint(-80, 80))
                self.minions.append(MiniScarecrow(self.pos + offset))

        # === Update Minions ===
        for m in self.minions[:]:
            m.update(dt, player)
            if not m.alive or m.health <= 0:
                self.minions.remove(m)

        # === Damage Player on contact ===
        if self.rect.colliderect(player.rect):
            player.take_damage(15)

        self.rect.center = self.pos

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def draw(self, surface):
        # Draw dash particles
        for pos, life in self.dash_particles:
            alpha = int(255 * (life / 0.4))
            surf = pg.Surface((30, 30), pg.SRCALPHA)
            pg.draw.circle(surf, (255, 180, 50, alpha), (15, 15), 15)
            surface.blit(surf, (pos.x - 15, pos.y - 15))

        # Draw boss
        surface.blit(self.image, self.rect.topleft)

        # Draw minions
        for m in self.minions:
            m.draw(surface)

        # --- Health bar (like original Pumpking style) ---
        bar_width = 600
        bar_height = 20
        x, y = 100, 750

        # Background
        pg.draw.rect(surface, (50, 0, 0), (x, y, bar_width, bar_height))
        # Health fill
        pg.draw.rect(surface, (255, 80, 80),
                     (x, y, bar_width * (self.health / self.max_health), bar_height))
        # Outline
        pg.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 2)

        # Boss name text
        font = pg.font.Font(None, 48)
        text = font.render("Scarecrow Lord", True, (255, 200, 0))
        text_rect = text.get_rect(center=(x + bar_width // 2, y - 25))
        surface.blit(text, text_rect)
