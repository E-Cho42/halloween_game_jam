# Maskquerade — A Halloween Boss Rush

**Maskquerade** is a fast-paced 2D boss rush built with **Pygame** for the 2025 Halloween Game Jam.  
Defeat powerful foes, claim their masks, and wield their powers — but beware, each mask comes with a cost.

---

## Gameplay Overview

Long ago, the Maskquerade began — a festival of souls.  
Each fallen foe leaves behind a mask imbued with their essence.  
Wearing one grants strength… but clouds your mind.

Face three terrifying bosses:
- Pumpking — the infernal pumpkin king  
- Specter Bride — the haunting soul of sorrow  
- Scarecrow Lord — the guardian of the cursed fields  

Defeat them all to uncover the secrets of the Maskquerade.

---

## Core Features

- Three unique boss fights, each with different attacks and environments  
- Mask system — absorb powers from defeated bosses  
- Dynamic screens for story, boss selection, and victory  
- Dash, heal, and ranged combat mechanics  
- Animated fog effects for atmospheric menus  
- Hand-drawn pixel art made in GIMP  

---

## Controls

| Action | Key |
|--------|-----|
| Move | W / A / S / D |
| Dash | SPACE |
| Attack | F |
| Heal | H |
| Switch Mask | 1–3 (when unlocked) |
| Select / Continue | ENTER |
| Back / Quit | ESC |

---

## Game Flow

1. **Start Screen** — Press `ENTER` to begin  
2. **Intro Screen** — Learn about the mask system and controls  
3. **Boss Select** — Choose one of three bosses to fight  
4. **Battle Arena** — Defeat the boss using your movement, dash, and attacks  
5. **Victory Screen** — Unlock that boss’s mask  
6. Return to **Boss Select** and continue the fight  

---

## Installation

### Requirements
- Python 3.9+
- Pygame (`pip install pygame`)

### How to Run
```bash
git clone https://github.com/E-Cho42/halloween_game_jam.git
cd halloween_game_jam
python main.py
