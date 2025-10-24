import pygame as pg
import random
import math

_mask_size = (80, 80)
_mask_spacing = 24

class FogParticle:
    def __init__(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(0, 800)
        self.radius = random.randint(80, 160)
        self.speed = random.uniform(5, 20)
        self.alpha = random.randint(30, 80)
        self.surface = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
        pg.draw.circle(self.surface, (200, 200, 200, self.alpha), (self.radius, self.radius), self.radius)

    def update(self, dt):
        self.x += math.sin(pg.time.get_ticks() * 0.0002) * self.speed * dt
        self.y += math.cos(pg.time.get_ticks() * 0.0002) * self.speed * dt
        if self.x < -self.radius: self.x = 800 + self.radius
        if self.x > 800 + self.radius: self.x = -self.radius
        if self.y < -self.radius: self.y = 800 + self.radius
        if self.y > 800 + self.radius: self.y = -self.radius

    def draw(self, surface):
        surface.blit(self.surface, (self.x - self.radius, self.y - self.radius))

fog_particles = [FogParticle() for _ in range(15)]


def you_died_screen(canvas, alpha):
    """Draws a fading 'YOU DIED' message centered on screen."""
    font = pg.font.Font(None, 150)  # You can replace with custom .ttf for a cooler look
    text = font.render("YOU DIED", True, (180, 0, 0))
    text.set_alpha(alpha)
    text_rect = text.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))

    # Draw a black overlay behind it
    overlay = pg.Surface(canvas.get_size())
    overlay.fill((0, 0, 0))
    overlay.set_alpha(min(200, alpha))  # darken background
    canvas.blit(overlay, (0, 0))
    canvas.blit(text, text_rect)

