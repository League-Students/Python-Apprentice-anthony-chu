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
pygame.display.set_caption("League Brawler - Knockback Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
game_over_font = pygame.font.SysFont("Arial", 40, bold=True)

class Fighter:
    def __init__(self, x, y, color, controls):
        # Position and Dimensions
        self.rect = pygame.Rect(x, y, 40, 100)
        self.color = color
        self.controls = controls  
        
        # Physics Vectors
        self.vx = 0
        self.vy = 0
        self.knockback_vx = 0  # Added for knockback velocity tracker
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

        # Horizontal movement inputs (only allowed if not experiencing heavy knockback)
        self.vx = 0
        if abs(self.knockback_vx) < 2:
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
        if keys[self.controls["attack"]] and self.attack_cooldown == 0 and abs(self.knockback_vx) < 3:
            self.is_attacking = True
            self.attack_cooldown = 20  
            
            # Create an attack hitbox
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
            if self.attack_cooldown < 10:
                self.is_attacking = False
                self.attack_rect = None

        if self.hp <= 0:
            return

        # Apply standard movement velocity combined with knockback forces
        self.rect.x += (self.vx + self.knockback_vx)
        self.vy += GRAVITY
        self.rect.y += self.vy

        # Apply friction to the knockback vector so it decays smoothly over time
        if self.knockback_vx > 0:
            self.knockback_vx -= 0.5
            if self.knockback_vx < 0: self.knockback_vx = 0
        elif self.knockback_vx < 0:
            self.knockback_vx += 0.5
            if self.knockback_vx > 0: self.knockback_vx = 0

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.knockback_vx = 0  # Stop momentum if hitting a wall
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.knockback_vx = 0  # Stop momentum if hitting a wall

        # Floor collision check
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.vy = 0
            self.is_jumping = False

    def check_hit(self, target):
        if self.is_attacking and self.attack_rect and target.hp > 0:
            if self.attack_rect.colliderect(target.rect):
                target.hp = max(0, target.hp - 10)
                target.hit_flash = 5
                
                # Apply knockback vector relative to attacker's current facing direction
                # A facing value of 1 pushes target right (+12), -1 pushes target left (-12)
                target.knockback_vx = self.facing * 12
                
                # Cancel the active hitbox frame to prevent multiple hits instantly
                self.is_attacking = False
                self.attack_rect = None

    def draw(self, surface):
        current_color = (255, 255, 255) if self.hit_flash > 0 else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1)  

        if self.is_attacking and self.attack_rect:
            pygame.draw.rect(surface, COLOR_HITBOX, self.attack_rect)


def draw_hud(player1, player2):
    p1_label = font.render("PLAYER 1 (A/D/W + F)", True, COLOR_TEXT)
    p2_label = font.render("PLAYER 2 (ARROWS + M)", True, COLOR_TEXT)
    screen.blit(p1_label, (50, 15))
    screen.blit(p2_label, (550, 15))

    pygame.draw.rect(screen, COLOR_HP_BG, (50, 40, 200, 20))
    p1_hp_width = int((player1.hp / player1.max_hp) * 200)
    pygame.draw.rect(screen, COLOR_HP_BAR, (50, 40, p1_hp_width, 20))

    pygame.draw.rect(screen, COLOR_HP_BG, (550, 40, 200, 20))
    p2_hp_width = int((player2.hp / player2.max_hp) * 200)
    pygame.draw.rect(screen, COLOR_HP_BAR, (750 - p2_hp_width, 40, p2_hp_width, 20))


# Keyboard mappings
p1_keys = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_f}
p2_keys = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "attack": pygame.K_m}

# Instantiate Fighters
p1 = Fighter(150, 250, (52, 152, 219), p1_keys)  
p2 = Fighter(610, 250, (231, 76, 60), p2_keys)   

floor_y = 350
running = True

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    p1.handle_input(keys)
    p2.handle_input(keys)

    p1.update_physics(floor_y)
    p2.update_physics(floor_y)

    p1.check_hit(p2)
    p2.check_hit(p1)

    screen.fill(COLOR_BG)
    pygame.draw.rect(screen, COLOR_FLOOR, (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y))

    p1.draw(screen)
    p2.draw(screen)
    draw_hud(p1, p2)

    if p1.hp <= 0:
        game_over_surface = game_over_font.render("PLAYER 2 WINS!", True, (241, 196, 15))
        screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 20))
    elif p2.hp <= 0:
        game_over_surface = game_over_font.render("PLAYER 1 WINS!", True, (241, 196, 15))
        screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
