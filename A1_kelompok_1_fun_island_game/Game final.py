# fun_island_game.py
import pygame, random, math, sys, time
pygame.init()

# --- Window ---
W, H = 900, 640
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Island Dash — Kumpulkan Kelapa, Hindari Bahaya!")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 24)
BIG = pygame.font.SysFont("Arial", 48, bold=True)

# --- Colors ---
SKY = (135, 206, 235)
OCEAN = (0, 105, 148)
SAND = (237, 201, 175)
PLAYER_SKIN = (255, 224, 189)
PLAYER_SHIRT = (30, 144, 255)
PLAYER_PANTS = (25, 25, 112)
SNAKE = (34, 139, 34)
CRAB = (200, 80, 40)
COCONUT = (120, 80, 30)
MEDKIT = (220, 20, 60)

# --- Controls accepted ---
# Arrow keys, WASD, or T F G H (T=up, F=left, G=right, H=down)

# --- Game objects ---
class Player:
    def __init__(self):
        self.w, self.h = 34, 50
        self.x = W//2 - self.w//2
        self.y = H - 180
        self.speed = 5
        self.hp = 100
        self.lives = 3
        self.invuln = 0   # frames of invulnerability after hit

    def move(self, keys):
        dx = dy = 0
        # Arrow / WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += self.speed
        # T F G H
        if keys[pygame.K_f]: dx -= self.speed
        if keys[pygame.K_g]: dx += self.speed
        if keys[pygame.K_t]: dy -= self.speed
        if keys[pygame.K_h]: dy += self.speed

        self.x = max(10, min(W - self.w - 10, self.x + dx))
        self.y = max(80, min(H - self.h - 60, self.y + dy))

    def draw(self, surf):
        # if invuln blink
        if self.invuln % 10 < 5:
            # head
            pygame.draw.circle(surf, PLAYER_SKIN, (self.x + self.w//2, self.y + 12), 10)
            # body
            pygame.draw.rect(surf, PLAYER_SHIRT, (self.x + 6, self.y + 22, self.w - 12, 18), border_radius=4)
            # pants
            pygame.draw.rect(surf, PLAYER_PANTS, (self.x + 8, self.y + 40, self.w - 16, 10), border_radius=3)
            # arms
            pygame.draw.line(surf, PLAYER_SKIN, (self.x+2, self.y+28), (self.x-8, self.y+36), 5)
            pygame.draw.line(surf, PLAYER_SKIN, (self.x+self.w-2, self.y+28), (self.x+self.w+8, self.y+36), 5)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Item:
    def __init__(self, kind):
        self.kind = kind  # "coconut" or "medkit"
        self.x = random.randint(60, W-60)
        self.y = random.randint(140, H-220)
        self.float = random.random()*2

    def update(self):
        self.float = math.sin(time.time()*3 + self.x)*3

    def draw(self, surf):
        y = int(self.y + self.float)
        if self.kind == "coconut":
            pygame.draw.circle(surf, COCONUT, (self.x, y), 12)
            pygame.draw.arc(surf, (90,60,30), (self.x-12, y-12, 24, 24), 0, 3.14, 2)
        else:
            pygame.draw.rect(surf, MEDKIT, (self.x-12, y-12, 24, 24), border_radius=5)
            pygame.draw.rect(surf, (255,255,255), (self.x-4, y-12, 8, 24))
            pygame.draw.rect(surf, (255,255,255), (self.x-12, y-4, 24, 8))

    def rect(self):
        return pygame.Rect(self.x-14, int(self.y+self.float)-14, 28, 28)

class Enemy:
    def __init__(self, kind, level=1):
        self.kind = kind  # 'snake' : slithers; 'crab' : walks horizontal
        self.level = level
        if kind == 'snake':
            self.x = random.randint(80, W-80)
            self.y = random.randint(150, H-220)
            self.angle = random.random()*2*math.pi
            self.speed = 0.8 + 0.2*level + random.random()*0.6
            self.length = 40 + level*4
        else:
            self.y = H - 120
            self.x = random.choice([50, W-50])
            self.dir = 1 if self.x < W//2 else -1
            self.speed = 1.2 + 0.2*level + random.random()*0.6
            self.leg = 0

    def update(self):
        if self.kind == 'snake':
            self.angle += random.uniform(-0.15, 0.15)
            self.x += math.cos(self.angle)*self.speed
            self.y += math.sin(self.angle)*self.speed
            # keep within play area
            self.x = max(60, min(W-60, self.x))
            self.y = max(120, min(H-200, self.y))
        else:
            self.x += self.dir * self.speed
            self.leg += 0.3
            if self.x < 40 or self.x > W-40:
                self.dir *= -1

    def draw(self, surf):
        if self.kind == 'snake':
            # draw segments
            for i in range(0, self.length, 6):
                off = i/2.0
                sx = int(self.x - math.cos(self.angle)*off)
                sy = int(self.y - math.sin(self.angle)*off)
                size = max(3, 8 - i/12)
                pygame.draw.circle(surf, SNAKE, (sx, sy), size)
            ex = int(self.x + math.cos(self.angle)*8)
            ey = int(self.y + math.sin(self.angle)*8)
            pygame.draw.circle(surf, (255,255,0), (ex,ey), 3)
        else:
            pygame.draw.circle(surf, CRAB, (int(self.x), int(self.y)), 14)
            # claws
            pygame.draw.circle(surf, (140,60,40), (int(self.x-18), int(self.y-4)), 6)
            pygame.draw.circle(surf, (140,60,40), (int(self.x+18), int(self.y-4)), 6)

    def rect(self):
        if self.kind == 'snake':
            # long collider along body
            return pygame.Rect(int(self.x-20), int(self.y-10), 60, 20)
        else:
            return pygame.Rect(int(self.x-18), int(self.y-14), 36, 28)

# --- Helpers: draw background and UI
def draw_background(t):
    screen.fill(SKY)
    # sun
    pygame.draw.circle(screen, (255,240,150), (100,80), 40)
    # clouds
    for i in range(3):
        cx = (i*320 + int(t*30)) % (W+200) - 100
        pygame.draw.ellipse(screen, (255,255,255), (cx, 70, 90, 40))
    # ocean
    pygame.draw.rect(screen, OCEAN, (0, H-160, W, 160))
    # waves
    for i in range(0, W, 30):
        wy = H-160 + math.sin(i*0.07 + t*3)*6
        pygame.draw.line(screen, (200,230,255), (i, wy), (i, wy+10), 2)
    # sand
    pygame.draw.rect(screen, SAND, (0, H-120, W, 120))
    # palm simple
    pygame.draw.rect(screen, (100,60,30), (W-140, H-320, 18, 180))
    for idx, leaf in enumerate([(-40,-40),(0,-60),(40,-40),(-80,-20),(80,-20)]):
        lx = W-131 + leaf[0]; ly = H-320 + leaf[1]
        pygame.draw.polygon(screen, (40,140,70), [(W-131,H-320),(lx,ly),(lx+30,ly+10)])

def draw_ui(score, hp, lives, level, time_left):
    # score & level
    s = FONT.render(f"Score: {score}", True, (20,20,20))
    lvl = FONT.render(f"Level: {level}", True, (20,20,20))
    screen.blit(s, (18,18)); screen.blit(lvl, (18,46))
    # HP bar
    pygame.draw.rect(screen, (60,60,60), (W-220,18,200,18), border_radius=6)
    pygame.draw.rect(screen, (220,0,0), (W-220,18,int(200*(hp/100)),18), border_radius=6)
    screen.blit(FONT.render(f"HP: {int(hp)}", True, (255,255,255)), (W-140,16))
    # lives
    screen.blit(FONT.render(f"Lives: {lives}", True, (20,20,20)), (18,74))
    # timer
    screen.blit(FONT.render(f"Time: {int(time_left)}s", True, (20,20,20)), (W//2-40,18))

# --- Game loop state ---
def run_game():
    player = Player()
    items = [Item("coconut") for _ in range(3)]
    enemies = [Enemy(random.choice(['snake','crab']), level=1) for _ in range(2)]
    score = 0
    level = 1
    start_level_time = time.time()
    level_duration = 25  # seconds per level
    last_spawn_item = time.time()
    last_spawn_enemy = time.time()
    game_over = False
    paused = False

    while True:
        dt = clock.tick(60)/1000.0
        t = time.time()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_p:
                    paused = not paused
                if ev.key == pygame.K_r and game_over:
                    return  # restart outerly

        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)

            # update items & enemies
            for it in items:
                it.update()
            for en in enemies:
                en.update()

            # spawn new item occasionally
            if time.time() - last_spawn_item > 3 and len(items) < 6:
                items.append(Item(random.choice(["coconut","medkit"])))
                last_spawn_item = time.time()

            # spawn new enemy occasionally (scale with level)
            if time.time() - last_spawn_enemy > max(1.2, 4.0 - level*0.3):
                enemies.append(Enemy(random.choice(['snake','crab']), level=level))
                last_spawn_enemy = time.time()

            # collisions: player <-> items
            for it in items[:]:
                if player.rect().colliderect(it.rect()):
                    if it.kind == "coconut":
                        score += 10 + level*2
                    else:
                        player.hp = min(100, player.hp + 30)
                    try:
                        items.remove(it)
                    except ValueError:
                        pass

            # collisions: player <-> enemies
            for en in enemies[:]:
                if player.rect().colliderect(en.rect()):
                    if player.invuln == 0:
                        # damage based on enemy
                        if en.kind == 'snake':
                            dmg = 30
                        else:
                            dmg = 12 + level*2
                        player.hp -= dmg
                        player.invuln = 40  # ~0.66s invuln
                        # knockback a bit
                        player.x -= 20 if en.x < player.x else -20
                        if player.hp <= 0:
                            player.lives -= 1
                            player.hp = 100
                            # clear some enemies to give a chance
                            enemies = enemies[2:] if len(enemies)>2 else []
                            if player.lives <= 0:
                                game_over = True

            if player.invuln > 0:
                player.invuln -= 1

            # level progression
            time_left = max(0, level_duration - (time.time() - start_level_time))
            if time_left <= 0:
                level += 1
                start_level_time = time.time()
                # give bonus and spawn more enemies
                score += 50 * level
                for _ in range(2 + level):
                    enemies.append(Enemy(random.choice(['snake','crab']), level=level))

        # --- DRAW ---
        draw_background(time.time())
        for it in items:
            it.draw(screen)
        for en in enemies:
            en.draw(screen)
        player.draw(screen)

        # ui
        time_left = max(0, level_duration - (time.time() - start_level_time))
        draw_ui(score, player.hp, player.lives, level, time_left)

        if paused:
            text = BIG.render("PAUSED", True, (20,20,20))
            screen.blit(text, (W//2 - text.get_width()//2, H//2 - 30))
        if game_over:
            overlay = pygame.Surface((W,H), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            screen.blit(overlay, (0,0))
            msg = BIG.render("GAME OVER", True, (255,80,80))
            screen.blit(msg, (W//2-msg.get_width()//2, H//2-40))
            sub = FONT.render(f"Score: {score}  —  Tekan R untuk main lagi", True, (255,255,255))
            screen.blit(sub, (W//2-sub.get_width()//2, H//2+20))

        pygame.display.flip()

# --- Start screen ---
def start_screen():
    while True:
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    return
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        screen.fill(SKY)
        draw_background(time.time())
        title = BIG.render("Island Dash", True, (15,90,60))
        screen.blit(title, (W//2 - title.get_width()//2, 80))
        help1 = FONT.render("Kontrol: Panah / WASD / T F G H  •  P = Pause  •  R = Restart", True, (10,10,10))
        screen.blit(help1, (W//2 - help1.get_width()//2, 180))
        desc = FONT.render("Kumpulkan kelapa, ambil medkit, hindari ular & kepiting. Tekan Enter untuk mulai!", True, (10,10,10))
        screen.blit(desc, (W//2 - desc.get_width()//2, 220))
        pygame.display.flip()

# --- Run game ---
if __name__ == "__main__":
    while True:
        start_screen()
        run_game()
        # After run_game returns (player pressed R on game over), loop restarts (start screen)
