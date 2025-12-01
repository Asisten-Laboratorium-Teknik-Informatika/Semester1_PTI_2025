from settings import *
from sprites import *
from groups import AllSprites
from support import *
from timer import Timer
from random import randint
import os
import pygame

class Game:
    def __init__(self):
        # init audio + pygame
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass
        #displaytab
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('ShooterBlitsz')
        self.clock = pygame.time.Clock()
        self.running = True

        self.health = 2
        self.kills = 0
        self.win_kills = 8      # menang skor
        self.game_over = False

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load assets
        self.load_assets()

        # play background music (stop dulu untuk cegah double audio)
        if 'msc' in self.audio:
            try:
                pygame.mixer.stop()
                pygame.mixer.music.stop()
            except Exception:
                pass
            try:
                self.audio['msc'].set_volume(0.5)
                self.audio['msc'].play(loops=-1)
            except Exception:
                pass

        # setup level dan spawn musuh
        self.setup()
        self.bee_timer = Timer(900, func=self.create_bee, autostart=True, repeat=True)
        self.create_bee()

    # spawn musuh berdasarkan kamera, beri variasi gerak vertikal (melayang)
    def create_bee(self):
        if not hasattr(self, "player"):
            return
        if not getattr(self, 'bee_frames', None):
            return

        NUM = 1
        X_OFFSET = 60

        cam_right_world = self.player.rect.centerx + WINDOW_WIDTH // 2
        base_x = cam_right_world + 40
        cam_top_world = self.player.rect.centery - WINDOW_HEIGHT // 2

        for i in range(NUM):
            x = base_x + i * X_OFFSET
            y = cam_top_world + randint(20, WINDOW_HEIGHT - 20)
            y = max(0, min(self.level_height, y))

            # buat instance Bee dan set property sway untuk gerak melayang
            bee = Bee(
                frames=self.bee_frames,
                pos=(x, y),
                groups=(self.all_sprites, self.enemy_sprites),
                speed=randint(250, 350)
            )

            # tingkatkan amplitude dan atur frequency acak supaya gerak tidak lurus
            try:
                bee.amplitude = randint(40, 120)   # besar ayunan vertikal
                bee.frequency = randint(150, 500)  # frekuensi ayunan (lebih kecil = lebih cepat)
                # optional phase offset supaya bee tidak sinkron sempurna
                bee._phase = randint(0, 10000)
            except Exception:
                pass

    # tembak peluru
    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        if 'shoot' in self.audio:
            try:
                self.audio['shoot'].play()
            except Exception:
                pass

    # load gambar + audio
    def load_assets(self):
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            images_root = os.path.join(project_root, 'images')
            audio_root = os.path.join(project_root, 'audio')

            self.player_frames = import_folder(images_root, 'player')
            self.bullet_surf = import_image(images_root, 'gun', 'bullet')
            self.fire_surf = import_image(images_root, 'gun', 'fire')
            self.bee_frames = import_folder(images_root, 'enemies', 'bee')
            self.worm_frames = import_folder(images_root, 'enemies', 'worm')

            # resize worm/crab agar proporsional
            if self.worm_frames and self.player_frames:
                try:
                    ref_h = self.player_frames[0].get_height()
                except:
                    ref_h = 32

                resized = []
                for surf in self.worm_frames:
                    try:
                        ratio = ref_h / surf.get_height()
                        w = int(surf.get_width() * ratio)
                        h = ref_h
                        resized.append(pygame.transform.scale(surf, (w, h)).convert_alpha())
                    except:
                        resized.append(surf)
                self.worm_frames = resized

            self.audio = audio_importer(audio_root)

            if not self.player_frames:
                dummy = pygame.Surface((32,32)).convert_alpha()
                dummy.fill((255,0,255))
                self.player_frames = [dummy]
            if not self.bee_frames:
                self.bee_frames = [pygame.Surface((32,32)).convert_alpha()]
            if not self.worm_frames:
                self.worm_frames = [pygame.Surface((32,32)).convert_alpha()]

        except:
            dummy = pygame.Surface((32,32)).convert_alpha()
            dummy.fill((255,0,255))
            self.player_frames = [dummy]
            self.bee_frames = [dummy]
            self.worm_frames = [dummy]
            self.bullet_surf = dummy
            self.fire_surf = dummy
            self.audio = {}

    # setup level
    def setup(self):
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            tmx_path = os.path.join(project_root, 'data', 'maps', 'world.tmx')
            tmx_map = load_pygame(tmx_path)

            self.level_width = tmx_map.width * TILE_SIZE
            self.level_height = tmx_map.height * TILE_SIZE

            for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

            for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

            for obj in tmx_map.get_layer_by_name('Entities'):
                if obj.name == 'Player':
                    self.player = Player(
                        (obj.x, obj.y),
                        self.all_sprites,
                        self.collision_sprites,
                        self.player_frames,
                        self.create_bullet
                    )
                if obj.name == 'Worm':
                    Worm(
                        self.worm_frames,
                        pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                        (self.all_sprites, self.enemy_sprites)
                    )
        except:
            pass

    # collision handling
    def collision(self):
        # peluru → musuh
        for bullet in list(self.bullet_sprites):
            hits = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if hits:
                if 'impact' in self.audio:
                    try:
                        self.audio['impact'].play()
                    except:
                        pass
                bullet.kill()
                for enemy in hits:
                    try:
                        enemy.destroy()
                    except:
                        enemy.kill()

                    # tambah kill
                    self.kills += 1

                    # cek menang
                    if self.kills >= self.win_kills:
                        self.trigger_win()
                        return

        # musuh → player
        collisions = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if collisions:
            for enemy in collisions:
                try:
                    enemy.destroy()
                except:
                    enemy.kill()

            self.health -= 1

            if 'impact' in self.audio:
                try:
                    self.audio['impact'].play()
                except:
                    pass

            if self.health <= 0:
                self.trigger_game_over()

    # layar kalah
    def trigger_game_over(self):
        self.game_over = True
        font = pygame.font.Font(None, 90)
        small_font = pygame.font.Font(None, 50)

        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except:
            pass

        while self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        return
                    if event.key == pygame.K_q:
                        pygame.quit()
                        exit()

            text = font.render("GAME OVER", True, (255, 80, 80))
            restart = small_font.render("Press R to Restart", True, (255, 255, 255))
            quit_msg = small_font.render("Press Q to Quit", True, (255, 255, 255))

            self.display_surface.fill((10, 10, 10))
            self.display_surface.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 150))
            self.display_surface.blit(restart, (WINDOW_WIDTH//2 - restart.get_width()//2, 300))
            self.display_surface.blit(quit_msg, (WINDOW_WIDTH//2 - quit_msg.get_width()//2, 360))
            pygame.display.update()
            self.clock.tick(30)

    # layar menang
    def trigger_win(self):
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except:
            pass

        font = pygame.font.Font(None, 90)
        small_font = pygame.font.Font(None, 50)
        win_text = "YOU WIN, LESGOOOO"

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        return
                    if event.key == pygame.K_q:
                        pygame.quit()
                        exit()

            text = font.render(win_text, True, (120, 220, 120))
            restart = small_font.render("Press R to Play Again", True, (255, 255, 255))
            quit_msg = small_font.render("Press Q to Quit", True, (255, 255, 255))

            self.display_surface.fill((10, 10, 10))
            self.display_surface.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 150))
            self.display_surface.blit(restart, (WINDOW_WIDTH//2 - restart.get_width()//2, 300))
            self.display_surface.blit(quit_msg, (WINDOW_WIDTH//2 - quit_msg.get_width()//2, 360))
            pygame.display.update()
            self.clock.tick(30)

    # main loop
    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()

            self.display_surface.fill(BG_COLOR)
            try:
                self.all_sprites.draw(self.player.rect.center)
            except:
                self.all_sprites.draw(self.display_surface)

            pygame.display.update()

        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except:
            pass
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
