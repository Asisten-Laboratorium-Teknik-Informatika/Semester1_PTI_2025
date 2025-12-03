import pygame
import random
import sys

pygame.init()

# --- Screen ---
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Fish - Night Mode Feature")

clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
DARK_GREEN = (20, 150, 20)
LIGHT_GREEN = (50, 220, 50)

# Day sky
SKY_TOP_DAY = (135, 206, 250)
SKY_BOTTOM_DAY = (180, 230, 255)

# Night sky
SKY_TOP_NIGHT = (10, 10, 40)
SKY_BOTTOM_NIGHT = (30, 30, 80)

BLACK = (0, 0, 0)

# --- Fish (character) ---
fish_x = 80
fish_y = HEIGHT // 2
velocity = 0
gravity = 0.4
jump = -8
frame = 0

# --- Pipes ---
pipe_width = 75
pipe_gap = 155
pipe_x = WIDTH
pipe_top = random.randint(80, 350)
pipe_speed = 3

# --- Score ---
score = 0
high_score = 0

font_big = pygame.font.SysFont("arial", 48, bold=True)
font = pygame.font.SysFont("arial", 32)
font_small = pygame.font.SysFont("arial", 22)


def draw_fish():
    global frame
    frame = (frame + 1) % 30
    tail_offset = [-6, 0, 6][frame // 10]

    # Body
    pygame.draw.ellipse(screen, (255, 140, 0), (fish_x - 20, fish_y - 12, 40, 24))
    pygame.draw.ellipse(screen, (200, 100, 0), (fish_x - 20, fish_y - 12, 40, 24), 2)

    # Tail animation
    pygame.draw.polygon(
        screen,
        (255, 180, 0),
        [(fish_x - 20, fish_y),
         (fish_x - 35, fish_y - 10 + tail_offset),
         (fish_x - 35, fish_y + 10 - tail_offset)]
    )

    # Eye
    pygame.draw.circle(screen, WHITE, (fish_x + 10, fish_y - 5), 5)
    pygame.draw.circle(screen, BLACK, (fish_x + 11, fish_y - 5), 2)


def draw_pipes():
    pygame.draw.rect(screen, DARK_GREEN, (pipe_x, 0, pipe_width, pipe_top))
    pygame.draw.rect(screen, LIGHT_GREEN, (pipe_x, 0, pipe_width, pipe_top), 5)

    bottom_y = pipe_top + pipe_gap

    pygame.draw.rect(screen, DARK_GREEN, (pipe_x, bottom_y, pipe_width, HEIGHT - bottom_y))
    pygame.draw.rect(screen, LIGHT_GREEN, (pipe_x, bottom_y, pipe_width, HEIGHT - bottom_y), 5)


def check_collision():
    if fish_x + 15 > pipe_x and fish_x - 15 < pipe_x + pipe_width:
        if fish_y - 15 < pipe_top or fish_y + 15 > pipe_top + pipe_gap:
            return True
    if fish_y <= 0 or fish_y >= HEIGHT:
        return True
    return False


# Moving cloud
cloud_x = WIDTH


def draw_background(is_night):
    global cloud_x

    # Select sky colors
    sky_top = SKY_TOP_NIGHT if is_night else SKY_TOP_DAY
    sky_bottom = SKY_BOTTOM_NIGHT if is_night else SKY_BOTTOM_DAY

    # Gradient sky
    for i in range(HEIGHT):
        color = (
            sky_top[0] + (sky_bottom[0] - sky_top[0]) * i // HEIGHT,
            sky_top[1] + (sky_bottom[1] - sky_top[1]) * i // HEIGHT,
            sky_top[2] + (sky_bottom[2] - sky_top[2]) * i // HEIGHT
        )
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))

    # Cloud only visible in day
    if not is_night:
        cloud_x -= 1
        if cloud_x < -200:
            cloud_x = WIDTH + random.randint(50, 150)

        pygame.draw.ellipse(screen, WHITE, (cloud_x, 80, 120, 40))
        pygame.draw.ellipse(screen, WHITE, (cloud_x + 50, 60, 100, 35))
        pygame.draw.ellipse(screen, WHITE, (cloud_x - 30, 70, 110, 45))


def show_start_menu():
    while True:
        draw_background(False)
        title = font_big.render("FLAPPY FISH", True, WHITE)
        start = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 180))
        screen.blit(start, (WIDTH//2 - start.get_width()//2, 300))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def show_pause_screen():
    pause_text = font_big.render("PAUSED", True, WHITE)
    info = font_small.render("Press P to Resume", True, WHITE)
    while True:
        draw_background(False)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, 240))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, 320))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                return


def show_game_over():
    global high_score
    if score > high_score:
        high_score = score
    while True:
        draw_background(False)
        over = font_big.render("GAME OVER", True, WHITE)
        sc = font.render(f"Score : {score}", True, WHITE)
        hs = font.render(f"High Score : {high_score}", True, WHITE)
        retry = font_small.render("Press SPACE to Restart", True, WHITE)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, 160))
        screen.blit(sc, (WIDTH//2 - sc.get_width()//2, 260))
        screen.blit(hs, (WIDTH//2 - hs.get_width()//2, 310))
        screen.blit(retry, (WIDTH//2 - retry.get_width()//2, 380))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


# Start game
show_start_menu()

while True:
    fish_y = HEIGHT//2
    velocity = 0
    pipe_x = WIDTH
    pipe_top = random.randint(80, 350)
    score = 0

    while True:
        is_night = score >= 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    velocity = jump
                if event.key == pygame.K_p:
                    show_pause_screen()

        velocity += gravity
        fish_y += velocity

        pipe_x -= pipe_speed

        if pipe_x < -pipe_width:
            pipe_x = WIDTH
            pipe_top = random.randint(80, 350)
            score += 1

        if check_collision():
            break

        draw_background(is_night)
        draw_pipes()
        draw_fish()

        txt = font.render(str(score), True, WHITE)
        screen.blit(txt, (WIDTH // 2 - 10, 20))

        pygame.display.update()
        clock.tick(60)

    show_game_over()
