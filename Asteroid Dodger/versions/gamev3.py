import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Asteroid Dodger")

# Set up asset directories
game_folder = os.path.dirname(__file__)
parent_folder = os.path.abspath(os.path.join(game_folder, ".."))
sound_folder = os.path.join(parent_folder, "sounds")

# Volume settings
bg_music_volume = 0.5
effects_volume = 0.5

# Fonts
def load_font(size):
    return pygame.font.Font(pygame.font.match_font('arial'), size)

# Load images
def create_player_image():
    ship_img = pygame.Surface((60, 60), pygame.SRCALPHA)
    # Main body
    pygame.draw.polygon(ship_img, (169, 169, 169), [(30, 0), (55, 20), (50, 50), (10, 50), (5, 20)])
    # Cockpit
    pygame.draw.polygon(ship_img, (70, 130, 180), [(30, 5), (45, 20), (30, 35), (15, 20)])
    # Left wing
    pygame.draw.polygon(ship_img, (105, 105, 105), [(5, 20), (0, 35), (10, 35)])
    # Right wing
    pygame.draw.polygon(ship_img, (105, 105, 105), [(55, 20), (60, 35), (50, 35)])
    # Engine
    pygame.draw.rect(ship_img, (255, 69, 0), (22, 50, 16, 10))
    # Add details and shading
    pygame.draw.lines(ship_img, (211, 211, 211), False, [(30, 0), (30, 60)], 2)
    pygame.draw.circle(ship_img, (192, 192, 192), (30, 30), 5)
    pygame.draw.polygon(ship_img, (160, 160, 160), [(10, 50), (50, 50), (40, 60), (20, 60)])
    return ship_img

def create_laser_images():
    laser_anim = []
    for i in range(5):
        width = 5 + i * 2
        laser_img = pygame.Surface((width, 30), pygame.SRCALPHA)
        # Draw the main beam in the center
        center_x = width // 2
        pygame.draw.rect(laser_img, (255, 0, 0), [center_x - 1, 0, 2, 30])
        # Draw outer glow
        pygame.draw.rect(laser_img, (255, 0, 0, 100), [center_x - (i + 1), 0, 2 * (i + 1), 30])
        laser_anim.append(laser_img)
    return laser_anim

def create_explosion_images():
    explosion_anim = []
    for i in range(9):
        frame = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(frame, (255, 255 - i * 28, 0), (25, 25), 25 - i * 2)
        explosion_anim.append(frame)
    return explosion_anim

def create_starfield():
    stars = []
    for _ in range(100):
        x = random.randrange(0, WIDTH)
        y = random.randrange(0, HEIGHT)
        speed = random.uniform(1, 3)
        stars.append([x, y, speed])
    return stars

# Load images
player_img = create_player_image()
laser_anim = create_laser_images()
explosion_anim = create_explosion_images()

# Starfield for dynamic background
starfield = create_starfield()

