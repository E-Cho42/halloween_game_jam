import pygame as pg

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
