import pygame as pg
import random
import player as p
from pumking import Pumpking
import ui
import math
from bride import SpecterBride
from ScarecrowLordStub import ScarecrowLord

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
    b = ScarecrowLord((400, 300))
    bg = pg.transform.scale(pg.image.load("Art/background3.png"), (WIDTH, HEIGHT))
    return b, bg




BOSS_FACTORIES = {
    "Pumpking": create_pumpking,
    "Specter Bride": create_specter_bride,
    "Scarecrow Lord": create_scarecrow_lord
}



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
    # Safe reset for boss
    if boss is not None:
        if hasattr(boss, "max_health"):
            boss.health = boss.max_health
        if hasattr(boss, "reset"):
            boss.reset()
        else:
            boss.alive = True
            if hasattr(boss, "projectiles"):
                boss.projectiles.clear()
            if hasattr(boss, "minions"):
                boss.minions.clear()

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
        ui.draw_start_screen(canvas, dt)
        for event in pg.event.get():
            if event.type == pg.QUIT: exit = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    GAME_STATE = "intro"
                elif event.key == pg.K_ESCAPE:
                    exit = True
        continue
    
    if GAME_STATE == "intro":
        ui.draw_intro_screen(canvas, dt)
        for event in pg.event.get():
            if event.type == pg.QUIT: exit = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    GAME_STATE = "boss_select"
                elif event.key == pg.K_ESCAPE:
                    GAME_STATE = "start"
        continue

    if GAME_STATE == "boss_select":
        ui.draw_boss_select_screen(canvas, dt, selected_boss, boss_names, defeated_bosses, mask_images)
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
        
        if boss_names == "Specter Bride":
            shake_intensity = 1
            shake_timer = 0.1
        else: 
            shake_timer = 0.4
            shake_intensity = 6
        
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

    # boss_projectiles: safe fallback if boss doesn't have projectiles
    boss_projectiles = boss.projectiles if boss and hasattr(boss, "projectiles") else []
    player.update(dt, boss_projectiles)

    # Player attack logic (player.update_attacks may expect boss or None) -- guard the call
    if boss:
        player.update_attacks(dt, boss)
    else:
        player.update_attacks(dt, None)

    # --- NEW: handle collisions between player's projectiles and boss / minions ---
    # We'll do this here so minions (boss.minions) are hittable by player.projectiles
    if boss:
        # iterate a copy because we may remove projectiles mid-loop
        for proj in list(player.projectiles):
            # skip projectiles if they don't have rect/alive
            if not hasattr(proj, "rect"):
                continue

            # hit minions first (if the boss type has minions)
            if hasattr(boss, "minions"):
                for m in list(boss.minions):
                    if not getattr(m, "alive", True):
                        continue
                    if m.rect.colliderect(proj.rect):
                        # damage the minion
                        dmg = getattr(proj, "damage", 1)
                        if hasattr(m, "health"):
                            m.health -= dmg
                        else:
                            m.alive = False
                        # destroy the projectile (if it has alive flag)
                        if hasattr(proj, "alive"):
                            proj.alive = False
                        # break so a single projectile doesn't hit multiple minions
                        break

            # hit the boss itself (if still alive)
            if getattr(boss, "alive", False) and hasattr(boss, "rect") and boss.rect.colliderect(proj.rect):
                dmg = getattr(proj, "damage", 1)
                # call take_damage if available, otherwise decrement health
                if hasattr(boss, "take_damage"):
                    boss.take_damage(dmg)
                else:
                    if hasattr(boss, "health"):
                        boss.health -= dmg
                if hasattr(proj, "alive"):
                    proj.alive = False

    # Clean up dead projectiles from player's list
    # Keep projectiles that either don't have 'alive' or are still alive
    player.projectiles[:] = [proj for proj in player.projectiles if not hasattr(proj, "alive") or proj.alive]

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
        elif boss_name == "Scarecrow Lord":
            # if you want to unlock the scarecrow mask, add here
            unlocked_masks.add("scarecrow")
            can_use_mask = True
        boss = None
        background = default_background
        GAME_STATE = "boss_cleared"  # Change to boss cleared screen
        continue

    if GAME_STATE == "boss_cleared":
        ui.draw_boss_cleared_screen(canvas, current_boss_name, dt)
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
