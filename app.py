import pygame
import sys
import random
import math
import time

# Initialize Pygame

pygame.init()

pygame.mixer.init()

# Load the background music
#pygame.mixer.music.load("unity.mp3")
#pygame.mixer.music.play(-1)  # Loop the music indefinitely

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_SIZE = 20
PLAYER_COLOR = (0, 255, 0)
RECTANGLE_COLOR = (255, 0, 0)
FONT = pygame.font.SysFont(None, 40)
speed = 10
spawn_timer = 0
speed_increase_timer = 0
initial_spawn_rate = 0.02
spawn_rate_increase = 0.0005
initial_speed = 2
speed_increase = 0.01
lives = 3
boss_attack_speed = -10
coins = 0
coin_cost = 100
base_lives_amount = 3
mod1 = 0
mod2 = 0
win = False
mode = "easy"
luck_cost = 500
luck = 1

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Escape")

# Function to launch larger lasers in a circle around the boss for the second attack
def boss_second_attack(boss, boss_lasers):
    num_lasers = 20  # Increase number of lasers for a larger attack
    angle_step = 360 / num_lasers
    for i in range(num_lasers):
        angle = math.radians(i * angle_step)
        laser_x = boss.centerx + int(math.cos(angle) * (boss.width))
        laser_y = boss.centery + int(math.sin(angle) * (boss.height))
        laser = pygame.Rect(laser_x - 2, laser_y - 2, 4, 4)
        boss_lasers.append(laser)

