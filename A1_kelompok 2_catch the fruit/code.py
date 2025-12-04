import pygame
import random

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch The Fruit - Game Keranjang")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)

clock = pygame.time.Clock()
FPS = 60

background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
for y in range(SCREEN_HEIGHT):
    color = (0, min(255, y // 3), min(255, y))
    pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))

basket_width = 110
basket_height = 25
basket_x = (SCREEN_WIDTH - basket_width) // 2
basket_y = SCREEN_HEIGHT - 60
basket_speed = 10

object_radius = 12
object_x = random.randint(object_radius, SCREEN_WIDTH - object_radius)
object_y = 0
object_speed = 3

object_type = random.choice(["apple", "orange", "banana", "bomb"])

score = 0
lives = 5
level = 1

font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 55)

running = True
game_over = False

while running:

    if game_over:
        screen.fill(BLACK)
        screen.blit(big_font.render("GAME OVER", True, RED), (80, 200))
        screen.blit(font.render(f"Skor Akhir: {score}", True, WHITE), (120, 260))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        continue

    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and basket_x > 0:
        basket_x -= basket_speed
    if keys[pygame.K_RIGHT] and basket_x < SCREEN_WIDTH - basket_width:
        basket_x += basket_speed

    object_y += object_speed

    if (object_y + object_radius >= basket_y and basket_x <= object_x <= basket_x + basket_width):

        if object_type == "bomb":
            lives -= 1
        else:
            score += 1

        if score % 5 == 0 and score > 0:
            level += 1
            object_speed += 0.3

        object_x = random.randint(object_radius, SCREEN_WIDTH - object_radius)
        object_y = 0
        object_type = random.choice(["apple", "orange", "banana", "bomb"])

    if object_y > SCREEN_HEIGHT:
        if object_type != "bomb":
            lives -= 1

        object_x = random.randint(object_radius, SCREEN_WIDTH - object_radius)
        object_y = 0
        object_type = random.choice(["apple", "orange", "banana", "bomb"])

    if lives <= 0:
        game_over = True

    pygame.draw.rect(screen, WHITE, (basket_x, basket_y, basket_width, basket_height))
    pygame.draw.rect(screen, WHITE, (basket_x + 20, basket_y - 10, basket_width - 40, 8))


    if object_type == "apple":  
        pygame.draw.circle(screen, RED, (object_x, object_y), object_radius)
        pygame.draw.rect(screen, BROWN, (object_x - 2, object_y - object_radius - 5, 4, 8))
        pygame.draw.ellipse(screen, GREEN, (object_x + 3, object_y - object_radius, 10, 6))

    elif object_type == "orange":  
        pygame.draw.circle(screen, ORANGE, (object_x, object_y), object_radius)
        for i in range(5):
            pygame.draw.circle(screen, (255, 180, 0),
                               (object_x + random.randint(-5, 5), object_y + random.randint(-5, 5)), 2)
        pygame.draw.polygon(screen, (0,150,0), [
            (object_x, object_y - object_radius),
            (object_x + 8, object_y - object_radius - 5),
            (object_x + 5, object_y - object_radius + 5)
        ])

    elif object_type == "banana":  
        pygame.draw.ellipse(screen, YELLOW, (object_x - 15, object_y - 8, 30, 16))
        pygame.draw.ellipse(screen, BLACK, (object_x - 15, object_y - 8, 30, 16), 2)
        pygame.draw.line(screen, BLACK, (object_x - 8, object_y - 2), (object_x + 8, object_y + 2), 2)

    elif object_type == "bomb":  
        pygame.draw.circle(screen, BLACK, (object_x, object_y), object_radius)
        pygame.draw.rect(screen, GRAY, (object_x - 3, object_y - object_radius - 6, 6, 6))

    screen.blit(font.render(f"Skor: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Nyawa: {lives}", True, WHITE), (10, 70))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
