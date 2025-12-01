from settings import * 
from timer import Timer
from math import sin
from random import randint
import pygame

DEBUG_INPUT = True  # set False kalau gak mau log input di console

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        # support groups as tuple/list or single group or None
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        elif groups is None:
            super().__init__()
        else:
            super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_rect(topleft=pos)
        # optional mask
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None

class Bullet(Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(pos, surf, groups)
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.direction = direction
        self.speed = 850
    
    def update(self, dt):
        self.rect.x += int(self.direction * self.speed * dt)
        # kill if offscreen far away
        if self.rect.right < -2000 or self.rect.left > WINDOW_WIDTH + 2000:
            self.kill()

class Fire(Sprite):
    def __init__(self, surf, pos, groups, player):
        super().__init__(pos, surf, groups)
        self.player = player 
        self.flip = player.flip
        self.timer = Timer(100, autostart=True, func=self.kill)
        self.y_offset = pygame.Vector2(0, 8)
        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset

    def update(self, _):
        self.timer.update()
        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset
        if self.flip != self.player.flip:
            self.kill()

class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames = frames if frames else [pygame.Surface((32,32))]
        self.frame_index = 0
        self.animation_speed = 10
        super().__init__(pos, self.frames[int(self.frame_index) % len(self.frames)], groups)

    def animate(self, dt):
        if not self.frames:
            return
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        # update mask after image change
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None

class Enemy(AnimatedSprite):
    def __init__(self, frames, pos, groups):
        super().__init__(frames, pos, groups)
        self.death_timer = Timer(200, func=self.kill)

    def destroy(self):
        self.death_timer.activate()
        self.animation_speed = 0
        try:
            surf = pygame.mask.from_surface(self.image).to_surface()
            surf.set_colorkey((0,0,0))
            self.image = surf
        except Exception:
            pass

    def update(self, dt):
        self.death_timer.update()
        if not self.death_timer:
            self.move(dt)
            self.animate(dt)
        self.constraint()

class Bee(Enemy):
    def __init__(self, frames, pos, groups, speed):
        super().__init__(frames, pos, groups)
        self.speed = speed
        self.amplitude = randint(20, 60)
        self.frequency = randint(300, 600)

    def move(self, dt):
        self.rect.x -= int(self.speed * dt)
        self.rect.y += int(sin(pygame.time.get_ticks() / self.frequency) * self.amplitude * dt)
    
    def constraint(self):
        if self.rect.right <= 0:
            self.kill()

# New: Crab class (replaces Worm visually). Keeps same behavior: walk left-right inside main_rect
class Crab(Enemy):
    def __init__(self, frames, rect, groups):
        # frames expected to be two images: 0.png (open), 1.png (closed) or vice versa
        super().__init__(frames, rect.topleft, groups)
        self.rect.bottomleft = rect.bottomleft
        self.main_rect = rect
        self.speed = randint(80, 140)   # crab moves slower than worm to feel different
        self.direction = 1
        # make animation visible (lower = slower frame change, higher = faster)
        self.animation_speed = 6

    def move(self, dt):
        self.rect.x += int(self.direction * self.speed * dt)

    def constraint(self):
        if not self.main_rect.contains(self.rect):
            self.direction *= -1
            # flip frames horizontally when turning
            self.frames = [pygame.transform.flip(surf, True, False) for surf in self.frames]

# keep Worm name for compatibility but point to Crab
Worm = Crab

class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, frames, create_bullet):
        super().__init__(frames, pos, groups)
        self.flip = False
        self.create_bullet = create_bullet

        # movement & collision
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.speed = 400
        self.gravity = 1000  
        self.on_floor = False

        # timer
        self.shoot_timer = Timer(500)

    def input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        # gerak kiri/kanan: Arrow keys atau A/D
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        left  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        old_dx = self.direction.x
        self.direction.x = int(right) - int(left)

        # lompat: SPACE atau W
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_floor:
            self.direction.y = -550

        # tembak: S atau klik kiri mouse
        if (keys[pygame.K_s] or mouse[0]) and not self.shoot_timer:
            if DEBUG_INPUT:
                print("DEBUG: shoot triggered (mouse/keyboard). flip:", self.flip)
            self.create_bullet(self.rect.center, -1 if self.flip else 1)
            self.shoot_timer.activate()

        if DEBUG_INPUT and old_dx != self.direction.x:
            print(f"DEBUG: move input dx={self.direction.x} (right={right} left={left})")

    def move(self, dt):
        self.rect.x += int(self.direction.x * self.speed * dt)
        self.collision('horizontal')
        
        self.direction.y += self.gravity * dt
        self.rect.y += int(self.direction.y * dt)
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                        self.on_floor = True
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                    self.direction.y = 0

    def check_floor(self):
        bottom_rect = pygame.Rect(0, 0, self.rect.width, 2)
        bottom_rect.midtop = self.rect.midbottom
        self.on_floor = bottom_rect.collidelist([sprite.rect for sprite in self.collision_sprites]) >= 0

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += self.animation_speed * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0

        self.frame_index = 1 if not self.on_floor else self.frame_index
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)
        # update mask after flip
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None

    def update(self, dt):
        self.shoot_timer.update()
        self.check_floor()
        self.input()
        self.move(dt)
        self.animate(dt)
