# Space Shooter Game 🚀

A classic vertical scrolling space shooter with modern features built with Python and Pygame!

## ✨ Features

### **Polished UI System**
- **Main Menu** - Beautifully designed start screen with custom fonts
- **Character Selection** - Choose from 3 unique spaceships
- **Settings Menu** - Adjustable sound/music volumes and fullscreen toggle
- **Clickable Buttons** - Professional UI with hover effects
- **Quit Confirmation** - Prevents accidental exits

### **Gameplay**
- **Classic Arcade Action** - Shoot enemies, dodge attacks, survive
- **Score System** - Earn 10 points per enemy destroyed
- **Progressive Difficulty** - Game gets harder as you play
- **Pause System** - Press ESC to pause, resume or quit to menu
- **Sound Effects** - Laser shots, explosions, and background music
- **Game Over Screen** - Clickable restart and menu options

### **Character Selection**
- Choose from 3 different spaceships (player1, player2, player3)
- Visual previews with SELECT buttons
- All ships auto-scaled to perfect size

### **Settings**
- **SFX Volume Slider** - Adjust sound effects (0-100%)
- **Music Volume Slider** - Control background music (0-100%)
- **Fullscreen Mode** - Toggle fullscreen with checkbox

## 🎮 Controls

### **Menus:**
- **Mouse** - Click buttons to navigate
- **Mouse Drag** - Adjust volume sliders in settings

### **Gameplay:**
- **← →** Arrow Keys - Move your ship left/right
- **SPACE** - Shoot lasers
- **ESC** - Return to main menu

### **Game Over:**
- **Click RESTART** - Play again with same ship
- **Click MAIN MENU** - Return to menu

## 🎨 Custom Fonts

The game uses custom retro fonts for an authentic arcade feel:
- **RETRO_SPACE** - All UI text, scores, and menus
- **Oleaguid** - Game Over title screen

## 📦 Installation

1. Make sure you have Python 3.7+ installed
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

**Note:** If `pip` is not recognized, use:
```bash
python -m pip install -r requirements.txt
```

3. Download game assets (see Assets section below)
4. Run the game:

```bash
python space_shooter.py
```

## 📁 Assets Required

The game will run without assets (using colored shapes), but for the full experience, organize assets into subfolders:

### **Assets/Images/ folder:**
- `player.png` - Spaceship 1 (auto-scaled)
- `player2.PNG` - Spaceship 2 (auto-scaled)
- `player3.png` - Spaceship 3 (auto-scaled)
- `enemy.png` - Enemy spaceship (auto-scaled)
- `bullet.png` - Laser projectile (auto-scaled)
- `background.avif` (or .png/.jpg) - Space background

### **Assets/Audio/ folder:**
- `laser.wav` - Shooting sound
- `explosion.wav` - Enemy destruction sound
- `game_over.mp3` - Game over sound
- `background_music.mp3` (or .ogg/.wav) - Background music

### **Assets/Fonts/ folder:**
- `RETRO_SPACE.ttf` - Main UI font
- `Oleaguid.ttf` - Game Over font

**Note:** All images are automatically scaled - any resolution works!

### **Recommended Asset Sources:**
- **Kenney.nl** - Space Shooter Redux pack (highly recommended!)
- **OpenGameArt.org** - Free game sprites
- **Itch.io** - Game asset bundles
- **Freesound.org** - Sound effects
- **DaFont.com** - Free fonts

## 🎯 Game Mechanics

### **Main Menu Flow:**
1. **START** → Character Selection → Choose Ship → Play
2. **SETTINGS** → Adjust volumes, toggle fullscreen → Back
3. **QUIT** → Confirm → Exit game

### **Core Gameplay Loop:**
1. **Player Movement** - Smooth left/right controls with boundary limits
2. **Shooting** - Fire lasers upward at enemies
3. **Enemies** - Spawn randomly at top, move downward
4. **Collision Detection**:
   - Bullet hits enemy → Both removed, +10 score, explosion sound
   - Enemy hits player → Game Over

### **Game Over:**
- Display final score with Oleaguid font
- Click **RESTART** to play again with same ship
- Click **MENU** to return and choose different ship

### **Pause System:**
- Press **ESC** during gameplay to pause
- Game freezes with "PAUSED" overlay
- Click **RESUME** to continue where you left off
- Click **QUIT TO MENU** to return to main menu

### **Difficulty Scaling:**
Enemies gradually speed up as your score increases!

## 🎨 UI Design Features

- **Semi-transparent overlays** for better menu visibility
- **Hover effects** on all buttons
- **Color-coded buttons**:
  - Blue for navigation
  - Green for confirmations
  - Red for warnings/quit
- **Custom retro fonts** for authentic arcade feel
- **Visual feedback** for selected character
- **Interactive sliders** with real-time volume adjustment

## ⚙️ Technical Features

- **State Management** - Clean separation of menu/gameplay states
- **OOP Design** - Classes for Player, Bullet, Enemy, Button, Slider, Checkbox
- **AVIF Support** - Loads modern image formats via Pillow
- **Flexible Assets** - Auto-scales any image size
- **Volume Control** - Independent SFX and music volumes
- **Fullscreen Mode** - Toggle between windowed and fullscreen

## 🔧 Code Structure

```
Classes:
├── Button       - Clickable UI buttons with hover effects
├── Slider       - Volume sliders for settings
├── Checkbox     - Fullscreen toggle
├── Player       - Player spaceship with movement
├── Bullet       - Laser projectiles
├── Enemy        - Enemy spaceships
└── Game         - Main game controller

States:
├── MAIN_MENU         - Start screen
├── CHARACTER_SELECT  - Choose your ship
├── SETTINGS          - Adjust audio/display
├── PLAYING           - Actual gameplay
│   └── PAUSED        - Pause overlay (ESC to toggle)
├── GAME_OVER         - End screen
└── QUIT_CONFIRM      - Exit confirmation
```

## Troubleshooting

**Game runs but I see rectangles instead of sprites:**
- Make sure assets are in the `Assets` folder with correct names
- Check the console for "Warning" messages about missing files

**No sound:**
- Ensure sound files are in `.wav` format (MP3 for music)
- Check your system volume

**Game runs too fast/slow:**
- Adjust the `FPS` constant in line 19 of `space_shooter.py`

## License

This is a learning project. Feel free to modify and expand upon it!

## Future Enhancement Ideas

- Power-ups (rapid fire, shield, etc.)
- Multiple enemy types
- Boss battles
- High score persistence
- Particle effects
- Multiple lives system

Happy shooting! 🎮
