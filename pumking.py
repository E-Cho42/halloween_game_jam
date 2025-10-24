import pygame as pg
import random
from projectile import Projectile
import math

class Pumpking:
    def __init__(self, pos):
        # --- Setup ---
        self.image = pg.transform.scale(pg.image.load("Art/boss1.png"), (256, 256))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.Vector2(pos)
        self.max_health = 800
        self.health = self.max_health
        self.speed = 80  # movement speed
        self.direction = pg.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        self.attack_cooldown = 2.0
        self.attack_timer = .5  # starts soon after appearing
        self.projectiles = []
        self.just_attacked = False
        # Movement bounds for 800x800 window
        self.bounds = pg.Rect(0, 0, 800, 800)

        # Alive status
        self.alive = True
    def radial_attack(self):
        self.just_attacked = True
        """Fires 8 slow projectiles in all directions (360° spread),
        spawned from the boss' actual center to avoid offset."""
        num_projectiles = 8
        angle_step = 2 * math.pi / num_projectiles
        attack_image = pg.image.load('Art/boss_attack.png').convert_alpha()
        projectile_speed = 12  # keep same slow speed as ghost shots

        proj_pos = self.rect.center  # spawn exactly at boss center

        for i in range(num_projectiles):
            angle = i * angle_step
            direction = pg.Vector2(math.cos(angle), math.sin(angle))
            if direction.length() != 0:
                direction = direction.normalize()
            proj = Projectile(proj_pos, direction, attack_image, speed=projectile_speed)
            self.projectiles.append(proj)


    def update(self, dt, player):
        if not self.alive:
            return

        # --- Movement ---
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # --- Bounce inside 800x800 window ---
        if self.rect.left < self.bounds.left or self.rect.right > self.bounds.right:
            self.direction.x *= -1
            self.pos.x = max(self.bounds.left + self.rect.width / 2,
                            min(self.bounds.right - self.rect.width / 2, self.pos.x))

        if self.rect.top < self.bounds.top or self.rect.bottom > self.bounds.bottom:
            self.direction.y *= -1
            self.pos.y = max(self.bounds.top + self.rect.height / 2,
                            min(self.bounds.bottom - self.rect.height / 2, self.pos.y))

        # --- Attacking ---
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.attack_timer = self.attack_cooldown

            # Alternate between ghost attack and radial attack 💥
            if random.random() < 0.5:
                self.shoot_ghosts(player.pos)
            else:
                self.radial_attack()
        # --- Direct contact damage ---
        if self.alive and self.rect.colliderect(player.rect):
            if hasattr(player, "take_damage"):
                player.take_damage(10)  # adjust damage as needed


        # --- Update projectiles ---
        for proj in list(self.projectiles):
            proj.update(dt)

            # ✅ Damage check
            if hasattr(player, "rect") and proj.rect.colliderect(player.rect):
                if hasattr(player, "take_damage") and not player.dead:
                    player.take_damage(20)
                self.projectiles.remove(proj)
            elif not proj.alive:
                self.projectiles.remove(proj)

        # --- Death check ---
        if self.health <= 0:
            self.alive = False


    def shoot_ghosts(self, player_pos):
        self.just_attacked = True
        """Fires 3 ghost projectiles toward the player."""
        ghost_img = pg.image.load("Art/boss_attack.png").convert_alpha()
        for i in range(3):
            direction = pg.Vector2(player_pos) - self.pos
            if direction.length() > 0:
                direction = direction.normalize()
            # Add random spread
            spread = pg.Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
            velocity = (direction + spread).normalize() * 8
            proj = Projectile(self.pos, velocity.x > 0, ghost_img, speed=12)
            self.projectiles.append(proj)

    def draw(self, canvas):
        if not self.alive:
            return

        # --- Boss sprite ---
        canvas.blit(self.image, self.rect)

        # --- Projectiles ---
        for proj in self.projectiles:
            proj.draw(canvas)

        # --- Health bar ---
        bar_width = 600
        bar_height = 20
        x, y = 100, 750

        # Background (empty bar)
        pg.draw.rect(canvas, (50, 0, 0), (x, y, bar_width, bar_height))
        # Health amount (filled part)
        pg.draw.rect(canvas, (255, 80, 80),
                    (x, y, bar_width * (self.health / self.max_health), bar_height))
        # Outline
        pg.draw.rect(canvas, (0, 0, 0), (x, y, bar_width, bar_height), 2)

        # --- Boss name text ---
        font = pg.font.Font(None, 48)  # You can replace None with a font file if you want a custom one
        text = font.render("Pump-King", True, (255, 200, 0))  # orange-yellow color
        text_rect = text.get_rect(center=(x + bar_width // 2, y - 25))
        canvas.blit(text, text_rect)

    def take_damage(self, amount):
        if self.alive:
            self.health -= amount
            if self.health <= 0:
                self.alive = False
