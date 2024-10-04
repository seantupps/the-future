import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 480, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Dodger")

# Load assets
SHIP_WIDTH, SHIP_HEIGHT = 50, 38
ASTEROID_WIDTH, ASTEROID_HEIGHT = 50, 50

ship_img = pygame.Surface((SHIP_WIDTH, SHIP_HEIGHT), pygame.SRCALPHA)
pygame.draw.polygon(ship_img, (255, 255, 255), [(0, SHIP_HEIGHT), (SHIP_WIDTH/2, 0), (SHIP_WIDTH, SHIP_HEIGHT)])

asteroid_img = pygame.Surface((ASTEROID_WIDTH, ASTEROID_HEIGHT), pygame.SRCALPHA)
pygame.draw.circle(asteroid_img, (169, 169, 169), (ASTEROID_WIDTH//2, ASTEROID_HEIGHT//2), ASTEROID_WIDTH//2)

# Fonts
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surf.blit(text_surface, text_rect)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ship_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speed = 5

    def update(self):
        self.speedx = 0
        # Get keys pressed
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -self.speed
        if keystate[pygame.K_RIGHT]:
            self.speedx = self.speed
        self.rect.x += self.speedx
        # Keep within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image_orig = asteroid_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - ASTEROID_WIDTH)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = speed
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        # Rotate asteroid
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # Reset position if off screen
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(0, WIDTH - ASTEROID_WIDTH)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 6)

# Game loop
def main():
    clock = pygame.time.Clock()
    running = True
    score = 0
    speed_increase = 0.005
    asteroid_speed = 2

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    # Spawn initial asteroids
    for _ in range(8):
        asteroid = Asteroid(asteroid_speed)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    while running:
        clock.tick(60)  # 60 FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        # Update
        all_sprites.update()

        # Check for collisions
        hits = pygame.sprite.spritecollide(player, asteroids, False)
        if hits:
            running = False

        # Increase difficulty over time
        asteroid_speed += speed_increase
        for asteroid in asteroids:
            asteroid.speedy = asteroid_speed

        # Draw/render
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        score += 1
        draw_text(screen, f"Score: {score}", 18, WIDTH / 2, 10)
        pygame.display.flip()

    # Game Over screen
    screen.fill((0, 0, 0))
    draw_text(screen, "GAME OVER", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, f"Final Score: {score}", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to exit", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                waiting = False
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()