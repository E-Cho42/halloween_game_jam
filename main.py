import pygame as pg
import random
import player as p
from pumking import Pumpking
import ui
import math
from bride import SpecterBride

pg.init()
clock = pg.time.Clock()

# === CONSTANTS ===
WIDTH, HEIGHT = 800, 800
GAME_STATE = "start"  # "start", "boss_select", "playing", "boss_cleared"
exit = False

# === SETUP ===
canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Maskquerade")

# === BACKGROUND SETUP ===
default_background = pg.transform.scale(pg.image.load("Art/background.png").convert(), (WIDTH, HEIGHT))
background = default_background

# === PLAYER ASSETS ===
player_left = pg.transform.scale(pg.image.load("Art/player_fliped.png"), (128, 128))
player_right = pg.transform.scale(pg.image.load("Art/player.png"), (128, 128))
player_left_masked = pg.transform.scale(pg.image.load("Art/player_masked_fliped.png"), (128, 128))
player_right_masked = pg.transform.scale(pg.image.load("Art/player_masked.png"), (128, 128))

# === MASK IMAGES (scaled for menu) ===
_mask_size = (80, 80)
_mask_spacing = 24

mask_images = {
    "Pumpking": pg.image.load("Art/mask_pumpking.png").convert_alpha(),
    "Specter Bride": pg.image.load("Art/mask_specter.png").convert_alpha(),
    "Scarecrow Lord": pg.image.load("Art/mask_scarecrow.png").convert_alpha()
}

for key in mask_images:
    mask_images[key] = pg.transform.smoothscale(mask_images[key], _mask_size)

# === PLAYER OBJECT ===
player = p.player([400, 400], False, False, player_left, player_right, 5, player_left_masked, player_right_masked)

boss = None

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
        if self.x < -self.radius: self.x = WIDTH + self.radius
        if self.x > WIDTH + self.radius: self.x = -self.radius
        if self.y < -self.radius: self.y = HEIGHT + self.radius
        if self.y > HEIGHT + self.radius: self.y = -self.radius

    def draw(self, surface):
        surface.blit(self.surface, (self.x - self.radius, self.y - self.radius))

fog_particles = [FogParticle() for _ in range(15)]

# -------------------------------------------------------------------
# === BOSS FACTORIES & STUBS ===
# -------------------------------------------------------------------

def create_pumpking():
    b = Pumpking((400, 300))
    b.name = "Pumpking"
    bg = pg.transform.scale(pg.image.load("Art/background.png"), (WIDTH, HEIGHT))
    return b, bg

def create_specter_bride():
    b = SpecterBride((400, 300))
    background = pg.transform.scale(pg.image.load("Art/background2.png"), (WIDTH, HEIGHT))
    return b, background

def create_scarecrow_lord():
    b = ScarecrowLordStub((400, 300))
    bg = pg.transform.scale(pg.image.load("Art/background2.png"), (WIDTH, HEIGHT))
    return b, bg



