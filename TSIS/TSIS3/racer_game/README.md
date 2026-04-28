# Speed Rush 🏎️

A top-down racing game built with Pygame satisfying all TSIS3 requirements.

## Setup

```bash
pip install pygame
python main.py
```

No external assets required – everything is drawn procedurally.

## Repository Structure

```
TSIS3/
├── main.py          # Game loop & entry point
├── racer.py         # All sprite classes (Player, Enemy, obstacles, power-ups)
├── ui.py            # All screen UIs (Menu, Settings, Game Over, Leaderboard)
├── persistence.py   # JSON save/load for leaderboard & settings
├── settings.json    # Persisted settings (sound, car colour, difficulty)
├── leaderboard.json # Top-10 scores (auto-generated on first run)
└── README.md
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys / WASD | Move car |
| ESC | Return to menu |

## Features

### 3.1 Gameplay & Race Track
- Lane hazards: oil spills slow you down, barriers/potholes require avoidance
- Dynamic road events: moving barriers, nitro boosts, coin bursts appear randomly
- 6-lane road with finish line at 5 000 m

### 3.2 Dynamic Traffic & Obstacles
- Enemy traffic cars spawn and fall down the road
- Obstacles: barriers, oil spills, potholes, speed bumps, moving barriers
- Safe spawn logic prevents spawning on the player
- Difficulty scaling: speed increases every 5 s, traffic density grows with distance

### 3.3 Power-Ups
| Power-Up | Effect | Duration |
|----------|--------|----------|
| **Nitro** | +80% speed boost | 4 seconds |
| **Shield** | Block one fatal collision | Until hit |
| **Repair** | Clears all obstacles from screen | Instant |

- Only one power-up active at a time
- Power-ups vanish after 8 s if uncollected
- Active power-up + timer shown in HUD

### 3.4 Score, Distance & Leaderboard
- Score = coins × difficulty-bonus + distance × 0.5
- Distance meter bar on the right side of screen
- Leaderboard saved to `leaderboard.json`
- Username entered before first game; persists for the session
- Top-10 screen shows rank, name, score, distance, coins

### 3.5 Game Screens
- **Main Menu** – Play, Leaderboard, Settings, Quit
- **Settings** – Toggle sound, choose car colour (4 options), choose difficulty
- **Game Over** – Score/distance/coins stats + Retry / Main Menu
- **Leaderboard** – Top-10 table with medals for top 3

Settings saved to `settings.json` and loaded at startup.