# Load sounds
try:
    pygame.mixer.music.load(os.path.join(sound_folder, "background.mp3"))
    laser_sound = pygame.mixer.Sound(os.path.join(sound_folder, "laser.mp3"))
    collision_sound = pygame.mixer.Sound(os.path.join(sound_folder, "exploding.mp3"))
    moving_sound = pygame.mixer.Sound(os.path.join(sound_folder, "moving.mp3"))
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    pygame.mixer.music = None
    laser_sound = None
    collision_sound = None
    moving_sound = None

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.speedx = 0
        self.speedy = 0
        self.speed = 5
        self.energy = 100  # Energy for shooting lasers
        self.last_move_time = 0  # For movement sound cooldown

    def update(self):
        self.speedx = 0
        self.speedy = 0
        # Get keys pressed
        keystate = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        moving = False
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -self.speed
            moving = True
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = self.speed
            moving = True
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.speedy = -self.speed
            moving = True
        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.speedy = self.speed
            moving = True
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Play moving sound with a cooldown to prevent overlap
        if moving and moving_sound and current_time - self.last_move_time > 100:
            moving_sound.set_volume(effects_volume)
            moving_sound.play()
            self.last_move_time = current_time

        # Keep within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        # Regenerate energy slowly
        if self.energy < 100:
            self.energy += 0.05  # Adjust the regeneration rate as needed

    def shoot(self):
        if self.energy >= 10:
            laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(laser)
            lasers.add(laser)
            self.energy -= 10  # Decrease energy
            if laser_sound:
                laser_sound.set_volume(effects_volume)
                laser_sound.play()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = laser_anim
        self.frame = 0
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # Adjust as needed

    def update(self):
        self.rect.y += self.speedy
        # Remove laser if it goes off screen
        if self.rect.bottom < 0:
            self.kill()
        # Animate laser
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame = (self.frame + 1) % len(self.frames)
            old_center = self.rect.center
            self.image = self.frames[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = old_center

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image_orig = self.create_asteroid_image()
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = 25
        self.spawn_position()
        self.speedx = random.uniform(-2, 2)
        self.speedy = random.uniform(-2, 2)
        self.speed_increase = speed
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

        # Ensure asteroids are moving towards the screen
        if self.speedx == 0 and self.speedy == 0:
            self.speedx = random.choice([-1, 1])
            self.speedy = random.choice([-1, 1])

    def create_asteroid_image(self):
        asteroid_img = pygame.Surface((50, 50), pygame.SRCALPHA)
        color = (random.randint(80, 120), random.randint(80, 120), random.randint(80, 120))
        pygame.draw.circle(asteroid_img, color, (25, 25), 25)
        # Add crater details
        for _ in range(random.randint(3, 7)):
            x = random.randint(5, 45)
            y = random.randint(5, 45)
            radius = random.randint(3, 6)
            crater_color = (max(color[0] - 20, 0), max(color[1] - 20, 0), max(color[2] - 20, 0))
            pygame.draw.circle(asteroid_img, crater_color, (x, y), radius)
        return asteroid_img

    def spawn_position(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        buffer = 100
        if side == 'top':
            self.rect.x = random.randrange(-buffer, WIDTH + buffer)
            self.rect.y = random.randrange(-buffer * 2, -buffer)
        elif side == 'bottom':
            self.rect.x = random.randrange(-buffer, WIDTH + buffer)
            self.rect.y = random.randrange(HEIGHT + buffer, HEIGHT + buffer * 2)
        elif side == 'left':
            self.rect.x = random.randrange(-buffer * 2, -buffer)
            self.rect.y = random.randrange(-buffer, HEIGHT + buffer)
        else:  # right
            self.rect.x = random.randrange(WIDTH + buffer, WIDTH + buffer * 2)
            self.rect.y = random.randrange(-buffer, HEIGHT + buffer)

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
        self.rect.x += self.speedx * self.speed_increase
        self.rect.y += self.speedy * self.speed_increase
        # Reset position if off screen
        if (self.rect.top > HEIGHT + 200 or self.rect.bottom < -200 or
            self.rect.left > WIDTH + 200 or self.rect.right < -200):
            self.spawn_position()
            self.speedx = random.uniform(-2, 2)
            self.speedy = random.uniform(-2, 2)
            if self.speedx == 0 and self.speedy == 0:
                self.speedx = random.choice([-1, 1])
                self.speedy = random.choice([-1, 1])
            self.image_orig = self.create_asteroid_image()
            self.image = self.image_orig.copy()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = explosion_anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # Adjust for animation speed

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Game functions
def show_menu():
    global WIDTH, HEIGHT, screen, starfield
    menu = True
    title_font = load_font(72)
    menu_font = load_font(36)
    clock = pygame.time.Clock()  # Added clock
    while menu:
        clock.tick(60)  # Limit frame rate
        screen.fill((10, 10, 30))
        draw_starfield()

        title_text = title_font.render("ASTEROID DODGER", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3))
        screen.blit(title_text, title_rect)

        play_text = menu_font.render("Press 'P' to Play", True, (200, 200, 255))
        play_rect = play_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(play_text, play_rect)

        settings_text = menu_font.render("Press 'S' for Settings", True, (200, 200, 255))
        settings_rect = settings_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        screen.blit(settings_text, settings_rect)

        quit_text = menu_font.render("Press 'Q' to Quit", True, (200, 200, 255))
        quit_rect = quit_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 100))
        screen.blit(quit_text, quit_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    menu = False
                    main_game()
                elif event.key == pygame.K_s:
                    settings_menu()
                elif event.key == pygame.K_q:
                    menu = False
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                starfield = create_starfield()

def settings_menu():
    global bg_music_volume, effects_volume, WIDTH, HEIGHT, screen, starfield
    settings = True
    title_font = load_font(72)
    menu_font = load_font(36)
    small_font = load_font(24)
    clock = pygame.time.Clock()
    slider_dragging = None  # To keep track of which slider is being dragged

    # Slider positions and dimensions
    slider_width = 300
    slider_height = 20
    bg_slider_rect = pygame.Rect((WIDTH / 2 - slider_width / 2, HEIGHT / 2 - 50), (slider_width, slider_height))
    effects_slider_rect = pygame.Rect((WIDTH / 2 - slider_width / 2, HEIGHT / 2 + 50), (slider_width, slider_height))

    while settings:
        clock.tick(60)
        screen.fill((10, 10, 30))
        draw_starfield()

        title_text = title_font.render("SETTINGS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3 - 50))
        screen.blit(title_text, title_rect)

        # Background Music Slider
        bg_text = menu_font.render("Background Music Volume", True, (255, 255, 255))
        bg_text_rect = bg_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 80))
        screen.blit(bg_text, bg_text_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_slider_rect)
        # Draw the slider handle
        bg_handle_x = bg_slider_rect.x + bg_music_volume * slider_width - 10
        bg_handle_rect = pygame.Rect(bg_handle_x, bg_slider_rect.y - 5, 20, slider_height + 10)
        pygame.draw.rect(screen, (200, 200, 200), bg_handle_rect)

        # Sound Effects Slider
        effects_text = menu_font.render("Sound Effects Volume", True, (255, 255, 255))
        effects_text_rect = effects_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20))
        screen.blit(effects_text, effects_text_rect)
        pygame.draw.rect(screen, (100, 100, 100), effects_slider_rect)
        # Draw the slider handle
        effects_handle_x = effects_slider_rect.x + effects_volume * slider_width - 10
        effects_handle_rect = pygame.Rect(effects_handle_x, effects_slider_rect.y - 5, 20, slider_height + 10)
        pygame.draw.rect(screen, (200, 200, 200), effects_handle_rect)

        # Instructions
        instructions_text = small_font.render("Press 'M' to return to Main Menu", True, (200, 200, 255))
        instructions_rect = instructions_text.get_rect(center=(WIDTH / 2, HEIGHT - 50))
        screen.blit(instructions_text, instructions_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_m:
                    settings = False
                    show_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bg_handle_rect.collidepoint(event.pos):
                    slider_dragging = 'bg'
                elif effects_handle_rect.collidepoint(event.pos):
                    slider_dragging = 'effects'
            elif event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = None
            elif event.type == pygame.MOUSEMOTION:
                if slider_dragging == 'bg':
                    # Update background music volume
                    mouse_x = event.pos[0]
                    relative_x = mouse_x - bg_slider_rect.x
                    bg_music_volume = max(0, min(relative_x / slider_width, 1))
                    if pygame.mixer.music:
                        pygame.mixer.music.set_volume(bg_music_volume)
                elif slider_dragging == 'effects':
                    # Update sound effects volume
                    mouse_x = event.pos[0]
                    relative_x = mouse_x - effects_slider_rect.x
                    effects_volume = max(0, min(relative_x / slider_width, 1))
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                starfield = create_starfield()
                # Update slider positions
                bg_slider_rect.x = WIDTH / 2 - slider_width / 2
                bg_slider_rect.y = HEIGHT / 2 - 50
                effects_slider_rect.x = WIDTH / 2 - slider_width / 2
                effects_slider_rect.y = HEIGHT / 2 + 50

def game_over_screen(score):
    global WIDTH, HEIGHT, screen, starfield
    menu = True
    title_font = load_font(72)
    menu_font = load_font(36)
    clock = pygame.time.Clock()  # Added clock
    while menu:
        clock.tick(60)  # Limit frame rate
        screen.fill((10, 10, 30))
        draw_starfield()

        game_over_text = title_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 3))
        screen.blit(game_over_text, game_over_rect)

        score_text = menu_font.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(score_text, score_rect)

        play_text = menu_font.render("Press 'P' to Play Again", True, (200, 200, 255))
        play_rect = play_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        screen.blit(play_text, play_rect)

        quit_text = menu_font.render("Press 'Q' to Quit", True, (200, 200, 255))
        quit_rect = quit_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 100))
        screen.blit(quit_text, quit_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    menu = False
                    main_game()
                elif event.key == pygame.K_q:
                    menu = False
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                starfield = create_starfield()

def draw_starfield():
    global starfield
    for star in starfield:
        pygame.draw.circle(screen, (255, 255, 255), (int(star[0]), int(star[1])), 2)
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[0] = random.randrange(0, WIDTH)
            star[1] = random.randrange(-20, -5)
            star[2] = random.uniform(1, 3)

# Main game loop
def main_game():
    global all_sprites, asteroids, lasers, WIDTH, HEIGHT, screen, starfield, bg_music_volume, effects_volume
    clock = pygame.time.Clock()
    running = True
    score = 0
    start_ticks = pygame.time.get_ticks()
    asteroid_speed = 2.5  # Increased base speed
    asteroid_spawn_interval = 2000  # Decreased initial spawn interval
    asteroid_spawn_timer = pygame.time.get_ticks()

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    # Spawn initial asteroids
    for _ in range(15):  # Increased initial asteroid count
        asteroid = Asteroid(asteroid_speed)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    # Play background music (if available)
    if pygame.mixer.music:
        pygame.mixer.music.set_volume(bg_music_volume)
        pygame.mixer.music.play(loops=-1)

    while running:
        clock.tick(60)  # 60 FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                starfield = create_starfield()

        # Update
        all_sprites.update()
        explosions.update()

        # Increase difficulty over time
        elapsed_time = pygame.time.get_ticks() - start_ticks

        # Increase asteroid speed over time
        asteroid_speed = 2.5 + (elapsed_time // 2000) * 0.1

        # Decrease asteroid spawn interval over time
        if elapsed_time // 3000 > 0:
            asteroid_spawn_interval = max(500, 2000 - (elapsed_time // 3000) * 100)

        # Spawn new asteroids at intervals
        if pygame.time.get_ticks() - asteroid_spawn_timer > asteroid_spawn_interval:
            asteroid_spawn_timer = pygame.time.get_ticks()
            asteroid = Asteroid(asteroid_speed)
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Calculate score
        score = (pygame.time.get_ticks() - start_ticks) // 100

        # Check for collisions between lasers and asteroids
        laser_hits = pygame.sprite.groupcollide(asteroids, lasers, True, True)
        for hit in laser_hits:
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if collision_sound:
                collision_sound.set_volume(effects_volume)
                collision_sound.play()
            # Optionally, increase score when destroying asteroids
            score += 50

        # Check for collisions between player and asteroids
        hits = pygame.sprite.spritecollide(player, asteroids, False, pygame.sprite.collide_circle)
        if hits:
            if collision_sound:
                collision_sound.set_volume(effects_volume)
                collision_sound.play()
            explosion = Explosion(player.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            running = False

        # Draw/render
        screen.fill((10, 10, 30))
        draw_starfield()
        all_sprites.draw(screen)
        player.draw(screen)
        explosions.draw(screen)

        # Draw energy bar
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 30, 10, 20, 100), 2)
        energy_height = int(player.energy)
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH - 28, 110 - energy_height, 16, energy_height))

        # Draw score
        score_font = load_font(24)
        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    # Wait for explosion animation to finish
    while len(explosions) > 0:
        clock.tick(60)
        explosions.update()
        screen.fill((10, 10, 30))
        draw_starfield()
        explosions.draw(screen)
        pygame.display.flip()

    # Stop music when game is over
    if pygame.mixer.music:
        pygame.mixer.music.stop()
    game_over_screen(score)

if __name__ == "__main__":
    show_menu()
