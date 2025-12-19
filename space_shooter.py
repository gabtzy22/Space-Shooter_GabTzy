"""
Space Shooter Game - Enhanced Edition
A classic vertical scrolling shooter with menus and character selection

Controls:
- Mouse: Navigate menus and click buttons
- Left/Right Arrow Keys: Move ship
- Space: Shoot laser
- ESC: Pause/Return to menu
"""

import pygame
import random
import os
import sys
import json
from PIL import Image

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 50, 150)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# Asset path helpers
def get_image_path(filename):
    """Helper function to get image asset path"""
    return os.path.join("Assets", "Images", filename)

def get_audio_path(filename):
    """Helper function to get audio asset path"""
    return os.path.join("Assets", "Audio", filename)

def get_font_path(filename):
    """Helper function to get font asset path"""
    return os.path.join("Assets", "Fonts", filename)


class Button:
    """Clickable button class for UI elements"""
    
    def __init__(self, x, y, width, height, text, font, color=BLUE, hover_color=LIGHT_GRAY, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, screen):
        """Draw button with hover effect"""
        current_color = self.hover_color if self.is_hovered else self.color
        # Draw button background with border
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=10)
        
        # Draw text centered
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over button"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        """Check if button is clicked"""
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]


class Slider:
    """Volume slider for settings"""
    
    def __init__(self, x, y, width, height, min_val=0, max_val=100, initial_val=50, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.was_dragging = False
        self.handle_radius = 12
    
    def draw(self, screen, font):
        """Draw slider with label and value"""
        # Draw label
        label_surface = font.render(f"{self.label}: {int(self.value)}%", True, WHITE)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))
        
        # Draw slider track
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=5)
        
        # Calculate handle position
        handle_x = self.rect.x + (self.value / self.max_val) * self.rect.width
        handle_pos = (int(handle_x), self.rect.centery)
        
        # Draw handle
        pygame.draw.circle(screen, WHITE, handle_pos, self.handle_radius)
        pygame.draw.circle(screen, BLUE, handle_pos, self.handle_radius - 3)
    
    def handle_event(self, event, mouse_pos):
        """Handle mouse events for slider, returns True when released after dragging"""
        handle_x = self.rect.x + (self.value / self.max_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - self.handle_radius, self.rect.centery - self.handle_radius,
                                   self.handle_radius * 2, self.handle_radius * 2)
        
        released = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.was_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.was_dragging:
                released = True
                self.was_dragging = False
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            relative_x = mouse_pos[0] - self.rect.x
            self.value = max(self.min_val, min(self.max_val, (relative_x / self.rect.width) * self.max_val))
        
        return released
    
    def get_value(self):
        """Get current value as 0-1 range"""
        return self.value / 100.0


class Checkbox:
    """Checkbox for settings"""
    
    def __init__(self, x, y, size, label, checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.checked = checked
    
    def draw(self, screen, font):
        """Draw checkbox with label"""
        # Draw checkbox
        pygame.draw.rect(screen, WHITE, self.rect, 3)
        if self.checked:
            # Draw checkmark
            pygame.draw.line(screen, GREEN, (self.rect.x + 5, self.rect.centery),
                           (self.rect.centerx, self.rect.bottom - 5), 3)
            pygame.draw.line(screen, GREEN, (self.rect.centerx, self.rect.bottom - 5),
                           (self.rect.right - 5, self.rect.top + 5), 3)
        
        # Draw label
        label_surface = font.render(self.label, True, WHITE)
        screen.blit(label_surface, (self.rect.right + 15, self.rect.y))
    
    def handle_click(self, mouse_pos):
        """Toggle checkbox if clicked"""
        if self.rect.collidepoint(mouse_pos):
            self.checked = not self.checked
            return True
        return False


class Dropdown:
    """Dropdown menu for selecting options"""
    
    def __init__(self, x, y, width, height, options, label="", initial_index=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.label = label
        self.selected_index = initial_index
        self.is_open = False
        self.option_rects = []
    
    def draw(self, screen, font):
        """Draw dropdown with label"""
        # Draw label
        if self.label:
            label_surface = font.render(self.label, True, WHITE)
            screen.blit(label_surface, (self.rect.x, self.rect.y - 30))
        
        # Draw main box
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw selected option
        text_surface = font.render(self.options[self.selected_index], True, WHITE)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 5))
        
        # Draw arrow
        arrow_x = self.rect.right - 25
        arrow_y = self.rect.centery
        if self.is_open:
            # Up arrow
            pygame.draw.polygon(screen, WHITE, [
                (arrow_x, arrow_y + 5),
                (arrow_x - 5, arrow_y - 5),
                (arrow_x + 5, arrow_y - 5)
            ])
        else:
            # Down arrow
            pygame.draw.polygon(screen, WHITE, [
                (arrow_x, arrow_y + 5),
                (arrow_x - 5, arrow_y - 5),
                (arrow_x + 5, arrow_y - 5)
            ])
        
        # Draw options if open
        if self.is_open:
            self.option_rects = []
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height * (i + 1),
                                         self.rect.width, self.rect.height)
                self.option_rects.append(option_rect)
                
                # Highlight on hover
                mouse_pos = pygame.mouse.get_pos()
                if option_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, BLUE, option_rect)
                else:
                    pygame.draw.rect(screen, GRAY, option_rect)
                
                pygame.draw.rect(screen, WHITE, option_rect, 2)
                option_surface = font.render(option, True, WHITE)
                screen.blit(option_surface, (option_rect.x + 10, option_rect.y + 5))
    
    def handle_click(self, mouse_pos):
        """Handle dropdown clicks, returns True if selection changed"""
        if self.rect.collidepoint(mouse_pos):
            self.is_open = not self.is_open
            return False
        
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                if option_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    self.is_open = False
                    return True
            # Click outside closes dropdown
            self.is_open = False
        
        return False
    
    def get_selected(self):
        """Get currently selected option"""
        return self.options[self.selected_index]


class Player:
    """Player spaceship class"""
    
    def __init__(self, x, y, player_type="player.png"):
        self.x = x
        self.y = y
        self.speed = 8
        self.player_type = player_type
        
        # Try to load player image
        try:
            self.image = pygame.image.load(get_image_path(player_type))
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            # Scale to max 80px width while maintaining aspect ratio
            if original_width > 80:
                scale_factor = 80 / original_width
                self.width = 80
                self.height = int(original_height * scale_factor)
            else:
                self.width = original_width
                self.height = original_height
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.has_image = True
        except Exception as e:
            self.has_image = False
            self.width = 64
            self.height = 64
            print(f"Warning: {player_type} not found. Using rectangle.")
    
    def move_left(self):
        """Move player left with boundary checking"""
        self.x -= self.speed
        if self.x < 0:
            self.x = 0
    
    def move_right(self):
        """Move player right with boundary checking"""
        self.x += self.speed
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
    
    def draw(self, screen):
        """Draw the player on screen"""
        if self.has_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Bullet:
    """Bullet/Laser projectile class"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7
        
        # Try to load bullet image
        try:
            self.image = pygame.image.load(get_image_path("bullet.png"))
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            if original_width > 16:
                scale_factor = 16 / original_width
                self.width = 16
                self.height = int(original_height * scale_factor)
            else:
                self.width = original_width
                self.height = original_height
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.has_image = True
        except:
            self.has_image = False
            self.width = 8
            self.height = 32
    
    def update(self):
        """Move bullet upward"""
        self.y -= self.speed
    
    def is_off_screen(self):
        """Check if bullet has left the screen"""
        return self.y < -self.height
    
    def draw(self, screen):
        """Draw the bullet on screen"""
        if self.has_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Enemy:
    """Enemy spaceship class"""
    
    def __init__(self, x, y, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.speed = 2 * speed_multiplier
        
        # Try to load enemy image
        try:
            self.image = pygame.image.load(get_image_path("enemy.png"))
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            if original_width > 70:
                scale_factor = 70 / original_width
                self.width = 70
                self.height = int(original_height * scale_factor)
            else:
                self.width = original_width
                self.height = original_height
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.has_image = True
        except:
            self.has_image = False
            self.width = 64
            self.height = 64
    
    def update(self):
        """Move enemy downward"""
        self.y += self.speed
    
    def is_off_screen(self):
        """Check if enemy has left the bottom of screen"""
        return self.y > SCREEN_HEIGHT
    
    def draw(self, screen):
        """Draw the enemy on screen"""
        if self.has_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    """Main game class"""
    
    def __init__(self):
        # Initialize display
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            self.retro_font_small = pygame.font.Font(get_font_path("RETRO_SPACE.ttf"), 24)
            self.retro_font_medium = pygame.font.Font(get_font_path("RETRO_SPACE.ttf"), 36)
            self.retro_font_large = pygame.font.Font(get_font_path("RETRO_SPACE.ttf"), 48)
            self.oleaguid_font = pygame.font.Font(get_font_path("Oleaguid.ttf"), 72)
            print("Custom fonts loaded successfully")
        except Exception as e:
            print(f"Error loading fonts: {e}")
            self.retro_font_small = pygame.font.Font(None, 24)
            self.retro_font_medium = pygame.font.Font(None, 36)
            self.retro_font_large = pygame.font.Font(None, 48)
            self.oleaguid_font = pygame.font.Font(None, 72)
        
        # Load background
        self.load_background()
        
        # Audio settings
        self.sfx_volume = 0.5
        self.music_volume = 0.2
        self.test_sound_type = "laser"  # Default test sound for SFX slider
        self.sounds = {}
        self.load_sounds()
        
        # Game state
        self.state = "MAIN_MENU"
        self.running = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.lives = 5
        self.difficulty = "medium"  # easy, medium, hard
        self.game_speed_multiplier = 1.0
        self.high_scores = self.load_high_scores()  # Dictionary with high score per difficulty
        self.leaderboards = self.load_leaderboards()
        self.selected_character = "player.png"
        self.player_life_icon = None
        self.player_name = ""
        self.entering_name = False
        self.name_error_message = ""
        self.password_input = ""
        self.password_error = ""
        
        # Game objects
        self.player = None
        self.bullets = []
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60
        
        # Initialize UI
        self.init_ui()
        
        # Start menu music
        self.play_music("menu")
    
    def load_background(self):
        """Load background image"""
        self.has_background = False
        for bg_file in ["background.avif", "background.png", "background.jpg"]:
            try:
                bg_path = get_image_path(bg_file)
                if bg_file.endswith('.avif'):
                    pil_image = Image.open(bg_path).convert('RGB')
                    pil_image = pil_image.resize((SCREEN_WIDTH, SCREEN_HEIGHT), Image.Resampling.LANCZOS)
                    image_string = pil_image.tobytes()
                    self.background = pygame.image.fromstring(image_string, pil_image.size, pil_image.mode)
                else:
                    self.background = pygame.image.load(bg_path)
                    self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.has_background = True
                print(f"Loaded background: {bg_file}")
                break
            except:
                continue
    
    def load_sounds(self):
        """Load sound effects"""
        sound_files = {
            'laser': 'laser.wav',
            'explosion': 'explosion.wav',
            'game_over': 'game_over.mp3',
            'click': 'click.wav'
        }
        
        for name, filename in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(get_audio_path(filename))
            except:
                self.sounds[name] = None
                print(f"Warning: Could not load {filename}")
        
        # Load gameplay background music
        self.gameplay_music_loaded = False
        for music_file in ["background_music.mp3", "background_music.ogg", "background_music.wav"]:
            try:
                # Store the path for later use
                self.gameplay_music_path = get_audio_path(music_file)
                pygame.mixer.music.load(self.gameplay_music_path)
                self.gameplay_music_loaded = True
                print(f"Loaded gameplay music: {music_file}")
                break
            except:
                continue
        
        # Load main menu music
        self.menu_music_loaded = False
        for music_file in ["main_menu_music.mp3", "main_menu_music.ogg", "main_menu_music.wav"]:
            try:
                self.menu_music_path = get_audio_path(music_file)
                # Don't load it yet, just store the path
                self.menu_music_loaded = True
                print(f"Found menu music: {music_file}")
                break
            except:
                continue
        
        self.current_music = None  # Track which music is playing
        self.update_volumes()
    
    def update_volumes(self):
        """Update sound volumes"""
        if self.sounds.get('explosion'):
            self.sounds['explosion'].set_volume(0.1 * self.sfx_volume)
        if self.sounds.get('game_over'):
            self.sounds['game_over'].set_volume(0.25 * self.sfx_volume)
        if self.sounds.get('laser'):
            self.sounds['laser'].set_volume(self.sfx_volume)
        if self.sounds.get('click'):
            self.sounds['click'].set_volume(0.3 * self.sfx_volume)  # 30% volume for clicks
        pygame.mixer.music.set_volume(self.music_volume)
    
    def play_sound(self, name):
        """Play sound effect"""
        if self.sounds.get(name):
            self.sounds[name].play()
    
    def play_music(self, music_type):
        """Play menu or gameplay music"""
        if music_type == "menu" and self.menu_music_loaded:
            if self.current_music != "menu":
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.menu_music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = "menu"
        elif music_type == "gameplay" and self.gameplay_music_loaded:
            if self.current_music != "gameplay":
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.gameplay_music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = "gameplay"
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def init_ui(self):
        """Initialize UI elements"""
        cx = SCREEN_WIDTH // 2
        
        # Main menu
        self.main_menu_buttons = {
            'start': Button(cx - 150, 260, 300, 60, "START", self.retro_font_medium),
            'leaderboard': Button(cx - 150, 340, 300, 60, "LEADERBOARD", self.retro_font_medium),
            'settings': Button(cx - 150, 420, 300, 60, "SETTINGS", self.retro_font_medium),
            'quit': Button(cx - 150, 500, 300, 60, "QUIT", self.retro_font_medium)
        }
        
        # Character selection
        self.character_buttons = []
        characters = [("player.png", "SHIP 1"), ("player2.PNG", "SHIP 2"), ("player3.png", "SHIP 3")]
        for i, (char_file, char_name) in enumerate(characters):
            x = cx - 270 + (i * 180)
            self.character_buttons.append({
                'file': char_file,
                'name': char_name,
                'button': Button(x, 450, 150, 50, "SELECT", self.retro_font_small),
                'preview_rect': pygame.Rect(x, 250, 150, 150),
                'image': self.load_character_preview(char_file)
            })
        self.char_back_button = Button(50, 50, 150, 50, "BACK", self.retro_font_small)
        
        # Difficulty selection
        self.difficulty_buttons = {
            'easy': Button(cx - 350, 320, 200, 70, "EASY", self.retro_font_medium, GREEN, LIGHT_GRAY),
            'medium': Button(cx - 100, 320, 200, 70, "MEDIUM", self.retro_font_medium, BLUE, LIGHT_GRAY),
            'hard': Button(cx + 150, 320, 200, 70, "HARD", self.retro_font_medium, RED, LIGHT_GRAY)
        }
        self.difficulty_back_button = Button(50, 50, 150, 50, "BACK", self.retro_font_small)
        
        # Leaderboard
        self.leaderboard_buttons = {
            'easy': Button(cx - 380, 180, 230, 50, "EASY", self.retro_font_small, GREEN, LIGHT_GRAY),
            'medium': Button(cx - 115, 180, 230, 50, "MEDIUM", self.retro_font_small, BLUE, LIGHT_GRAY),
            'hard': Button(cx + 150, 180, 230, 50, "HARD", self.retro_font_small, RED, LIGHT_GRAY)
        }
        self.leaderboard_back_button = Button(cx - 100, 650, 200, 50, "BACK", self.retro_font_medium)
        self.clear_leaderboard_button = Button(cx + 300, 650, 180, 50, "CLEAR ALL", self.retro_font_small, RED, LIGHT_GRAY)
        self.active_leaderboard = "medium"
        
        # Password entry (for clearing leaderboards)
        self.password_entry_rect = pygame.Rect(cx - 200, 300, 400, 50)
        self.submit_password_button = Button(cx - 100, 380, 200, 50, "SUBMIT", self.retro_font_medium)
        self.cancel_password_button = Button(cx - 100, 450, 200, 50, "CANCEL", self.retro_font_medium)
        
        # Name entry (for high score)
        self.name_entry_rect = pygame.Rect(cx - 200, 300, 400, 50)
        self.submit_name_button = Button(cx - 100, 380, 200, 50, "SUBMIT", self.retro_font_medium)
        
        # Settings
        self.sfx_slider = Slider(cx - 200, 250, 400, 20, 0, 100, self.sfx_volume * 100, "SFX Volume")
        self.music_slider = Slider(cx - 200, 350, 400, 20, 0, 100, self.music_volume * 100, "Music Volume")
        self.test_sound_dropdown = Dropdown(cx - 200, 470, 400, 40, ["Laser", "Explosion"], "Test Sound", 0)
        self.fullscreen_checkbox = Checkbox(cx - 100, 570, 30, "Fullscreen Mode", self.fullscreen)
        self.settings_back_button = Button(cx - 100, 650, 200, 50, "BACK", self.retro_font_medium)
        
        # Game over
        self.game_over_buttons = {
            'restart': Button(cx - 250, 400, 200, 60, "RESTART", self.retro_font_medium),
            'menu': Button(cx + 50, 400, 200, 60, "MENU", self.retro_font_medium)
        }
        
        # Quit confirm
        self.quit_confirm_buttons = {
            'yes': Button(cx - 200, 350, 150, 60, "YES", self.retro_font_medium, RED, LIGHT_GRAY),
            'no': Button(cx + 50, 350, 150, 60, "NO", self.retro_font_medium, GREEN, LIGHT_GRAY)
        }
        
        # Pause menu
        self.pause_buttons = {
            'resume': Button(cx - 150, 300, 300, 60, "RESUME", self.retro_font_medium),
            'settings': Button(cx - 150, 380, 300, 60, "SETTINGS", self.retro_font_medium),
            'menu': Button(cx - 150, 460, 300, 60, "QUIT TO MENU", self.retro_font_medium)
        }
    
    def load_character_preview(self, filename):
        """Load and scale character preview"""
        try:
            img = pygame.image.load(get_image_path(filename))
            return pygame.transform.scale(img, (120, 120))
        except:
            return None
    
    def load_player_life_icon(self):
        """Load player life icon (small version of selected ship)"""
        try:
            img = pygame.image.load(get_image_path(self.selected_character))
            self.player_life_icon = pygame.transform.scale(img, (30, 30))
        except:
            self.player_life_icon = None
    
    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists("high_scores.json"):
                with open("high_scores.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return {"easy": 0, "medium": 0, "hard": 0}
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open("high_scores.json", "w") as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def load_leaderboards(self):
        """Load leaderboards from file"""
        try:
            if os.path.exists("leaderboards.json"):
                with open("leaderboards.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return {"easy": [], "medium": [], "hard": []}
    
    def save_leaderboards(self):
        """Save leaderboards to file"""
        try:
            with open("leaderboards.json", "w") as f:
                json.dump(self.leaderboards, f, indent=2)
        except Exception as e:
            print(f"Error saving leaderboards: {e}")
    
    def add_to_leaderboard(self, name, score, difficulty):
        """Add score to leaderboard and keep top 10"""
        entry = {"name": name[:10], "score": score}  # Limit name to 10 chars
        self.leaderboards[difficulty].append(entry)
        # Sort by score (descending) and keep top 10
        self.leaderboards[difficulty].sort(key=lambda x: x["score"], reverse=True)
        self.leaderboards[difficulty] = self.leaderboards[difficulty][:10]
        self.save_leaderboards()
    
    def validate_name(self, name):
        """Validate player name for leaderboard"""
        # Check if empty
        if not name or name.strip() == "":
            return False, "Please enter a name!"
        
        # Check if name already exists in this difficulty's leaderboard
        leaderboard = self.leaderboards[self.difficulty]
        for entry in leaderboard:
            if entry["name"].upper() == name.upper():
                return False, "Username already taken!"
        
        return True, ""
    
    def clear_all_leaderboards(self):
        """Clear all leaderboards and high scores"""
        self.leaderboards = {"easy": [], "medium": [], "hard": []}
        self.high_scores = {"easy": 0, "medium": 0, "hard": 0}
        self.save_leaderboards()
        self.save_high_scores()
        print("All leaderboards and high scores cleared!")
    
    def start_game(self):
        """Start the game"""
        self.state = "PLAYING"
        self.game_over = False
        self.paused = False
        self.score = 0
        
        # Set lives based on difficulty
        if self.difficulty == "easy":
            self.lives = 7
            self.game_speed_multiplier = 1.0
        elif self.difficulty == "medium":
            self.lives = 5
            self.game_speed_multiplier = 1.08
        else:  # hard
            self.lives = 3
            self.game_speed_multiplier = 1.15
        
        self.player = Player(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT - 120, self.selected_character)
        self.bullets = []
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.load_player_life_icon()
        self.play_music("gameplay")
    
    def spawn_enemy(self):
        """Spawn enemy"""
        temp = Enemy(0, -100, self.game_speed_multiplier)
        x = random.randint(0, SCREEN_WIDTH - temp.width)
        self.enemies.append(Enemy(x, -temp.height, self.game_speed_multiplier))
    
    def shoot_bullet(self):
        """Shoot bullet"""
        if self.player:
            x = self.player.x + self.player.width // 2 - 4
            self.bullets.append(Bullet(x, self.player.y))
            self.play_sound('laser')
    
    def check_collisions(self):
        """Check collisions"""
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.score += 10
                    self.play_sound('explosion')
                    break
        
        # Check enemy collision with player
        if self.player:
            for enemy in self.enemies[:]:
                if self.player.get_rect().colliderect(enemy.get_rect()):
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.lives -= 1
                    self.play_sound('explosion')
                    if self.lives <= 0:
                        self.end_game()
                    break
    
    def end_game(self):
        """End the game and update high score"""
        self.game_over = True
        pygame.mixer.music.stop()
        self.play_sound('game_over')
        
        # Update high score for this difficulty if needed
        if self.score > self.high_scores[self.difficulty]:
            self.high_scores[self.difficulty] = self.score
            self.save_high_scores()
        
        # Check if score qualifies for leaderboard (top 10 or less than 10 entries)
        leaderboard = self.leaderboards[self.difficulty]
        if len(leaderboard) < 10 or self.score > leaderboard[-1]["score"]:
            self.entering_name = True
            self.player_name = ""
            self.name_error_message = ""
            self.state = "NAME_ENTRY"
        else:
            self.state = "GAME_OVER"
    
    def update_game(self):
        """Update game"""
        if self.game_over:
            return
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                # Lose a life when enemy passes through
                self.lives -= 1
                if self.lives <= 0:
                    self.end_game()
        
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
        
        self.check_collisions()
    
    def handle_game_input(self):
        """Handle game input"""
        if not self.game_over and self.player:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
    
    def draw_background(self):
        """Draw background"""
        if self.has_background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
    
    def draw_main_menu(self):
        """Draw main menu"""
        self.draw_background()
        
        title = self.oleaguid_font.render("SPACE SHOOTER", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
        
        subtitle = self.retro_font_small.render("A bored GabTzy project", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220)))
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_menu_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen)
    
    def draw_character_select(self):
        """Draw character selection"""
        self.draw_background()
        
        title = self.retro_font_large.render("SELECT YOUR SHIP", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        
        mouse_pos = pygame.mouse.get_pos()
        for char in self.character_buttons:
            # Draw preview
            pygame.draw.rect(self.screen, DARK_BLUE, char['preview_rect'], border_radius=10)
            pygame.draw.rect(self.screen, WHITE if char['file'] == self.selected_character else GRAY, 
                           char['preview_rect'], 3, border_radius=10)
            
            if char['image']:
                img_rect = char['image'].get_rect(center=char['preview_rect'].center)
                self.screen.blit(char['image'], img_rect)
            
            # Draw name
            name_text = self.retro_font_small.render(char['name'], True, WHITE)
            name_rect = name_text.get_rect(center=(char['preview_rect'].centerx, char['preview_rect'].bottom + 30))
            self.screen.blit(name_text, name_rect)
            
            # Draw button
            char['button'].check_hover(mouse_pos)
            char['button'].draw(self.screen)
        
        self.char_back_button.check_hover(mouse_pos)
        self.char_back_button.draw(self.screen)
    
    def draw_settings(self):
        """Draw settings"""
        self.draw_background()
        
        title = self.retro_font_large.render("SETTINGS", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        
        self.sfx_slider.draw(self.screen, self.retro_font_small)
        self.music_slider.draw(self.screen, self.retro_font_small)
        self.test_sound_dropdown.draw(self.screen, self.retro_font_small)
        self.fullscreen_checkbox.draw(self.screen, self.retro_font_small)
        
        mouse_pos = pygame.mouse.get_pos()
        self.settings_back_button.check_hover(mouse_pos)
        self.settings_back_button.draw(self.screen)
    
    def draw_playing(self):
        """Draw gameplay"""
        self.draw_background()
        
        if self.player:
            self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw score
        score_text = self.retro_font_medium.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))
        
        # Draw high score for current difficulty
        high_score_text = self.retro_font_small.render(f"HIGH SCORE: {self.high_scores[self.difficulty]}", True, WHITE)
        self.screen.blit(high_score_text, (10, 50))
        
        # Draw lives with player icon
        lives_text = self.retro_font_medium.render(str(self.lives), True, GREEN)
        lives_x = SCREEN_WIDTH - 80
        self.screen.blit(lives_text, (lives_x, 10))
        
        # Draw player life icon
        if self.player_life_icon:
            icon_x = lives_x - 40
            self.screen.blit(self.player_life_icon, (icon_x, 15))
    
    def draw_game_over(self):
        """Draw game over"""
        self.draw_background()
        
        title = self.oleaguid_font.render("GAME OVER", True, RED)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        
        score_text = self.retro_font_large.render(f"FINAL SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, 310)))
        
        high_score_text = self.retro_font_medium.render(f"HIGH SCORE: {self.high_scores[self.difficulty]}", True, YELLOW)
        self.screen.blit(high_score_text, high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 360)))
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen)
    
    def draw_quit_confirm(self):
        """Draw quit confirmation"""
        self.draw_background()
        
        title = self.retro_font_large.render("ARE YOU SURE?", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 220)))
        
        subtitle = self.retro_font_small.render("Do you want to quit the game?", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 290)))
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.quit_confirm_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen)
    
    def draw_paused(self):
        """Draw pause screen"""
        # Draw the game in background (frozen)
        if self.has_background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
        
        # Draw frozen game elements
        if self.player:
            self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw score and lives (frozen state)
        score_text = self.retro_font_medium.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.retro_font_small.render(f"HIGH SCORE: {self.high_scores[self.difficulty]}", True, WHITE)
        self.screen.blit(high_score_text, (10, 50))
        
        lives_text = self.retro_font_medium.render(str(self.lives), True, GREEN)
        lives_x = SCREEN_WIDTH - 80
        self.screen.blit(lives_text, (lives_x, 10))
        
        if self.player_life_icon:
            icon_x = lives_x - 40
            self.screen.blit(self.player_life_icon, (icon_x, 15))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw PAUSED title
        title = self.oleaguid_font.render("PAUSED", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        
        # Draw subtitle
        subtitle = self.retro_font_small.render("Game is paused - Choose an option", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 280)))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.pause_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen)
    
    def draw_difficulty_select(self):
        """Draw difficulty selection"""
        self.draw_background()
        
        title = self.retro_font_large.render("SELECT DIFFICULTY", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons and show info only on hover
        for diff, button in self.difficulty_buttons.items():
            button.check_hover(mouse_pos)
            button.draw(self.screen)
            
            # Show difficulty info only when hovering
            if button.is_hovered:
                if diff == "easy":
                    info_text = "7 Lives | Normal Speed"
                elif diff == "medium":
                    info_text = "5 Lives | 8% Faster"
                else:  # hard
                    info_text = "3 Lives | 15% Faster"
                
                info = self.retro_font_small.render(info_text, True, WHITE)
                self.screen.blit(info, info.get_rect(center=(button.rect.centerx, button.rect.bottom + 30)))
        
        self.difficulty_back_button.check_hover(mouse_pos)
        self.difficulty_back_button.draw(self.screen)
    
    def draw_leaderboard(self):
        """Draw leaderboard"""
        self.draw_background()
        
        title = self.retro_font_large.render("LEADERBOARD", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        
        # Draw difficulty tabs
        mouse_pos = pygame.mouse.get_pos()
        for diff, button in self.leaderboard_buttons.items():
            if diff == self.active_leaderboard:
                # Highlight active tab
                pygame.draw.rect(self.screen, button.color, button.rect.inflate(4, 4), border_radius=8)
            button.check_hover(mouse_pos)
            button.draw(self.screen)
        
        # Draw leaderboard entries
        leaderboard = self.leaderboards[self.active_leaderboard]
        y_start = 260
        for i, entry in enumerate(leaderboard):
            rank_text = self.retro_font_small.render(f"#{i+1}", True, YELLOW)
            name_text = self.retro_font_small.render(entry["name"], True, WHITE)
            score_text = self.retro_font_small.render(str(entry["score"]), True, GREEN)
            
            self.screen.blit(rank_text, (200, y_start + i * 35))
            self.screen.blit(name_text, (300, y_start + i * 35))
            self.screen.blit(score_text, (900, y_start + i * 35))
        
        # If leaderboard is empty
        if not leaderboard:
            empty_text = self.retro_font_medium.render("No scores yet!", True, GRAY)
            self.screen.blit(empty_text, empty_text.get_rect(center=(SCREEN_WIDTH // 2, 400)))
        
        self.leaderboard_back_button.check_hover(mouse_pos)
        self.leaderboard_back_button.draw(self.screen)
        
        self.clear_leaderboard_button.check_hover(mouse_pos)
        self.clear_leaderboard_button.draw(self.screen)
    
    def draw_name_entry(self):
        """Draw name entry screen"""
        self.draw_background()
        
        title = self.oleaguid_font.render("NEW HIGH SCORE!", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
        
        score_text = self.retro_font_large.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, 230)))
        
        prompt = self.retro_font_small.render("Enter your name (max 10 characters):", True, WHITE)
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 270)))
        
        # Draw input box
        pygame.draw.rect(self.screen, WHITE, self.name_entry_rect, 3)
        name_surface = self.retro_font_medium.render(self.player_name + "_", True, WHITE)
        self.screen.blit(name_surface, (self.name_entry_rect.x + 10, self.name_entry_rect.y + 10))
        
        # Draw error message if any
        if self.name_error_message:
            error_surface = self.retro_font_small.render(self.name_error_message, True, RED)
            self.screen.blit(error_surface, error_surface.get_rect(center=(SCREEN_WIDTH // 2, 360)))
        
        mouse_pos = pygame.mouse.get_pos()
        self.submit_name_button.check_hover(mouse_pos)
        self.submit_name_button.draw(self.screen)
    
    def draw_password_entry(self):
        """Draw password entry screen for clearing leaderboards"""
        self.draw_background()
        
        title = self.retro_font_large.render("ADMIN ACCESS", True, RED)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
        
        warning = self.retro_font_medium.render("Clear All Leaderboards?", True, YELLOW)
        self.screen.blit(warning, warning.get_rect(center=(SCREEN_WIDTH // 2, 220)))
        
        prompt = self.retro_font_small.render("Enter admin password:", True, WHITE)
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 270)))
        
        # Draw password input box (show asterisks)
        pygame.draw.rect(self.screen, WHITE, self.password_entry_rect, 3)
        password_display = "*" * len(self.password_input) + "_"
        password_surface = self.retro_font_medium.render(password_display, True, WHITE)
        self.screen.blit(password_surface, (self.password_entry_rect.x + 10, self.password_entry_rect.y + 10))
        
        # Draw error message if any
        if self.password_error:
            error_surface = self.retro_font_small.render(self.password_error, True, RED)
            self.screen.blit(error_surface, error_surface.get_rect(center=(SCREEN_WIDTH // 2, 360)))
        
        mouse_pos = pygame.mouse.get_pos()
        self.submit_password_button.check_hover(mouse_pos)
        self.submit_password_button.draw(self.screen)
        
        self.cancel_password_button.check_hover(mouse_pos)
        self.cancel_password_button.draw(self.screen)
    
    def handle_events(self):
        """Handle events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Password entry
                if self.state == "PASSWORD_ENTRY":
                    if event.key == pygame.K_RETURN:
                        if self.password_input == "admin123":
                            self.clear_all_leaderboards()
                            self.password_input = ""
                            self.password_error = ""
                            self.state = "LEADERBOARD"
                        else:
                            self.password_error = "Incorrect password!"
                    elif event.key == pygame.K_BACKSPACE:
                        self.password_input = self.password_input[:-1]
                        self.password_error = ""
                    elif event.key == pygame.K_ESCAPE:
                        self.password_input = ""
                        self.password_error = ""
                        self.state = "LEADERBOARD"
                    elif len(self.password_input) < 20 and event.unicode.isprintable():
                        self.password_input += event.unicode
                        self.password_error = ""
                # Name entry
                elif self.state == "NAME_ENTRY":
                    if event.key == pygame.K_RETURN:
                        is_valid, error_msg = self.validate_name(self.player_name)
                        if is_valid:
                            self.add_to_leaderboard(self.player_name, self.score, self.difficulty)
                            self.entering_name = False
                            self.state = "GAME_OVER"
                        else:
                            self.name_error_message = error_msg
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                        self.name_error_message = ""  # Clear error when typing
                    elif len(self.player_name) < 10 and event.unicode.isprintable():
                        self.player_name += event.unicode.upper()
                        self.name_error_message = ""  # Clear error when typing
                # Only allow ESC to pause during active gameplay
                elif event.key == pygame.K_ESCAPE and self.state == "PLAYING" and not self.game_over:
                    self.paused = not self.paused
                # Allow shooting only when not paused
                elif event.key == pygame.K_SPACE and self.state == "PLAYING" and not self.game_over and not self.paused:
                    self.shoot_bullet()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "PLAYING" and self.paused:
                    self.handle_pause_click(mouse_pos)
                elif self.state == "SETTINGS":
                    self.handle_mouse_click(mouse_pos)
                else:
                    self.handle_mouse_click(mouse_pos)
            
            # Handle sliders
            if self.state == "SETTINGS":
                sfx_released = self.sfx_slider.handle_event(event, mouse_pos)
                self.music_slider.handle_event(event, mouse_pos)
                self.sfx_volume = self.sfx_slider.get_value()
                self.music_volume = self.music_slider.get_value()
                self.update_volumes()
                
                # Play test sound when SFX slider is released
                if sfx_released:
                    if self.test_sound_type == "laser":
                        self.play_sound('laser')
                    elif self.test_sound_type == "explosion":
                        self.play_sound('explosion')
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks"""
        if self.state == "MAIN_MENU":
            if self.main_menu_buttons['start'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "DIFFICULTY_SELECT"
            elif self.main_menu_buttons['leaderboard'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "LEADERBOARD"
            elif self.main_menu_buttons['settings'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "SETTINGS"
            elif self.main_menu_buttons['quit'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "QUIT_CONFIRM"
        
        elif self.state == "CHARACTER_SELECT":
            if self.char_back_button.rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "DIFFICULTY_SELECT"
            else:
                for char in self.character_buttons:
                    if char['button'].rect.collidepoint(mouse_pos):
                        self.play_sound('click')
                        self.selected_character = char['file']
                        self.start_game()
                        break
        
        elif self.state == "DIFFICULTY_SELECT":
            if self.difficulty_back_button.rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "MAIN_MENU"
            else:
                for diff, button in self.difficulty_buttons.items():
                    if button.rect.collidepoint(mouse_pos):
                        self.play_sound('click')
                        self.difficulty = diff
                        self.state = "CHARACTER_SELECT"
                        break
        
        elif self.state == "LEADERBOARD":
            if self.leaderboard_back_button.rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "MAIN_MENU"
            elif self.clear_leaderboard_button.rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.password_input = ""
                self.password_error = ""
                self.state = "PASSWORD_ENTRY"
            else:
                for diff, button in self.leaderboard_buttons.items():
                    if button.rect.collidepoint(mouse_pos):
                        self.play_sound('click')
                        self.active_leaderboard = diff
                        break
        
        elif self.state == "NAME_ENTRY":
            if self.submit_name_button.rect.collidepoint(mouse_pos):
                is_valid, error_msg = self.validate_name(self.player_name)
                if is_valid:
                    self.play_sound('click')
                    self.add_to_leaderboard(self.player_name, self.score, self.difficulty)
                    self.entering_name = False
                    self.state = "GAME_OVER"
                else:
                    self.name_error_message = error_msg
        
        elif self.state == "PASSWORD_ENTRY":
            if self.submit_password_button.rect.collidepoint(mouse_pos):
                if self.password_input == "admin123":
                    self.play_sound('click')
                    self.clear_all_leaderboards()
                    self.password_input = ""
                    self.password_error = ""
                    self.state = "LEADERBOARD"
                else:
                    self.password_error = "Incorrect password!"
            elif self.cancel_password_button.rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.password_input = ""
                self.password_error = ""
                self.state = "LEADERBOARD"
        
        elif self.state == "SETTINGS":
            if self.settings_back_button.rect.collidepoint(mouse_pos):
                self.play_sound('click')
                # Return to previous state (could be MAIN_MENU or paused PLAYING)
                if hasattr(self, 'previous_state') and self.previous_state == "PLAYING":
                    self.state = "PLAYING"
                    self.previous_state = None
                else:
                    self.state = "MAIN_MENU"
            elif self.fullscreen_checkbox.handle_click(mouse_pos):
                self.play_sound('click')
                self.toggle_fullscreen()
            elif self.test_sound_dropdown.handle_click(mouse_pos):
                # Update test sound type based on dropdown selection
                selected = self.test_sound_dropdown.get_selected()
                self.test_sound_type = selected.lower()
                if self.test_sound_dropdown.selected_index != self.test_sound_dropdown.selected_index:  # Selection changed
                    self.play_sound('click')
        
        elif self.state == "GAME_OVER":
            if self.game_over_buttons['restart'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.start_game()
            elif self.game_over_buttons['menu'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "MAIN_MENU"
                self.play_music("menu")
        
        elif self.state == "QUIT_CONFIRM":
            if self.quit_confirm_buttons['yes'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.running = False
            elif self.quit_confirm_buttons['no'].rect.collidepoint(mouse_pos):
                self.play_sound('click')
                self.state = "MAIN_MENU"
    
    def handle_pause_click(self, mouse_pos):
        """Handle pause menu clicks"""
        if self.pause_buttons['resume'].rect.collidepoint(mouse_pos):
            self.play_sound('click')
            self.paused = False
        elif self.pause_buttons['settings'].rect.collidepoint(mouse_pos):
            self.play_sound('click')
            self.previous_state = "PLAYING"
            self.state = "SETTINGS"
        elif self.pause_buttons['menu'].rect.collidepoint(mouse_pos):
            self.play_sound('click')
            self.state = "MAIN_MENU"
            self.paused = False
            self.play_music("menu")
    
    def run(self):
        """Main loop"""
        while self.running:
            self.handle_events()
            
            if self.state == "PLAYING":
                if not self.paused:
                    self.handle_game_input()
                    self.update_game()
                self.draw_playing()
                if self.paused:
                    self.draw_paused()
            elif self.state == "MAIN_MENU":
                self.draw_main_menu()
            elif self.state == "DIFFICULTY_SELECT":
                self.draw_difficulty_select()
            elif self.state == "CHARACTER_SELECT":
                self.draw_character_select()
            elif self.state == "LEADERBOARD":
                self.draw_leaderboard()
            elif self.state == "NAME_ENTRY":
                self.draw_name_entry()
            elif self.state == "PASSWORD_ENTRY":
                self.draw_password_entry()
            elif self.state == "SETTINGS":
                self.draw_settings()
            elif self.state == "GAME_OVER":
                self.draw_game_over()
            elif self.state == "QUIT_CONFIRM":
                self.draw_quit_confirm()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