# -------------------------------------------------------------------
# === UI: Screens ===
# -------------------------------------------------------------------
# === INTRO SCREEN ===
def draw_intro_screen(canvas, dt):
    canvas.fill((10, 10, 10))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)

    overlay = pg.Surface((800, 800), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    canvas.blit(overlay, (0, 0))

    font_title = pg.font.Font(None, 80)
    font_story = pg.font.Font(None, 36)
    font_controls = pg.font.Font(None, 34)
    font_continue = pg.font.Font(None, 40)

    # Title
    title = font_title.render("The Mask System", True, (240, 220, 180))
    canvas.blit(title, title.get_rect(center=(800 // 2, 120)))

    # Story text
    story_lines = [
        "Long ago, the Maskquerade began — a festival of souls.",
        "Each mask holds the power of a fallen foe.",
        "Wearing one grants strength... but clouds your mind.",
        "",
        "Defeat bosses to unlock their masks, then toggle them in battle!"
    ]
    y = 200
    for line in story_lines:
        text = font_story.render(line, True, (210, 200, 190))
        canvas.blit(text, text.get_rect(center=(800 // 2, y)))
        y += 40

    # Controls section
    control_title = font_title.render("Controls", True, (240, 220, 180))
    canvas.blit(control_title, control_title.get_rect(center=(800 // 2, 460)))

    controls = [
        "W / A / S / D — Move",
        "SPACE — Dash",
        "F — Attack",
        "H — Heal",
        "1-2-3 — Toggle Mask (when unlocked)",
    ]
    y = 520
    for line in controls:
        text = font_controls.render(line, True, (200, 200, 200))
        canvas.blit(text, text.get_rect(center=(800 // 2, y)))
        y += 35

    # Continue prompt (flickering)
    flicker = (pg.time.get_ticks() // 400) % 2
    if flicker:
        continue_text = font_continue.render("Press ENTER to Continue", True, (240, 220, 140))
    else:
        continue_text = font_continue.render("Press ENTER to Continue", True, (180, 180, 120))
    canvas.blit(continue_text, continue_text.get_rect(center=(800 // 2, 740)))

    pg.display.flip()


def draw_start_screen(canvas, dt):
    canvas.fill((5, 5, 5))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)

    darken = pg.Surface((800, 800), pg.SRCALPHA)
    darken.fill((0, 0, 0, 150))
    canvas.blit(darken, (0, 0))

    font_title = pg.font.Font(None, 120)
    font_subtitle = pg.font.Font(None, 60)
    font_info = pg.font.Font(None, 40)
    font_controls = pg.font.Font(None, 36)

    title_text = font_title.render("MASKQUERADE", True, (230, 210, 150))
    subtitle_text = font_subtitle.render("— The Boss Rush —", True, (160, 140, 90))
    canvas.blit(title_text, title_text.get_rect(center=(800 // 2, 200)))
    canvas.blit(subtitle_text, subtitle_text.get_rect(center=(800 // 2, 270)))

    flicker = (pg.time.get_ticks() // 300) % 2
    if flicker:
        start_text = font_info.render("Press ENTER to Begin", True, (240, 220, 150))
    else:
        start_text = font_info.render("Press ENTER to Begin", True, (200, 200, 200))
    canvas.blit(start_text, start_text.get_rect(center=(800 // 2, 430)))

    quit_text = font_info.render("Press ESC to Quit", True, (120, 120, 120))
    canvas.blit(quit_text, quit_text.get_rect(center=(800 // 2, 480)))

    pg.display.flip()

def draw_boss_select_screen(canvas, dt, selected_index, boss_names, defeated_bosses, mask_images):
    canvas.fill((10, 10, 10))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)
    darken = pg.Surface((800, 800), pg.SRCALPHA)
    darken.fill((0, 0, 0, 160))
    canvas.blit(darken, (0, 0))

    font_title = pg.font.Font(None, 100)
    font_option = pg.font.Font(None, 60)
    font_info = pg.font.Font(None, 40)
    font_masks = pg.font.Font(None, 50)

    title_text = font_title.render("Choose Your Foe", True, (230, 210, 150))
    canvas.blit(title_text, title_text.get_rect(center=(800 // 2, 120)))

    y = 260
    for i, name in enumerate(boss_names):
        if name in defeated_bosses:
            color = (120, 120, 120)
        elif i == selected_index:
            color = (240, 200, 120)
        else:
            color = (180, 180, 180)

        text = font_option.render(name, True, color)
        rect = text.get_rect(center=(800 // 2, y))
        canvas.blit(text, rect)

        if name in defeated_bosses:
            pg.draw.line(canvas, (200, 50, 50),
                         (rect.left - 10, rect.centery),
                         (rect.right + 10, rect.centery), 5)
        y += 80

    # Mask section
    mask_title = font_masks.render("Your Masks", True, (220, 210, 160))
    canvas.blit(mask_title, mask_title.get_rect(center=(800 // 2, 520)))

    mask_w, mask_h = _mask_size
    total_width = len(boss_names) * mask_w + (len(boss_names) - 1) * _mask_spacing
    start_x = (800 - total_width) // 2
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
    canvas.blit(info_text, info_text.get_rect(center=(800 // 2, 740)))

    pg.display.flip()

def draw_boss_cleared_screen(canvas, boss_name, dt):
    canvas.fill((5, 5, 5))
    for fog in fog_particles:
        fog.update(dt)
        fog.draw(canvas)

    darken = pg.Surface((800, 800), pg.SRCALPHA)
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
    
    canvas.blit(title_text, title_text.get_rect(center=(800 // 2, 250)))

    # Boss name
    boss_text = font_boss.render(boss_name, True, (220, 180, 80))
    canvas.blit(boss_text, boss_text.get_rect(center=(800 // 2, 350)))

    # Victory message
    victory_text = font_info.render("Victory Achieved", True, (180, 180, 180))
    canvas.blit(victory_text, victory_text.get_rect(center=(800 // 2, 420)))

    # Continue prompt
    continue_flicker = (pg.time.get_ticks() // 500) % 2
    if continue_flicker:
        continue_text = font_info.render("", True, (200, 200, 100))
    else:
        continue_text = font_info.render("", True, (150, 150, 100))
    canvas.blit(continue_text, continue_text.get_rect(center=(800 // 2, 500)))

    pg.display.flip()