class ScarecrowLordStub:
    def __init__(self, pos=(400, 300)):
        self.name = "Scarecrow Lord"
        self.pos = pg.Vector2(pos)
        self.max_health = 150
        self.health = self.max_health
        self.alive = True
        self.projectiles = []
        self.just_attacked = False
        
        # Add rect attribute for collision detection
        self.rect = pg.Rect(0, 0, 64, 96)
        self.rect.center = self.pos

    def update(self, dt, player):
        # Update rect position
        self.rect.center = self.pos

    def draw(self, surface):
        rect = pg.Rect(0, 0, 64, 96)
        surf = pg.Surface(rect.size, pg.SRCALPHA)
        pg.draw.rect(surf, (160, 120, 40), rect)
        surface.blit(surf, (self.pos.x - rect.width//2, self.pos.y - rect.height//2))

BOSS_FACTORIES = {
    "Pumpking": create_pumpking,
    "Specter Bride": create_specter_bride,
    "Scarecrow Lord": create_scarecrow_lord
}

# -------------------------------------------------------------------
# === UI: Screens ===
# -------------------------------------------------------------------

def draw_start_screen(canvas, dt):
    canvas.fill((5, 5, 5))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)

    darken = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    darken.fill((0, 0, 0, 150))
    canvas.blit(darken, (0, 0))

    font_title = pg.font.Font(None, 120)
    font_subtitle = pg.font.Font(None, 60)
    font_info = pg.font.Font(None, 40)
    font_controls = pg.font.Font(None, 36)

    title_text = font_title.render("MASKQUERADE", True, (230, 210, 150))
    subtitle_text = font_subtitle.render("— The Boss Rush —", True, (160, 140, 90))
    canvas.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 200)))
    canvas.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, 270)))

    flicker = (pg.time.get_ticks() // 300) % 2
    if flicker:
        start_text = font_info.render("Press ENTER to Begin", True, (240, 220, 150))
    else:
        start_text = font_info.render("Press ENTER to Begin", True, (200, 200, 200))
    canvas.blit(start_text, start_text.get_rect(center=(WIDTH // 2, 430)))

    quit_text = font_info.render("Press ESC to Quit", True, (120, 120, 120))
    canvas.blit(quit_text, quit_text.get_rect(center=(WIDTH // 2, 480)))

    pg.display.flip()

def draw_boss_select_screen(canvas, dt, selected_index, boss_names, defeated_bosses, mask_images):
    canvas.fill((10, 10, 10))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)
    darken = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    darken.fill((0, 0, 0, 160))
    canvas.blit(darken, (0, 0))

    font_title = pg.font.Font(None, 100)
    font_option = pg.font.Font(None, 60)
    font_info = pg.font.Font(None, 40)
    font_masks = pg.font.Font(None, 50)

    title_text = font_title.render("Choose Your Foe", True, (230, 210, 150))
    canvas.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 120)))

    y = 260
    for i, name in enumerate(boss_names):
        if name in defeated_bosses:
            color = (120, 120, 120)
        elif i == selected_index:
            color = (240, 200, 120)
        else:
            color = (180, 180, 180)

        text = font_option.render(name, True, color)
        rect = text.get_rect(center=(WIDTH // 2, y))
        canvas.blit(text, rect)

        if name in defeated_bosses:
            pg.draw.line(canvas, (200, 50, 50),
                         (rect.left - 10, rect.centery),
                         (rect.right + 10, rect.centery), 5)
        y += 80

    # Mask section
    mask_title = font_masks.render("Your Masks", True, (220, 210, 160))
    canvas.blit(mask_title, mask_title.get_rect(center=(WIDTH // 2, 520)))

    mask_w, mask_h = _mask_size
    total_width = len(boss_names) * mask_w + (len(boss_names) - 1) * _mask_spacing
    start_x = (WIDTH - total_width) // 2
    y_mask = 580

    for name in boss_names:
        mask = mask_images[name]
        pos = (start_x, y_mask)
        if name in defeated_bosses:
            canvas.blit(mask, pos)
        else:
            faded = mask.copy()
            faded.fill((80, 80, 80, 180), None, pg.BLEND_RGBA_MULT)
            canvas.blit(faded, pos)
            lock_font = pg.font.Font(None, 22)
            lock = lock_font.render("🔒", True, (200, 80, 80))
            canvas.blit(lock, (start_x + mask_w//2 - lock.get_width()//2, y_mask + mask_h//2 - lock.get_height()//2))
        start_x += mask_w + _mask_spacing

    info_text = font_info.render("w / s to Select  |  ENTER to Begin  |  ESC to Back", True, (200, 200, 200))
    canvas.blit(info_text, info_text.get_rect(center=(WIDTH // 2, 740)))

    pg.display.flip()

def draw_boss_cleared_screen(canvas, boss_name, dt):
    canvas.fill((5, 5, 5))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)

    darken = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    darken.fill((0, 0, 0, 180))
    canvas.blit(darken, (0, 0))

    font_title = pg.font.Font(None, 120)
    font_boss = pg.font.Font(None, 80)
    font_info = pg.font.Font(None, 40)

    # Flickering "BOSS CLEARED" text
    flicker = (pg.time.get_ticks() // 200) % 2
    if flicker:
        title_text = font_title.render("BOSS CLEARED", True, (255, 215, 0))
    else:
        title_text = font_title.render("BOSS CLEARED", True, (200, 170, 50))
    
    canvas.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 250)))

    # Boss name
    boss_text = font_boss.render(boss_name, True, (220, 180, 80))
    canvas.blit(boss_text, boss_text.get_rect(center=(WIDTH // 2, 350)))

    # Victory message
    victory_text = font_info.render("Victory Achieved", True, (180, 180, 180))
    canvas.blit(victory_text, victory_text.get_rect(center=(WIDTH // 2, 420)))

    # Continue prompt
    continue_flicker = (pg.time.get_ticks() // 500) % 2
    if continue_flicker:
        continue_text = font_info.render("Press ENTER to continue", True, (200, 200, 100))
    else:
        continue_text = font_info.render("Press ENTER to continue", True, (150, 150, 100))
    canvas.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, 500)))

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

# === GAME VARIABLES ===
boss_names = ["Pumpking", "Specter Bride", "Scarecrow Lord"]
selected_boss = 0
defeated_bosses = set()
can_use_mask = False
unlocked_masks = set()  # Track which masks are unlocked
current_boss_name = ""

# === MAIN LOOP ===
while not exit:
    dt = clock.tick(60) / 1000

    if GAME_STATE == "start":
        draw_start_screen(canvas, dt)
        for event in pg.event.get():
            if event.type == pg.QUIT: exit = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN: GAME_STATE = "boss_select"
                elif event.key == pg.K_ESCAPE: exit = True
        continue

    if GAME_STATE == "boss_select":
        draw_boss_select_screen(canvas, dt, selected_boss, boss_names, defeated_bosses, mask_images)
        for event in pg.event.get():
            if event.type == pg.QUIT: exit = True
            elif event.type == pg.KEYDOWN:
                if event.key in [pg.K_UP, pg.K_w]:
                    selected_boss = (selected_boss - 1) % len(boss_names)
                elif event.key in [pg.K_DOWN, pg.K_s]:
                    selected_boss = (selected_boss + 1) % len(boss_names)
                elif event.key == pg.K_RETURN:
                    chosen_boss = boss_names[selected_boss]
                    if chosen_boss in defeated_bosses: continue
                    factory = BOSS_FACTORIES.get(chosen_boss)
                    if factory:
                        boss, background = factory()
                        if not hasattr(boss, "name"): boss.name = chosen_boss
                        current_boss_name = chosen_boss  # Store current boss name
                        restart_game(player, boss)
                        GAME_STATE = "playing"
                elif event.key == pg.K_ESCAPE:
                    GAME_STATE = "start"
        continue

    # === PLAYING ===
    if boss and getattr(boss, "just_attacked", False):
        shake_timer = 0.4
        shake_intensity = 10
        boss.just_attacked = False

    if shake_timer > 0:
        shake_timer -= dt
        offset_x, offset_y = random.uniform(-shake_intensity, shake_intensity), random.uniform(-shake_intensity, shake_intensity)
    else:
        offset_x = offset_y = 0

    canvas.blit(background, (offset_x, offset_y))

    for event in pg.event.get():
        if event.type == pg.QUIT: exit = True
        player.player_mask_check(event, can_use_mask, unlocked_masks)  # Pass unlocked_masks here
        player.player_dash(event)
        player.player_attack(event, boss)
        player.player_heal(event)

    player.update_dash(dt)
    player.player_move()
    boss_projectiles = boss.projectiles if boss and hasattr(boss, "projectiles") else []
    player.update(dt, boss_projectiles)
    player.update_attacks(dt, boss)
    player.update_footsteps(dt)
    player.update_heal(dt)

    player.draw_footsteps(canvas)
    player.draw(canvas)
    player.draw_dash_indicator(canvas, dt)
    player.draw_health_bar(canvas)

    if boss and getattr(boss, "alive", False):
        boss.update(dt, player)
        boss.draw(canvas)
    elif boss:
        defeated_bosses.add(getattr(boss, "name", boss.__class__.__name__))
        # Enable masks based on which boss is defeated
        boss_name = getattr(boss, "name", boss.__class__.__name__)
        if boss_name == "Pumpking":
            can_use_mask = True
            unlocked_masks.add("pumpkin")
        elif boss_name == "Specter Bride":
            unlocked_masks.add("specter")
        boss = None
        background = default_background
        GAME_STATE = "boss_cleared"  # Change to boss cleared screen
        continue

    if GAME_STATE == "boss_cleared":
        draw_boss_cleared_screen(canvas, current_boss_name, dt)
        for event in pg.event.get():
            if event.type == pg.QUIT: exit = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    GAME_STATE = "boss_select"
        continue

    if player.dead:
        ui.you_died_screen(canvas, player.death_fade_alpha)
        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            if boss: restart_game(player, boss)
        elif keys[pg.K_ESCAPE]:
            background = default_background
            GAME_STATE = "boss_select"

    pg.display.flip()

pg.quit()