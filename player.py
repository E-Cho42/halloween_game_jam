import pygame as pg
import math
from projectile import Projectile
import random 

class player():
    def __init__(self, pos, masked, direction, image_left, image_right, speed, masked_left, masked_right ):
        self.pos = pos
        self.masked = masked
        # True = right, False = left
        self.direction = direction
        self.image = image_left
        self.image_right = image_right
        self.speed = speed
        self.masked_left = masked_left
        self.masked_right = masked_right
        
        self.dead = False
        self.death_timer = 0
        self.death_fade_alpha = 0

        # dash variables
        self.dashing = False
        self.dash_speed = 20
        self.dash_time = 0.2  # seconds
        self.dash_timer = 0
        self.dash_cooldown = 1.0  # seconds between dashes
        self.cooldown_timer = 0
        
        self.projectiles = []
        self.attack_cooldown = 0.3  # seconds
        self.attack_timer = 0
        
        self.foot_particles = []
        self.foot_timer = 0
        self.foot_cooldown = 0.15  # seconds between footsteps
        
        self.max_health = 100
        self.current_health = 75
        self.display_health = 75  # for smooth animation
        self.healing = False
        self.heal_amount = 40
        self.heal_speed = 80  # how fast the bar refills visually
        self.max_flasks = 3
        self.current_flasks = 3
        self.heal_timer = 0
        self.heal_duration = 1.0  # seconds of healing animation

        # ✅ Added collision rect for boss projectile detection
        self.rect = self.image_right.get_rect(topleft=self.pos)

        # --- Hit effect ---
        self.hit_flash_alpha = 0
        self.hit_particles = []

    
    def player_move(self):
        if self.dead:
            return
        keys = pg.key.get_pressed()

        # Base movement vector
        move_x, move_y = 0, 0
        if keys[pg.K_a]:
            self.direction = False
            move_x -= 1
        if keys[pg.K_d]:
            self.direction = True
            move_x += 1
        if keys[pg.K_w]:
            move_y -= 1
        if keys[pg.K_s]:
            move_y += 1

        # ✅ Keep player inside arena
        arena_rect = pg.Rect(0, 0, 800, 800)
        self.rect.clamp_ip(arena_rect)
        self.pos[0], self.pos[1] = self.rect.topleft

        # normalize diagonal movement
        magnitude = math.hypot(move_x, move_y)
        if magnitude > 0:
            move_x /= magnitude
            move_y /= magnitude

        # use dash speed if dashing
        current_speed = self.dash_speed if self.dashing else self.speed

        # apply movement
        self.pos[0] += move_x * current_speed
        self.pos[1] += move_y * current_speed

        # ✅ Keep collision rect in sync with movement
        self.rect.topleft = self.pos
        
        moving = any(pg.key.get_pressed()[k] for k in [pg.K_a, pg.K_d, pg.K_w, pg.K_s])
        if moving:
            self.foot_timer -= 1 / 60  # assuming roughly 60 fps
            if self.foot_timer <= 0:
                self.foot_timer = self.foot_cooldown
                # spawn a footstep particle at player’s feet
                self.foot_particles.append(FootstepParticle([self.pos[0] + 64, self.pos[1] + 128]))

    def update_footsteps(self, dt):
        for f in self.foot_particles:
            f.update(dt)
        # remove finished particles
        self.foot_particles = [f for f in self.foot_particles if f.timer > 0]

    def draw_footsteps(self, canvas):
        for f in self.foot_particles:
            f.draw(canvas)
        
    def player_mask_check(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_m:
                self.masked = not self.masked
    
    def player_dash(self, event):
        if self.dead:
            return
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and not self.dashing and self.cooldown_timer <= 0:
                self.dashing = True
                self.dash_timer = self.dash_time
                self.cooldown_timer = self.dash_cooldown

    def update_dash(self, dt):
        """Updates dash timers."""
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        if self.dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False

    def draw(self, canvas):
        # drawing player
        if self.masked:
            if self.direction:
                canvas.blit(self.masked_right, self.pos)
            else:
                canvas.blit(self.masked_left, self.pos)
        else:        
            if self.direction:
                canvas.blit(self.image_right, self.pos)
            else:
                canvas.blit(self.image, self.pos)
        # draw projectiles
        for proj in self.projectiles:
            proj.draw(canvas)

        # ✅ draw hit effects
        self.draw_hit_effects(canvas)

    def draw_dash_indicator(self, canvas, dt):
        bar_x, bar_y = 20, 80
        bar_width, bar_height = 200, 20
        bar_color = (79, 121, 66)
        fade_delay = 2.0
        fade_speed = 100

        if not hasattr(self, "flash_alpha"):
            self.flash_alpha = 0
            self.was_ready = True
            self.fade_alpha = 255
            self.inactive_timer = 0

        ratio = 1 - (self.cooldown_timer / self.dash_cooldown)
        ratio = max(0, min(1, ratio))

        is_ready = self.cooldown_timer <= 0

        if not is_ready or self.dashing:
            self.inactive_timer = 0
            self.fade_alpha = 255
        else:
            self.inactive_timer += dt

        if is_ready and not self.was_ready:
            self.flash_alpha = 255
            self.fade_alpha = 255
            self.inactive_timer = 0

        self.was_ready = is_ready

        if self.flash_alpha > 0:
            self.flash_alpha -= 10

        if self.inactive_timer > fade_delay:
            self.fade_alpha -= fade_speed * dt
            self.fade_alpha = max(0, self.fade_alpha)

        if self.fade_alpha > 0:
            surface = pg.Surface((bar_width, bar_height), pg.SRCALPHA)
            pg.draw.rect(surface, (30, 30, 30, int(self.fade_alpha * 0.5)), (0, 0, bar_width, bar_height))
            pg.draw.rect(surface, (*bar_color, int(self.fade_alpha)), (0, 0, bar_width * ratio, bar_height))
            canvas.blit(surface, (bar_x, bar_y))

            if self.flash_alpha > 0:
                flash_surface = pg.Surface((bar_width, bar_height), pg.SRCALPHA)
                pg.draw.rect(flash_surface, (255, 255, 255, self.flash_alpha), (0, 0, bar_width, bar_height))
                canvas.blit(flash_surface, (bar_x, bar_y))
                
    def player_attack(self, event):
        if self.dead:
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_f:
            if self.attack_timer <= 0:
                attack_image = pg.image.load('Art/attack.png').convert_alpha()
                proj_pos = (self.pos[0] + 64, self.pos[1] + 64)
                self.projectiles.append(Projectile(proj_pos, self.direction, attack_image))
                self.attack_timer = self.attack_cooldown
                
    def update_attacks(self, dt, boss):
        if self.attack_timer > 0:
            self.attack_timer -= dt

        for proj in self.projectiles:
            proj.update(dt)

        self.projectiles = [p for p in self.projectiles if p.alive]
        for proj in self.projectiles:
            if boss.alive and boss.rect.colliderect(proj.rect):
                boss.take_damage(20)
                proj.alive = False
        
    def player_heal(self, event):
        if self.dead:
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_h:
            if not self.healing and self.current_flasks > 0 and self.current_health < self.max_health:
                self.healing = True
                self.heal_timer = self.heal_duration
                self.current_flasks -= 1

    def update_heal(self, dt):
        if self.healing:
            self.heal_timer -= dt
            heal_progress = 1 - (self.heal_timer / self.heal_duration)
            heal_progress = max(0, min(1, heal_progress))
            
            target_health = min(self.current_health + self.heal_amount, self.max_health)
            self.display_health = self.current_health + (target_health - self.current_health) * heal_progress

            if self.heal_timer <= 0:
                self.healing = False
                self.current_health = target_health
                self.display_health = self.current_health
        else:
            if self.display_health < self.current_health:
                self.display_health += self.heal_speed * dt
                if self.display_health > self.current_health:
                    self.display_health = self.current_health

    def draw_health_bar(self, canvas):
        bar_width = 200
        bar_height = 20
        x, y = 20, 20

        pg.draw.rect(canvas, (40, 0, 0), (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pg.draw.rect(canvas, (100, 0, 0), (x, y, bar_width, bar_height))
        
        health_ratio = self.display_health / self.max_health
        pg.draw.rect(canvas, (180, 30, 30), (x, y, bar_width * health_ratio, bar_height))

        for i in range(self.max_flasks):
            color = (200, 180, 80) if i < self.current_flasks else (80, 80, 40)
            pg.draw.rect(canvas, color, (x + i * 25, y + 30, 20, 20))
            
    def take_damage(self, amount):
        if not hasattr(self, "invuln_timer"):
            self.invuln_timer = 0

        if self.invuln_timer <= 0:
            self.current_health -= amount
            self.display_health = self.current_health
            self.hit_flash_alpha = 255
            for _ in range(10):
                self.hit_particles.append(HitParticle((self.pos[0] + 64, self.pos[1] + 64)))

            if self.current_health <= 0:
                self.current_health = 0
                self.display_health = 0
                self.dead = True
                self.death_timer = 0

            self.invuln_timer = 1.0
            print(f"Player took {amount} damage! Health: {self.current_health}")
            
    def update_invuln(self, dt):
        if hasattr(self, "invuln_timer") and self.invuln_timer > 0:
            self.invuln_timer -= dt

    def update_hit_effects(self, dt):
        if self.hit_flash_alpha > 0:
            self.hit_flash_alpha -= 600 * dt
            self.hit_flash_alpha = max(0, self.hit_flash_alpha)

        for p in self.hit_particles:
            p.update(dt)
        self.hit_particles = [p for p in self.hit_particles if p.age < p.lifetime]

    def draw_hit_effects(self, canvas):
        if self.hit_flash_alpha > 0:
            flash = pg.Surface((128, 128), pg.SRCALPHA)
            flash.fill((255, 255, 255, int(self.hit_flash_alpha)))
            #canvas.blit(flash, (self.pos[0], self.pos[1]))

        for p in self.hit_particles:
            p.draw(canvas)

    def update(self, dt, boss_projectiles):
        if not hasattr(self, "invuln_timer"):
            self.invuln_timer = 0
            
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        
        if self.invuln_timer <= 0:
            for proj in boss_projectiles[:]:
                if self.rect.colliderect(proj.rect):
                    print("PLAYER HIT!")
                    self.take_damage(20)
                    proj.alive = False
                    boss_projectiles.remove(proj)
                    break
        
        if not self.healing and abs(self.display_health - self.current_health) > 5:
            self.display_health = self.current_health
        if self.dead:
            self.death_timer += dt
            self.death_fade_alpha = min(255, int(self.death_timer * 128))

        self.update_hit_effects(dt)

class FootstepParticle:
    def __init__(self, pos):
        self.pos = pos[:]  
        self.life = 0.4  
        self.timer = self.life
        self.size = 8
        self.color = (120, 61, 34)
        self.alpha = 180  

    def update(self, dt):
        self.timer -= dt
        fade_ratio = max(self.timer / self.life, 0)
        self.alpha = int(255 * fade_ratio)
        self.size = int(8 * fade_ratio)

    def draw(self, canvas):
        if self.alpha > 0:
            surf = pg.Surface((self.size * 2, self.size * 2), pg.SRCALPHA)
            pg.draw.circle(surf, (*self.color, self.alpha), (self.size, self.size), self.size)
            canvas.blit(surf, (self.pos[0] + -20, self.pos[1] + -30))

class HitParticle:
    def __init__(self, pos):
        self.pos = pg.Vector2(pos)
        self.lifetime = 0.4
        self.age = 0

        # random circular velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 160)
        self.vel = pg.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)

        self.radius = random.randint(3, 5)
        self.color = (255, random.randint(0, 100), 0)  # reddish-orange sparks

    def update(self, dt):
        self.age += dt
        # slow down (air resistance)
        self.vel *= 0.9
        self.pos += self.vel * dt

    def draw(self, surface):
        if self.age < self.lifetime:
            fade = max(0, 255 * (1 - self.age / self.lifetime))
            color = (
                min(255, self.color[0]),
                max(0, self.color[1]),
                max(0, self.color[2]),
            )
            # Just draw the fading circle directly (no alpha surfaces)
            pg.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)
