import pygame as pg
import random
import player as p
from pumking import Pumpking
import ui
import math

pg.init()
clock = pg.time.Clock()

# === CONSTANTS ===
WIDTH, HEIGHT = 800, 800
GAME_STATE = "start"
exit = False

# === SETUP ===
canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Maskquerade")

background = pg.image.load("Art/background.png").convert()
background = pg.transform.scale(background, (WIDTH, HEIGHT))

# === PLAYER ASSETS ===
player_left = pg.transform.scale(pg.image.load('Art/player_fliped.png'), (128, 128))
player_right = pg.transform.scale(pg.image.load('Art/player.png'), (128, 128))
player_left_masked = pg.transform.scale(pg.image.load('Art/player_masked_fliped.png'), (128, 128))
player_right_masked = pg.transform.scale(pg.image.load('Art/player_masked.png'), (128, 128))

player = p.player([400, 400], False, False, player_left, player_right, 5, player_left_masked, player_right_masked)
boss = Pumpking((400, 300))

# === CAMERA SHAKE ===
shake_timer = 0
shake_intensity = 0

# === FOG SYSTEM ===
class FogParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(80, 160)
        self.speed = random.uniform(5, 20)
        self.alpha = random.randint(30, 80)
        self.surface = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
        pg.draw.circle(self.surface, (200, 200, 200, self.alpha), (self.radius, self.radius), self.radius)

    def update(self, dt):
        self.x += math.sin(pg.time.get_ticks() * 0.0002) * self.speed * dt
        self.y += math.cos(pg.time.get_ticks() * 0.0002) * self.speed * dt
        if self.x < -self.radius:
            self.x = WIDTH + self.radius
        if self.x > WIDTH + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = HEIGHT + self.radius
        if self.y > HEIGHT + self.radius:
            self.y = -self.radius

    def draw(self, surface):
        surface.blit(self.surface, (self.x - self.radius, self.y - self.radius))


fog_particles = [FogParticle() for _ in range(15)]

# === START SCREEN ===
def draw_start_screen(canvas, dt):
    canvas.fill((0, 0, 0))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)

    darken = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    darken.fill((0, 0, 0, 100))
    canvas.blit(darken, (0, 0))

    font_title = pg.font.Font(None, 100)
    font_subtitle = pg.font.Font(None, 60)
    font_sub = pg.font.Font(None, 50)
    font_controls = pg.font.Font(None, 36)

    title_text = font_title.render("MASKQUERADE", True, (200, 0, 0))
    subtitle_text = font_subtitle.render("(Boss Rush)", True, (230, 230, 230))
    start_text = font_sub.render("Press ENTER to Start", True, (255, 255, 255))
    quit_text = font_sub.render("Press ESC to Quit", True, (180, 180, 180))

    controls_text = [
        font_controls.render("WASD - Move", True, (230, 230, 230)),
        font_controls.render("SPACE - Dash", True, (230, 230, 230)),
        font_controls.render("F - Attack", True, (230, 230, 230)),
        font_controls.render("H - Heal", True, (230, 230, 230))
    ]

    canvas.blit(title_text, title_text.get_rect(center=(400, 200)))
    canvas.blit(subtitle_text, subtitle_text.get_rect(center=(400, 270)))
    canvas.blit(start_text, start_text.get_rect(center=(400, 400)))
    canvas.blit(quit_text, quit_text.get_rect(center=(400, 460)))

    y_offset = 550
    for t in controls_text:
        rect = t.get_rect(center=(400, y_offset))
        canvas.blit(t, rect)
        y_offset += 40

    pg.display.flip()

# === RESTART ===
def restart_game(player, boss):
    player.pos = [400, 400]
    player.rect.topleft = player.pos
    player.current_health = player.max_health
    player.display_health = player.max_health
    player.current_flasks = player.max_flasks
    player.dead = False
    player.death_timer = 0
    player.death_fade_alpha = 0
    player.projectiles.clear()
    player.foot_particles.clear()
    player.invuln_timer = 0
    player.healing = False
    player.dashing = False

    boss.health = boss.max_health
    if hasattr(boss, "reset"):
        boss.reset()
    else:
        boss.health = boss.max_health
        boss.alive = True
        if hasattr(boss, "projectiles"):
            boss.projectiles.clear()


# === MAIN LOOP ===
while not exit:
    dt = clock.tick(60) / 1000

    # --- Start Screen ---
    if GAME_STATE == "start":
        draw_start_screen(canvas, dt)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    GAME_STATE = "playing"
                elif event.key == pg.K_ESCAPE:
                    exit = True
        continue

    # --- Camera Shake (only after boss attacks) ---
    if getattr(boss, "just_attacked", False):
        shake_timer = 0.4
        shake_intensity = 10
        boss.just_attacked = False

    if shake_timer > 0:
        shake_timer -= dt
        offset_x = random.uniform(-shake_intensity, shake_intensity)
        offset_y = random.uniform(-shake_intensity, shake_intensity)
    else:
        offset_x, offset_y = 0, 0

    canvas.blit(background, (offset_x, offset_y))

    # --- Input Handling ---
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit = True
        player.player_mask_check(event)
        player.player_dash(event)
        player.player_attack(event)
        player.player_heal(event)

    # --- Player Updates ---
    player.update_dash(dt)
    player.player_move()
    player.update(dt, boss.projectiles)
    player.update_attacks(dt, boss)
    player.update_footsteps(dt)
    player.update_heal(dt)

    # --- Drawing ---
    player.draw_footsteps(canvas)
    player.draw(canvas)
    player.draw_dash_indicator(canvas, dt)
    player.draw_health_bar(canvas)

    # --- Boss Logic ---
    if boss.alive:
        boss.update(dt, player)
        boss.draw(canvas)
    else:
        player.masked = True
        player.current_mask = "fire"

    # --- Death Screen ---
    if player.dead:
        ui.you_died_screen(canvas, player.death_fade_alpha)
        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            restart_game(player, boss)
        elif keys[pg.K_ESCAPE]:
            GAME_STATE = "start"

    pg.display.flip()

pg.quit()
