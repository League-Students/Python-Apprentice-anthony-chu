import pygame
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
GRAVITY = 1.0

# Colors
COLOR_BG = (51, 51, 51)
COLOR_FLOOR = (85, 85, 85)
COLOR_HP_BAR = (46, 204, 113)
COLOR_HP_BG = (34, 34, 34)
COLOR_TEXT = (255, 255, 255)
COLOR_HITBOX = (241, 196, 15)

# Set up Display Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("League Brawler - Pygame Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
game_over_font = pygame.font.SysFont("Arial", 40, bold=True)

class Fighter:
    def __init__(self, x, y, color, controls):
        # Position and Dimensions
        self.rect = pygame.Rect(x, y, 40, 100)
        self.color = color
        self.controls = controls  # Dictionary mapping actions to keys
        
        # Physics Vectors
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        self.facing = 1  # 1 = Right, -1 = Left
        
        # Combat Stats
        self.hp = 100
        self.max_hp = 100
        self.is_attacking = False
        self.attack_cooldown = 0
        self.hit_flash = 0
        self.attack_rect = None

    def handle_input(self, keys):
        if self.hp <= 0:
            return

        # Horizontal movement inputs
        self.vx = 0
        if keys[self.controls["left"]]:
            self.vx = -5
            self.facing = -1
        if keys[self.controls["right"]]:
            self.vx = 5
            self.facing = 1

        # Jump input
        if keys[self.controls["jump"]] and not self.is_jumping:
            self.vy = -18
            self.is_jumping = True

        # Attack input trigger
        if keys[self.controls["attack"]] and self.attack_cooldown == 0:
            self.is_attacking = True
            self.attack_cooldown = 20  # Frames total for the move
            
            # Create a localized attack hitbox based on facing direction
            reach = 40
            if self.facing == 1:
                self.attack_rect = pygame.Rect(self.rect.right, self.rect.top + 30, reach, 20)
            else:
                self.attack_rect = pygame.Rect(self.rect.left - reach, self.rect.top + 30, reach, 20)

    def update_physics(self, floor_y):
        # Flash timer logic
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Cooldown timer logic
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            # Hide the attack hitbox halfway through the cooldown animation
            if self.attack_cooldown < 10:
                self.is_attacking = False
                self.attack_rect = None

        if self.hp <= 0:
            return

        # Apply movements and gravity simulations
        self.rect.x += self.vx
        self.vy += GRAVITY
        self.rect.y += self.vy

        # Left/Right screen boundary boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Floor collision check
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.vy = 0
            self.is_jumping = False

    def check_hit(self, target):
        # Collision detection evaluation using standard rect intersections
        if self.is_attacking and self.attack_rect and target.hp > 0:
            if self.attack_rect.colliderect(target.rect):
                target.hp = max(0, target.hp - 10)
                target.hit_flash = 5
                # Deselect active attack to prevent multi-hit frames
                self.is_attacking = False
                self.attack_rect = None

    def draw(self, surface):
        # Swap fill color to white during an active damage frame
        current_color = (255, 255, 255) if self.hit_flash > 0 else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1)  # Character border

        # Draw the weapon hitbox layer
        if self.is_attacking and self.attack_rect:
            pygame.draw.rect(surface, COLOR_HITBOX, self.attack_rect)


def draw_hud(player1, player2):
    # Text labels
    p1_label = font.render("PLAYER 1 (A/D/W + F)", True, COLOR_TEXT)
    p2_label = font.render("PLAYER 2 (ARROWS + M)", True, COLOR_TEXT)
    screen.blit(p1_label, (50, 15))
    screen.blit(p2_label, (550, 15))

    # P1 Health bar rendering configurations
    pygame.draw.rect(screen, COLOR_HP_BG, (50, 40, 200, 20))
    p1_hp_width = int((player1.hp / player1.max_hp) * 200)
    pygame.draw.rect(screen, COLOR_HP_BAR, (50, 40, p1_hp_width, 20))

    # P2 Health bar rendering configurations
    pygame.draw.rect(screen, COLOR_HP_BG, (550, 40, 200, 20))
    p2_hp_width = int((player2.hp / player2.max_hp) * 200)
    pygame.draw.rect(screen, COLOR_HP_BAR, (750 - p2_hp_width, 40, p2_hp_width, 20))


# Define Keyboard mappings
p1_keys = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_f}
p2_keys = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "attack": pygame.K_m}

# Instantiate OOP Fighters
p1 = Fighter(150, 250, (52, 152, 219), p1_keys)  # Blue Fighter
p2 = Fighter(610, 250, (231, 76, 60), p2_keys)   # Red Fighter

# Main Loop Execution Block
floor_y = 350
running = True

while running:
    clock.tick(FPS)
    
    # 1. Event Handling Layer
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Logic Update Layer
    keys = pygame.key.get_pressed()
    p1.handle_input(keys)
    p2.handle_input(keys)

    p1.update_physics(floor_y)
    p2.update_physics(floor_y)

    # Cross-reference attack hitboxes with targets
    p1.check_hit(p2)
    p2.check_hit(p1)

    # 3. Drawing / Rendering Layer
    screen.fill(COLOR_BG)
    pygame.draw.rect(screen, COLOR_FLOOR, (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y))

    p1.draw(screen)
    p2.draw(screen)
    draw_hud(p1, p2)

    # Win state evaluation overlay 
    if p1.hp <= 0:
        game_over_surface = game_over_font.render("PLAYER 2 WINS!", True, (241, 196, 15))
        screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 20))
    elif p2.hp <= 0:
        game_over_surface = game_over_font.render("PLAYER 1 WINS!", True, (241, 196, 15))
        screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
