import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side Scrolling Game")

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Font for score and game over text
font = pygame.font.Font(None, 36)

# Global variables
SCORE = 0
LEVEL = 1

# Load images for player, enemy, and collectible
player_image = pygame.Surface((50, 50))
player_image.fill(BLUE)

enemy_image = pygame.Surface((50, 50))
enemy_image.fill(RED)

collectible_image = pygame.Surface((30, 30))
collectible_image.fill(GREEN)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 150)
        self.speed_x = 0
        self.speed_y = 0
        self.health = 100
        self.lives = 3
        self.is_jumping = False
        self.gravity = 0.8
        self.jump_power = -15

    def update(self):
        # Apply gravity
        self.speed_y += self.gravity
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # Prevent player from falling off the screen
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.speed_y = self.jump_power

    def move_left(self):
        self.speed_x = -5

    def move_right(self):
        self.speed_x = 5

    def stop(self):
        self.speed_x = 0

    def shoot(self):
        # Shoot a projectile
        projectile = Projectile(self.rect.centerx, self.rect.top)
        all_sprites.add(projectile)
        projectiles.add(projectile)

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = 10

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left > WIDTH:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.randint(-3, -1)
        self.health = 50

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right < 0:
            self.kill()

# Collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, type_):
        super().__init__()
        self.image = collectible_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.type = type_

    def apply_effect(self, player):
        if self.type == "health":
            player.health += 20
            if player.health > 100:
                player.health = 100
        elif self.type == "life":
            player.lives += 1

# Camera class
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.speed = 0.1

    def apply(self, target):
        return target.rect.move(self.offset.x, 0)

    def update(self, player):
        self.offset.x = -player.rect.centerx + WIDTH // 4

# Function to display score
def display_score():
    global SCORE
    score_text = font.render(f"Score: {SCORE}", True, BLACK)
    screen.blit(score_text, (10, 10))

# Function to handle game over
def game_over():
    game_over_text = font.render("Game Over! Press R to Restart", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 4, HEIGHT // 2))

# Function to create levels
def create_level(level):
    for i in range(level * 5):
        enemy = Enemy(WIDTH + i * 200, HEIGHT - 150)
        all_sprites.add(enemy)
        enemies.add(enemy)

    if level == 3:
        boss_enemy = Enemy(WIDTH + 1000, HEIGHT - 150)
        boss_enemy.health = 200  # Boss has more health
        all_sprites.add(boss_enemy)
        enemies.add(boss_enemy)

# Initialize all sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create camera
camera = Camera()

# Create level 1
create_level(LEVEL)

# Main game loop
running = True
game_over_flag = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check for keypresses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move_left()
            if event.key == pygame.K_RIGHT:
                player.move_right()
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_x:
                player.shoot()
            if event.key == pygame.K_r and game_over_flag:
                SCORE = 0
                LEVEL = 1
                player.lives = 3
                player.health = 100
                create_level(LEVEL)
                game_over_flag = False

        # Check for key releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.stop()

    if not game_over_flag:
        # Update all sprites
        all_sprites.update()

        # Update camera
        camera.update(player)

        # Check for collisions between projectiles and enemies
        for projectile in projectiles:
            enemy_hits = pygame.sprite.spritecollide(projectile, enemies, True)
            if enemy_hits:
                SCORE += 10
                projectile.kill()

        # Check if player collides with collectibles
        for collectible in collectibles:
            if pygame.sprite.collide_rect(player, collectible):
                collectible.apply_effect(player)
                collectible.kill()

        # Check for game over condition
        if player.lives <= 0:
            game_over_flag = True

        # Draw everything
        screen.fill(WHITE)
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        display_score()

    else:
        # Game over screen
        game_over()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