# Function to launch triple lasers for the third attack
def boss_third_attack(boss, boss_lasers):
    num_lasers = 3  # Number of lasers for the triple attack
    for i in range(num_lasers):
        laser_x = boss.centerx - 2 + (i - 1) * (boss.width // 2)
        laser_y = boss.bottom
        laser = pygame.Rect(laser_x, laser_y, 4, HEIGHT - boss.bottom)
        boss_lasers.append(laser)


# Function to calculate distance between two points
def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to create a random rectangle
def create_rectangle(player_rect):
    size = random.randint(20, 50)
    while True:
        x = random.randint(0, WIDTH - size)
        y = random.randint(0, HEIGHT - size)
        if distance((x + size // 2, y + size // 2), (player_rect.x + PLAYER_SIZE // 2, player_rect.y + PLAYER_SIZE // 2)) > 100:
            break
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    speed_x = random.uniform(-3, 3)  # Random horizontal speed
    speed_y = random.uniform(-3, 3)  # Random vertical speed
    return pygame.Rect(x, y, size, size), color, speed_x, speed_y

# Function to update the rectangles
def update_rectangles(rectangles):
    for i in range(len(rectangles) - 1, -1, -1):
        rect, color, speed_x, speed_y = rectangles[i]
        rect.x += speed_x
        rect.y += speed_y

        # Remove rectangles that are out of bounds
        if rect.left > WIDTH or rect.right < 0 or rect.top > HEIGHT or rect.bottom < 0:
            rectangles.pop(i)
        else:
            pygame.draw.rect(screen, color, rect)

# Function to update the player
def update_player(player_rect):
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

# Function to check collision
def check_collision(player_rect, rectangles):
    for rect, _, _, _ in rectangles:
        if player_rect.colliderect(rect):
            return True
    return False

# Function to clear all rectangles
def clear_rectangles(rectangles):
    rectangles.clear()

# Main game loop
def game():
    global speed, spawn_timer, speed_increase_timer, initial_spawn_rate, spawn_rate_increase, initial_speed, speed_increase, lives, highest_score, boss_attack_speed, coins, coin_cost, base_lives_amount, PLAYER_COLOR, mode, luck_cost, luck
    restart_mode = False
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT // 2 - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
    clock = pygame.time.Clock()
    score = 0
    highest_score = 0
    rectangles = []
    power_up_triangle = None  # Power-up triangle
    power_up_circle = None  # Power-up circle
    power_up_heart = None  # Power-up heart
    power_up_purple = None  # Power-up purple
    ultra_power_up_circle = None # Ultra-Power-up circle
    power_up_flash_timer = 0  # Timer for power-up flashing
    power_up_flash_interval = 20  # Power-up flash interval (frames)
    invincibility_timer = 0  # Timer for invincibility
    invincibility_duration = 180  # 3 seconds (60 frames per second * 3)
    speed_multiplier = 1  # Speed multiplier for player and rectangles
    clear_rectangles_chance = 0.002  # Chance of clearing 75% of rectangles (adjust as needed)
    paused = False
    boss_spawn_score = 10000
    boss = None
    boss_hp = 10
    boss_lasers = []
    boss_laser_cooldown = 0
    boss_speed_increase = 5
    green_diamonds = []
    green_diamond_spawn_timer = 0
    boss_spawned = False
    running = True
    screen.fill(WHITE)
    PLAYER_COLOR = (0, 255, 0)
    mod1 = 0
    mod2 = 0
    win = False
    completed = False
    speed_multiplier = 1  # Reset speed multiplier
    mode = "easy"
    luck_cost = 500
        
    pygame.display.flip()
    while running:
        # Game setup
        if not paused:
            main_attacks_counter = 0  # Counter for tracking main attacks by boss
            third_attack_counter = 0  # Counter for tracking main attacks specifically for the third attack
            second_attack_cooldown = 0  # Cooldown for the second attack
            third_attack_cooldown = 0  # Cooldown for the third attack
            lives = base_lives_amount
            score = 0
            rectangles.clear()
            power_up_triangle = None
            power_up_circle = None
            power_up_heart = None
            power_up_purple = None
            ultra_power_up_circle = None
            power_up_flash_timer = 0
            invincibility_timer = 0
            spawn_timer = initial_spawn_rate  # Reset spawn rate
            boss_spawned = False
            boss_hp = 10
            boss_lasers.clear()
            green_diamonds.clear()
            PLAYER_COLOR = (0, 255, 0)
            mod1 = 0
            mod2 = 0
            win = False
            completed = False

        while lives > 0:
            if mode == "easy":
                if win:
                    coins += 10000
                    game_win = True
                    while game_win:
                        screen.fill(BLACK)
                        value = FONT.render("You Won! Press Q-Quit, C-Play Again, P-Continue", True, WHITE)
                        screen.blit(value, [WIDTH // 2 - value.get_width() // 2, HEIGHT // 2])
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_q:
                                    pygame.quit()
                                    sys.exit
                                if event.key == pygame.K_c:
                                    game_win = False
                                    win = False
                                    lives = 0
                                if event.key == pygame.K_p:
                                    game_win = False
                                    win = False
                                    completed = True
                                    boss_hp = 1

                PLAYER_COLOR = (mod1, 255, mod2)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            paused = not paused
                        if event.key == pygame.K_q:
                            lives = 0
                        if event.key == pygame.K_r:
                            restart_mode = False
                            time.sleep(0.25)

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and player_rect.left > 0:
                    player_rect.x -= 5 * speed_multiplier
                if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
                    player_rect.x += 5 * speed_multiplier
                if keys[pygame.K_UP] and player_rect.top > 0:
                    player_rect.y -= 5 * speed_multiplier
                if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
                    player_rect.y += 5 * speed_multiplier

                screen.fill(BLACK)

                # Create new rectangles periodically
                if random.random() < spawn_timer and len(rectangles) < 100:
                    rectangles.append(create_rectangle(player_rect))

                # Spawn power-ups randomly
                if power_up_triangle is None and random.random() < 0.5 + luck / 10:  # Adjust probability as needed
                    power_up_triangle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_circle is None and random.random() < 0.01 + luck / 50:  # Adjust probability as needed
                    power_up_circle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_heart is None and random.random() < 0.005 + luck / 100:  # Lower probability for heart power-up
                    power_up_heart = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_purple is None and random.random() < 0.001 + luck / 500:  # Adjust probability as needed for rarity
                    power_up_purple = pygame.Rect(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40), 40, 40)
                if ultra_power_up_circle is None and random.random() < 0.0005 + luck / 1000:
                    ultra_power_up_circle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 30, 30)

                # Draw and check collision with power-up triangle
                if power_up_triangle:
                    pygame.draw.polygon(screen, (255, 255, 0), [(power_up_triangle.left, power_up_triangle.bottom), (power_up_triangle.centerx, power_up_triangle.top), (power_up_triangle.right, power_up_triangle.bottom)])  # Draw triangle for power-up
                    if player_rect.colliderect(power_up_triangle):
                        power_up_triangle = None
                        spawn_timer *= 0.9  # Decrease spawn rate by 10%

                # Draw and check collision with power-up circle
                if power_up_circle:
                    pygame.draw.circle(screen, (0, 255, 0), power_up_circle.center, power_up_circle.width // 2)  # Draw circle for power-up
                    if player_rect.colliderect(power_up_circle):
                        power_up_circle = None
                        clear_rectangles(rectangles)  # Clear all rectangles

                # Draw and check collision with power-up heart
                if power_up_heart:
                    pygame.draw.polygon(screen, (255, 0, 0), [(power_up_heart.left + 10, power_up_heart.top + 5), (power_up_heart.left, power_up_heart.top + 10), (power_up_heart.left + 10, power_up_heart.bottom), (power_up_heart.centerx, power_up_heart.bottom - 5), (power_up_heart.right - 10, power_up_heart.bottom), (power_up_heart.right, power_up_heart.top + 10), (power_up_heart.right - 10, power_up_heart.top + 5)])  # Draw heart for power-up
                    if player_rect.colliderect(power_up_heart):
                        power_up_heart = None
                        lives += 1  # Add 1 life

                # Draw and check collision with power-up purple
                if power_up_purple:
                    pygame.draw.polygon(screen, (128, 0, 128), [(power_up_purple.centerx, power_up_purple.top), (power_up_purple.right, power_up_purple.centery), (power_up_purple.centerx, power_up_purple.bottom), (power_up_purple.left, power_up_purple.centery)])  # Draw diamond for power-up
                    if player_rect.colliderect(power_up_purple):
                        power_up_purple = None
                        clear_rectangles(rectangles)  # Destroy all rectangles
                        lives += 5  # Add 5 lives
                        spawn_rate_increase *= 0.5  # Decrease spawn rate increase by 50%
                        invincibility_timer = invincibility_duration  # Activate invincibility

                # Draw and check collision with ultra power-up circle
                if ultra_power_up_circle:
                    pygame.draw.circle(screen, (255, 255, 255), ultra_power_up_circle.center, ultra_power_up_circle.width // 2)  # Draw circle for power-up
                    if player_rect.colliderect(ultra_power_up_circle):
                        ultra_power_up_circle = None
                        if mod1 < 205:
                            mod1 += 50
                        else:
                            mod1 = 255
                            if mod2 < 205:
                                mod2 += 50
                            else:
                                if not completed:
                                    mod2 = 255
                                    lives += 3
                                    win = True
                                else:
                                    lives += 6

                        score += 5000
                        coins += 1000
                        lives += 3
                        invincibility_timer = invincibility_duration
                        clear_rectangles(rectangles)
                        spawn_timer *= 0.1
                        spawn_rate_increase *= 0.025

                        

                # Toggle power-up color (flash effect)
                if power_up_flash_timer >= power_up_flash_interval:
                    power_up_flash_timer = 0
                else:
                    power_up_flash_timer += 1

                # Increase spawn rate over time
                spawn_timer += spawn_rate_increase

                # Increase speed over time
                if speed_increase_timer >= 300:  # Increase speed every 300 frames (5 seconds at 60 FPS)
                    speed += speed_increase
                    speed_increase_timer = 0
                    
                if random.random() < initial_spawn_rate and len(rectangles) < 100:
                    rectangles.append(create_rectangle(player_rect))

                # Check for invincibility
                if invincibility_timer > 0:
                    invincibility_timer -= 1
                    # Blink player rectangle when invincible
                    if invincibility_timer % 10 < 5:  # Blink every 5 frames
                        update_player(player_rect)
                else:
                    update_player(player_rect)

                update_rectangles(rectangles)

                if check_collision(player_rect, rectangles):
                    if invincibility_timer <= 0:  # Only decrease lives if not invincible
                        lives -= 1
                        if lives > 0:
                            # Activate invincibility
                            invincibility_timer = invincibility_duration
                        else:
                            if score > highest_score:
                                highest_score = score
                            break  # Exit the loop when lives run out

                # Periodically clear 90% of rectangles
                if random.random() < clear_rectangles_chance:
                    num_rectangles_to_clear = int(len(rectangles) * 0.90)
                    random.shuffle(rectangles)
                    for i in range(num_rectangles_to_clear):
                        rectangles.pop()

                # Increase score
                if not boss:
                    score += 1

                    # Display score
                    score_text = FONT.render(f"Score: {score}", True, WHITE)
                    screen.blit(score_text, (10, 10))
                else:
                    green_diamond_amount = FONT.render(f"Boss Hp: {boss_hp}", True, WHITE)
                    screen.blit(green_diamond_amount, (10, 10))
                
                coins += 1
                
                if score % 3 == 0 and not boss:
                    coins -= 2

                if score % 10000 == 0:
                    spawn_timer += score / 1000000
                
                coin_text = FONT.render(f"Coins: {coins}", True, WHITE)
                screen.blit(coin_text, (10, 50))

                # Display highest score
                highest_score_text = FONT.render(f"High Score: {highest_score}", True, WHITE)
                screen.blit(highest_score_text, (WIDTH - highest_score_text.get_width() - 10, 10))

                mode_text = FONT.render(f"Mode:  {mode}", True, WHITE)
                screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 90))

                # Display lives counter
                lives_text = FONT.render(f"Lives: {lives}", True, WHITE)
                screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 50))

                # Display pause message
                if paused:
                    while paused:
                        pause_text = FONT.render("Paused", True, WHITE)
                        screen.blit(pause_text, (WIDTH / 2 - pause_text.get_width() / 2, HEIGHT / 2 - pause_text.get_height() / 2))
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    paused = not paused
                        pygame.display.flip()

                pygame.display.flip()
                clock.tick(60)
                speed_increase_timer += 1
            elif mode == "normal":
                if win:
                    coins += 100000
                    game_win = True
                    while game_win:
                        screen.fill(BLACK)
                        value = FONT.render("You Won! Press Q-Quit, C-Play Again, P-Continue", True, WHITE)
                        screen.blit(value, [WIDTH // 2 - value.get_width() // 2, HEIGHT // 2])
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_q:
                                    pygame.quit()
                                    sys.exit
                                if event.key == pygame.K_c:
                                    game_win = False
                                    win = False
                                    lives = 0
                                    highest_score = score
                                if event.key == pygame.K_p:
                                    game_win = False
                                    win = False
                                    completed = True
                                    boss_hp = 1

                PLAYER_COLOR = (mod1, 255, mod2)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            paused = not paused
                        if event.key == pygame.K_q:
                            lives = 0
                            highest_score = score
                        if event.key == pygame.K_r:
                            restart_mode = False
                            time.sleep(0.25)

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and player_rect.left > 0:
                    player_rect.x -= 5 * speed_multiplier
                if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
                    player_rect.x += 5 * speed_multiplier
                if keys[pygame.K_UP] and player_rect.top > 0:
                    player_rect.y -= 5 * speed_multiplier
                if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
                    player_rect.y += 5 * speed_multiplier

                screen.fill(BLACK)

                # Create new rectangles periodically
                if random.random() < spawn_timer and len(rectangles) < 100:
                    rectangles.append(create_rectangle(player_rect))

                # Spawn power-ups randomly
                if power_up_triangle is None and random.random() < 0.05 + luck / 100:  # Adjust probability as needed
                    power_up_triangle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_circle is None and random.random() < 0.001 + luck / 500:  # Adjust probability as needed
                    power_up_circle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_heart is None and random.random() < 0.0005 + luck / 1000:  # Lower probability for heart power-up
                    power_up_heart = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_purple is None and random.random() < 0.0001 + luck / 5000:  # Adjust probability as needed for rarity
                    power_up_purple = pygame.Rect(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40), 40, 40)
                if ultra_power_up_circle is None and random.random() < 0.0001 + luck / 5000:
                    ultra_power_up_circle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 30, 30)

                # Draw and check collision with power-up triangle
                if power_up_triangle:
                    pygame.draw.polygon(screen, (255, 255, 0), [(power_up_triangle.left, power_up_triangle.bottom), (power_up_triangle.centerx, power_up_triangle.top), (power_up_triangle.right, power_up_triangle.bottom)])  # Draw triangle for power-up
                    if player_rect.colliderect(power_up_triangle):
                        power_up_triangle = None
                        spawn_timer *= 0.5  # Decrease spawn rate by 50%

                # Draw and check collision with power-up circle
                if power_up_circle:
                    pygame.draw.circle(screen, (0, 255, 0), power_up_circle.center, power_up_circle.width // 2)  # Draw circle for power-up
                    if player_rect.colliderect(power_up_circle):
                        power_up_circle = None
                        clear_rectangles(rectangles)  # Clear all rectangles

                # Draw and check collision with power-up heart
                if power_up_heart:
                    pygame.draw.polygon(screen, (255, 0, 0), [(power_up_heart.left + 10, power_up_heart.top + 5), (power_up_heart.left, power_up_heart.top + 10), (power_up_heart.left + 10, power_up_heart.bottom), (power_up_heart.centerx, power_up_heart.bottom - 5), (power_up_heart.right - 10, power_up_heart.bottom), (power_up_heart.right, power_up_heart.top + 10), (power_up_heart.right - 10, power_up_heart.top + 5)])  # Draw heart for power-up
                    if player_rect.colliderect(power_up_heart):
                        power_up_heart = None
                        lives += 1  # Add 1 life

                # Draw and check collision with power-up purple
                if power_up_purple:
                    pygame.draw.polygon(screen, (128, 0, 128), [(power_up_purple.centerx, power_up_purple.top), (power_up_purple.right, power_up_purple.centery), (power_up_purple.centerx, power_up_purple.bottom), (power_up_purple.left, power_up_purple.centery)])  # Draw diamond for power-up
                    if player_rect.colliderect(power_up_purple):
                        power_up_purple = None
                        clear_rectangles(rectangles)  # Destroy all rectangles
                        lives += 10  # Add 10 lives
                        spawn_rate_increase *= 0.1  # Decrease spawn rate increase by 90%
                        invincibility_timer = invincibility_duration  # Activate invincibility

                # Draw and check collision with ultra power-up circle
                if ultra_power_up_circle:
                    pygame.draw.circle(screen, (255, 255, 255), ultra_power_up_circle.center, ultra_power_up_circle.width // 2)  # Draw circle for power-up
                    if player_rect.colliderect(ultra_power_up_circle):
                        ultra_power_up_circle = None
                        if mod1 < 205:
                            mod1 += 50
                        else:
                            mod1 = 255
                            if mod2 < 205:
                                mod2 += 50
                            else:
                                if not completed:
                                    mod2 = 255
                                    lives += 3
                                    win = True
                                else:
                                    lives += 6

                        score += 5000
                        coins += 5000
                        lives += 3
                        invincibility_timer = invincibility_duration
                        clear_rectangles(rectangles)
                        spawn_timer *= 0.1
                        spawn_rate_increase *= 0.025

                        

                # Toggle power-up color (flash effect)
                if power_up_flash_timer >= power_up_flash_interval:
                    power_up_flash_timer = 0
                else:
                    power_up_flash_timer += 1

                # Increase spawn rate over time
                spawn_rate_increase += score / 1000000000
                spawn_timer += spawn_rate_increase

                # Increase speed over time
                if speed_increase_timer >= 300:  # Increase speed every 300 frames (5 seconds at 60 FPS)
                    speed += speed_increase
                    speed_increase_timer = 0

                if not boss_spawned:
                    # Create new rectangle
                    if random.random() < initial_spawn_rate and len(rectangles) < 100:
                        rectangles.append(create_rectangle(player_rect))

                # Check for invincibility
                if invincibility_timer > 0:
                    invincibility_timer -= 1
                    # Blink player rectangle when invincible
                    if invincibility_timer % 10 < 5:  # Blink every 5 frames
                        update_player(player_rect)
                else:
                    update_player(player_rect)

                if not boss_spawned:
                    update_rectangles(rectangles)

                # Check collision with boss and launch lasers
                if boss and not paused:
                    if player_rect.colliderect(boss) and invincibility_timer <= 0:
                        lives -= 1
                        if lives > 0:
                            invincibility_timer = invincibility_duration / 2
                        else:
                            if score > highest_score:
                                highest_score = score
                            break
                    if boss_laser_cooldown <= 0:
                        # Track main attacks for boss's second and third attacks
                        main_attacks_counter += 1
                        third_attack_counter += 1
                        if main_attacks_counter == max(1, score * 3 / 10000) and second_attack_cooldown <= 0:  # Second attack after every 3 main attacks
                            boss_second_attack(boss, boss_lasers)
                            second_attack_cooldown = 120  # Cooldown of 2 seconds (60 frames per second * 2)
                            main_attacks_counter = 0  # Reset main attacks counter
                        if third_attack_counter == max(2, score / 2000) and third_attack_cooldown <= 0:  # Third attack after every 5 main attacks
                            boss_third_attack(boss, boss_lasers)
                            third_attack_cooldown = 180  # Cooldown of 3 seconds (60 frames per second * 3)
                            third_attack_counter = 0  # Reset third attack counter

                        # Decrement cooldowns
                        if second_attack_cooldown > 0:
                            second_attack_cooldown -= 1
                        if third_attack_cooldown > 0:
                            third_attack_cooldown -= 1
                        boss_laser_cooldown = 60 - (boss_attack_speed)
                        boss_lasers.append(pygame.Rect(boss.centerx - 2, boss.bottom, 4, HEIGHT - boss.bottom))
                    else:
                        boss_laser_cooldown -= 1
                    for laser in boss_lasers:
                        laser.y += max(0.25, 50000/score)  # Adjust laser speed
                        pygame.draw.rect(screen, (255, 0, 0), laser)
                        if laser.colliderect(player_rect) and invincibility_timer <= 0:
                            lives -= score / 10000
                            if lives > 0:
                                invincibility_timer = invincibility_duration
                            else:
                                if score > highest_score:
                                    highest_score = score
                                break
                    boss_movement = math.sin(pygame.time.get_ticks() * 0.001) * 5  # Adjust boss movement pattern
                    boss.x += boss_movement

                    # Draw boss
                    pygame.draw.circle(screen, (255, 0, 0), boss.center, boss.width // 2)

                if score >= boss_spawn_score and not boss_spawned:
                    # Increase boss's attack speed with each new boss spawn
                    boss_attack_speed += boss_speed_increase

                    boss_spawned = True
                    boss = pygame.Rect(WIDTH // 2 - 20, -40, 40, 40)
                    boss_hp = round(8 + score / 5000)  # Reset boss HP
                    boss_lasers.clear()  # Clear boss lasers

                if boss_spawned:
                    clear_rectangles(rectangles)
                    if boss.y < 40:
                        boss.y += 1  # Adjust boss spawn speed
                    else:
                        pygame.draw.circle(screen, (255, 0, 0), boss.center, boss.width // 2)

                # Spawn green diamonds to defeat boss
                if score >= boss_spawn_score and len(green_diamonds) < boss_hp:
                    if green_diamond_spawn_timer <= 0:
                        green_diamond_spawn_timer = 180  # Spawn every 3 seconds (60 frames per second * 3)
                        diamond = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                        green_diamonds.append(diamond)
                    else:
                        green_diamond_spawn_timer -= 1

                for diamond in green_diamonds:
                    pygame.draw.rect(screen, (0, 255, 0), diamond)
                    if player_rect.colliderect(diamond):
                        green_diamonds.remove(diamond)
                        if boss and boss_spawned:
                            boss_hp -= 1
                            if boss_hp <= 0:
                                boss = None
                                boss_spawned = False

                if check_collision(player_rect, rectangles):
                    if invincibility_timer <= 0:  # Only decrease lives if not invincible
                        lives -= 1
                        if lives > 0:
                            # Activate invincibility
                            invincibility_timer = invincibility_duration
                        else:
                            if score > highest_score:
                                highest_score = score
                            break  # Exit the loop when lives run out

                # Periodically clear 90% of rectangles
                if random.random() < clear_rectangles_chance:
                    num_rectangles_to_clear = int(len(rectangles) * 0.90)
                    random.shuffle(rectangles)
                    for i in range(num_rectangles_to_clear):
                        rectangles.pop()

                # Increase score
                if not boss:
                    score += 1

                    # Display score
                    score_text = FONT.render(f"Score: {score}", True, WHITE)
                    screen.blit(score_text, (10, 10))
                else:
                    green_diamond_amount = FONT.render(f"Boss Hp: {boss_hp}", True, WHITE)
                    screen.blit(green_diamond_amount, (10, 10))
                
                coins += 1
                
                if score % 2 == 0 and not boss:
                    coins -= 1

                if score % 10000 == 0:
                    spawn_timer += score / 1000000
                
                coin_text = FONT.render(f"Coins: {coins}", True, WHITE)
                screen.blit(coin_text, (10, 50))

                # Display highest score
                highest_score_text = FONT.render(f"High Score: {highest_score}", True, WHITE)
                screen.blit(highest_score_text, (WIDTH - highest_score_text.get_width() - 10, 10))

                mode_text = FONT.render(f"Mode:  {mode}", True, WHITE)
                screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 90))

                # Display lives counter
                lives_text = FONT.render(f"Lives: {lives}", True, WHITE)
                screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 50))

                # Display pause message
                if paused:
                    while paused:
                        pause_text = FONT.render("Paused", True, WHITE)
                        screen.blit(pause_text, (WIDTH / 2 - pause_text.get_width() / 2, HEIGHT / 2 - pause_text.get_height() / 2))
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    paused = not paused
                        pygame.display.flip()

                pygame.display.flip()
                clock.tick(60)
                speed_increase_timer += 1
            elif mode == "hard":  
                if win:
                    coins += 1000000
                    game_win = True
                    while game_win:
                        screen.fill(BLACK)
                        value = FONT.render("You Won! Press Q-Quit, C-Play Again, P-Continue", True, WHITE)
                        screen.blit(value, [WIDTH // 2 - value.get_width() // 2, HEIGHT // 2])
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_q:
                                    pygame.quit()
                                    sys.exit
                                if event.key == pygame.K_c:
                                    game_win = False
                                    win = False
                                    lives = 0
                                if event.key == pygame.K_p:
                                    game_win = False
                                    win = False
                                    completed = True
                                    boss_hp = 1

                PLAYER_COLOR = (mod1, 255, mod2)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            paused = not paused
                        if event.key == pygame.K_q:
                            lives = 0
                        if event.key == pygame.K_r:
                            restart_mode = False
                            time.sleep(0.25)

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and player_rect.left > 0:
                    player_rect.x -= 7.5 * speed_multiplier
                if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
                    player_rect.x += 7.5 * speed_multiplier
                if keys[pygame.K_UP] and player_rect.top > 0:
                    player_rect.y -= 7.5 * speed_multiplier
                if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
                    player_rect.y += 7.5 * speed_multiplier

                screen.fill(BLACK)

                # Create new rectangles periodically
                if random.random() < spawn_timer and len(rectangles) < 100:
                    rectangles.append(create_rectangle(player_rect))

                # Spawn power-ups randomly
                if power_up_triangle is None and random.random() < 0.005 + luck / 1000:  # Adjust probability as needed
                    power_up_triangle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_circle is None and random.random() < 0.0001 + luck / 5000:  # Adjust probability as needed
                    power_up_circle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_heart is None and random.random() < 0.0005 + luck / 10000:  # Lower probability for heart power-up
                    power_up_heart = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                if power_up_purple is None and random.random() < 0.00001 + + luck / 50000:  # Adjust probability as needed for rarity
                    power_up_purple = pygame.Rect(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40), 40, 40)
                if ultra_power_up_circle is None and random.random() < 0.00005 + luck / 100000:
                    ultra_power_up_circle = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 30, 30)

                # Draw and check collision with power-up triangle
                if power_up_triangle:
                    pygame.draw.polygon(screen, (255, 255, 0), [(power_up_triangle.left, power_up_triangle.bottom), (power_up_triangle.centerx, power_up_triangle.top), (power_up_triangle.right, power_up_triangle.bottom)])  # Draw triangle for power-up
                    if player_rect.colliderect(power_up_triangle):
                        power_up_triangle = None
                        spawn_timer *= 0.5  # Decrease spawn rate by 50%

                # Draw and check collision with power-up circle
                if power_up_circle:
                    pygame.draw.circle(screen, (0, 255, 0), power_up_circle.center, power_up_circle.width // 2)  # Draw circle for power-up
                    if player_rect.colliderect(power_up_circle):
                        power_up_circle = None
                        clear_rectangles(rectangles)  # Clear all rectangles

                # Draw and check collision with power-up heart
                if power_up_heart:
                    pygame.draw.polygon(screen, (255, 0, 0), [(power_up_heart.left + 10, power_up_heart.top + 5), (power_up_heart.left, power_up_heart.top + 10), (power_up_heart.left + 10, power_up_heart.bottom), (power_up_heart.centerx, power_up_heart.bottom - 5), (power_up_heart.right - 10, power_up_heart.bottom), (power_up_heart.right, power_up_heart.top + 10), (power_up_heart.right - 10, power_up_heart.top + 5)])  # Draw heart for power-up
                    if player_rect.colliderect(power_up_heart):
                        power_up_heart = None
                        lives += 3  # Add 3 lives

                # Draw and check collision with power-up purple
                if power_up_purple:
                    pygame.draw.polygon(screen, (128, 0, 128), [(power_up_purple.centerx, power_up_purple.top), (power_up_purple.right, power_up_purple.centery), (power_up_purple.centerx, power_up_purple.bottom), (power_up_purple.left, power_up_purple.centery)])  # Draw diamond for power-up
                    if player_rect.colliderect(power_up_purple):
                        power_up_purple = None
                        clear_rectangles(rectangles)  # Destroy all rectangles
                        lives += 5  # Add 5 lives
                        spawn_rate_increase *= 0.5  # Decrease spawn rate increase by 50%
                        invincibility_timer = invincibility_duration  # Activate invincibility

                # Draw and check collision with ultra power-up circle
                if ultra_power_up_circle:
                    pygame.draw.circle(screen, (255, 255, 255), ultra_power_up_circle.center, ultra_power_up_circle.width // 2)  # Draw circle for power-up
                    if player_rect.colliderect(ultra_power_up_circle):
                        ultra_power_up_circle = None
                        if mod1 < 205:
                            mod1 += 50
                        else:
                            mod1 = 255
                            if mod2 < 205:
                                mod2 += 50
                            else:
                                if not completed:
                                    mod2 = 255
                                    lives += 3
                                    win = True
                                else:
                                    lives += 6

                        score += 5000
                        coins += 10000
                        lives += 3
                        invincibility_timer = invincibility_duration
                        clear_rectangles(rectangles)
                        spawn_timer *= 0.1
                        spawn_rate_increase *= 0.1

                        

                # Toggle power-up color (flash effect)
                if power_up_flash_timer >= power_up_flash_interval:
                    power_up_flash_timer = 0
                else:
                    power_up_flash_timer += 1

                # Increase spawn rate over time
                spawn_rate_increase += score / 100000000
                spawn_timer += spawn_rate_increase

                # Increase speed over time
                if speed_increase_timer >= 300:  # Increase speed every 300 frames (5 seconds at 60 FPS)
                    speed += speed_increase
                    speed_increase_timer = 0

                if not boss_spawned:
                    # Create new rectangle
                    if random.random() < initial_spawn_rate and len(rectangles) < 100:
                        rectangles.append(create_rectangle(player_rect))

                # Check for invincibility
                if invincibility_timer > 0:
                    invincibility_timer -= 1
                    # Blink player rectangle when invincible
                    if invincibility_timer % 10 < 5:  # Blink every 5 frames
                        update_player(player_rect)
                else:
                    update_player(player_rect)

                if not boss_spawned:
                    update_rectangles(rectangles)

                # Check collision with boss and launch lasers
                if boss and not paused:
                    if player_rect.colliderect(boss) and invincibility_timer <= 0:
                        lives -= 100
                        if lives > 0:
                            invincibility_timer = invincibility_duration / 2
                        else:
                            if score > highest_score:
                                highest_score = score
                            break
                    if boss_laser_cooldown <= 0:
                        # Track main attacks for boss's second and third attacks
                        main_attacks_counter += 1
                        third_attack_counter += 1
                        if main_attacks_counter == max(1, score * 3 / 10000) and second_attack_cooldown <= 0:  # Second attack after every 3 main attacks
                            boss_second_attack(boss, boss_lasers)
                            second_attack_cooldown = 120  # Cooldown of 2 seconds (60 frames per second * 2)
                            main_attacks_counter = 0  # Reset main attacks counter
                        if third_attack_counter == max(2, score / 2000) and third_attack_cooldown <= 0:  # Third attack after every 5 main attacks
                            boss_third_attack(boss, boss_lasers)
                            third_attack_cooldown = 180  # Cooldown of 3 seconds (60 frames per second * 3)
                            third_attack_counter = 0  # Reset third attack counter

                        # Decrement cooldowns
                        if second_attack_cooldown > 0:
                            second_attack_cooldown -= 1
                        if third_attack_cooldown > 0:
                            third_attack_cooldown -= 1
                        boss_laser_cooldown = 60 - (boss_attack_speed)
                        boss_lasers.append(pygame.Rect(boss.centerx - 2, boss.bottom, 4, HEIGHT - boss.bottom))
                    else:
                        boss_laser_cooldown -= 1
                    for laser in boss_lasers:
                        laser.y += max(0.25, 100000/score)  # Adjust laser speed
                        pygame.draw.rect(screen, (255, 0, 0), laser)
                        if laser.colliderect(player_rect) and invincibility_timer <= 0:
                            lives -= score / 5000
                            if lives > 0:
                                invincibility_timer = invincibility_duration
                            else:
                                if score > highest_score:
                                    highest_score = score
                                break
                    boss_movement = math.sin(pygame.time.get_ticks() * 0.001) * 5  # Adjust boss movement pattern
                    boss.x += boss_movement

                    # Draw boss
                    pygame.draw.circle(screen, (255, 0, 0), boss.center, boss.width // 2)

                if score >= boss_spawn_score and not boss_spawned:
                    # Increase boss's attack speed with each new boss spawn
                    boss_attack_speed += boss_speed_increase

                    boss_spawned = True
                    boss = pygame.Rect(WIDTH // 2 - 20, -40, 40, 40)
                    boss_hp = round(8 + score / 5000)  # Reset boss HP
                    boss_lasers.clear()  # Clear boss lasers

                if boss_spawned:
                    clear_rectangles(rectangles)
                    if boss.y < 40:
                        boss.y += 5  # Adjust boss spawn speed
                    else:
                        pygame.draw.circle(screen, (255, 0, 0), boss.center, boss.width // 2)

                # Spawn green diamonds to defeat boss
                if score >= boss_spawn_score and len(green_diamonds) < boss_hp:
                    if green_diamond_spawn_timer <= 0:
                        green_diamond_spawn_timer = 180  # Spawn every 3 seconds (60 frames per second * 3)
                        diamond = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
                        green_diamonds.append(diamond)
                    else:
                        green_diamond_spawn_timer -= 1

                for diamond in green_diamonds:
                    pygame.draw.rect(screen, (0, 255, 0), diamond)
                    if player_rect.colliderect(diamond):
                        green_diamonds.remove(diamond)
                        if boss and boss_spawned:
                            boss_hp -= 1
                            if boss_hp <= 0:
                                boss = None
                                boss_spawned = False

                if check_collision(player_rect, rectangles):
                    if invincibility_timer <= 0:  # Only decrease lives if not invincible
                        lives -= 1
                        if lives > 0:
                            # Activate invincibility
                            invincibility_timer = invincibility_duration
                        else:
                            if score > highest_score:
                                highest_score = score
                            break  # Exit the loop when lives run out

                # Periodically clear 90% of rectangles
                if random.random() < clear_rectangles_chance:
                    num_rectangles_to_clear = int(len(rectangles) * 0.90)
                    random.shuffle(rectangles)
                    for i in range(num_rectangles_to_clear):
                        rectangles.pop()

                # Increase score
                if not boss:
                    score += 1

                    # Display score
                    score_text = FONT.render(f"Score: {score}", True, WHITE)
                    screen.blit(score_text, (10, 10))
                else:
                    green_diamond_amount = FONT.render(f"Boss Hp: {boss_hp}", True, WHITE)
                    screen.blit(green_diamond_amount, (10, 10))
                
                coins += 2
                
                if score % 10 == 0 and not boss:
                    coins -= 1

                if score % 10000 == 0:
                    spawn_timer += score / 1000000
                
                coin_text = FONT.render(f"Coins: {coins}", True, WHITE)
                screen.blit(coin_text, (10, 50))

                # Display highest score
                highest_score_text = FONT.render(f"High Score: {highest_score}", True, WHITE)
                screen.blit(highest_score_text, (WIDTH - highest_score_text.get_width() - 10, 10))

                mode_text = FONT.render(f"Mode:  {mode}", True, WHITE)
                screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 90))

                # Display lives counter
                lives_text = FONT.render(f"Lives: {lives}", True, WHITE)
                screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 50))

                # Display pause message
                if paused:
                    while paused:
                        pause_text = FONT.render("Paused", True, WHITE)
                        screen.blit(pause_text, (WIDTH / 2 - pause_text.get_width() / 2, HEIGHT / 2 - pause_text.get_height() / 2))
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    paused = not paused
                        pygame.display.flip()

                pygame.display.flip()
                clock.tick(60)
                speed_increase_timer += 1


        # Game Over
        if restart_mode:
            game_over_text = FONT.render("Game Over! Restarting in 1 second.", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
            pygame.display.flip()
            time.sleep(1)
            boss = None
        else:
            boss = None
            game_close = True
            while game_close:
                screen.fill(BLACK)
                value = FONT.render("You Lost! Press Q-Quit, C-Play Again", True, WHITE)
                value2 = FONT.render("I-Increase Hearts (costs " + str(coin_cost) + " coins.)", True, WHITE)
                value3 = FONT.render("R-Turn on Auto Restart (turn off by pressing r at any time)", True, WHITE)
                value4 = FONT.render("E-Easy Mode, N-Normal Mode,", True, WHITE)
                value5 = FONT.render("H-Hard Mode (harder = more coins)", True, WHITE)
                value6 = FONT.render("L-Increase Luck (costs " + str(luck_cost) + " coins.)", True, WHITE)
                screen.blit(value, (WIDTH // 2 - value.get_width() // 2, HEIGHT // 2 - 100))
                screen.blit(value2, (WIDTH // 2 - value2.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(value3, (WIDTH // 2 - value3.get_width() // 2, HEIGHT // 2))
                screen.blit(value4, (WIDTH // 2 - value4.get_width() // 2, HEIGHT // 2 + 50))
                screen.blit(value5, (WIDTH // 2 - value5.get_width() // 2, HEIGHT // 2 + 100))
                screen.blit(value6, (WIDTH // 2 - value6.get_width() // 2, HEIGHT // 2 + 150))

                coin_amount = FONT.render(f"Coins: {coins}", True, WHITE)
                heart_amount = FONT.render(f"Lives: {base_lives_amount}", True, WHITE)
                mode_text = FONT.render(f"Mode: {mode}", True, WHITE)
                screen.blit(coin_amount, [10, 10])
                screen.blit(heart_amount, [WIDTH - heart_amount.get_width() - 10, 10])
                screen.blit(mode_text, [WIDTH - mode_text.get_width() - 10, 50])
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_c:
                            game_close = False
                        if event.key == pygame.K_i:
                            if coins > coin_cost:
                                coins -= coin_cost
                                base_lives_amount += 1
                                coin_cost *= 1.25
                                coin_cost = int(round(coin_cost))
                        if event.key == pygame.K_r:
                            restart_mode = True
                        if event.key == pygame.K_e:
                            mode = "easy"
                        if event.key == pygame.K_n:
                            mode = "normal"
                        if event.key == pygame.K_h:
                            mode = "hard"
                        if event.key == pygame.K_l:
                            if coins > luck_cost:
                                luck += 1
                                coins -= luck_cost
                                luck_cost *= 1.25
                                luck_cost = int(round(luck_cost))



        
    
    pygame.quit()

game()
