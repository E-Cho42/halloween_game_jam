import pygame as pg
import random


class Particle:
    def __init__(self, pos, color, lifetime=0.3):
        self.pos = pg.Vector2(pos)
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.radius = random.randint(2, 4)
        self.velocity = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

    def update(self, dt):
        self.age += dt
        self.pos += self.velocity
        # fade out alpha over time
        fade = max(0, 255 * (1 - self.age / self.lifetime))
        return fade > 0  # still alive?

    def draw(self, canvas, fade):
        alpha_surface = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
        pg.draw.circle(
            alpha_surface,
            (*self.color, int(fade)),
            (self.radius, self.radius),
            self.radius
        )
        canvas.blit(alpha_surface, (self.pos.x - self.radius, self.pos.y - self.radius))


class Projectile:
    def __init__(self, pos, direction, image, speed=12):
        self.pos = pg.Vector2(pos)
        self.image = pg.transform.scale(image, (32, 32))
        self.rect = self.image.get_rect(center=pos)
        self.alive = True
        self.particles = []
        self.speed = speed

        # ✅ Support for four directions (player) and Vector2 (boss)
        if isinstance(direction, str):  # Player projectile - four directions
            if direction == "right":
                self.velocity = pg.Vector2(1, 0)
            elif direction == "left":
                self.velocity = pg.Vector2(-1, 0)
            elif direction == "up":
                self.velocity = pg.Vector2(0, -1)
            elif direction == "down":
                self.velocity = pg.Vector2(0, 1)
        elif isinstance(direction, bool):
            # Player projectile — left or right (backward compatibility)
            self.velocity = pg.Vector2(1 if direction else -1, 0)
        else:
            # Boss projectile — arbitrary direction vector
            self.velocity = pg.Vector2(direction).normalize()

    def update(self, dt):
        # --- Movement ---
        self.pos += self.velocity * self.speed
        self.rect.center = self.pos

        # --- Trail particles ---
        for _ in range(2):
            self.particles.append(
                Particle(self.pos, (100, 149, 237))  # bluish particle
            )

        # --- Update particles ---
        alive_particles = []
        for p in self.particles:
            fade = 255 * (1 - p.age / p.lifetime)
            if p.update(dt):
                alive_particles.append(p)
        self.particles = alive_particles

        # --- Kill projectile if off-screen ---
        if not pg.Rect(0, 0, 800, 800).collidepoint(self.pos):
            self.alive = False

    def draw(self, canvas):
        # --- Draw projectile sprite ---
        canvas.blit(self.image, self.rect)

        # --- Draw particle trail ---
        for p in self.particles:
            fade = 255 * (1 - p.age / p.lifetime)
            p.draw(canvas, fade)