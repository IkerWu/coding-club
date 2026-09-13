"""
FLAPPY BIRD - TWEAK EDITION
Coding Club

HOW TO PLAY
  SPACE or CLICK ... flap
  R ............... restart

HOW TO TWEAK (while the game is running!)
  UP / DOWN ....... pick a setting
  LEFT / RIGHT .... change it
  H ............... show the bird's hitbox
  TAB ............. hide the settings panel (for screenshots)
  BACKSPACE ....... reset everything back to normal

Put the img/ folder next to this file. If it's missing, the game
still runs with coloured boxes instead of pictures.
"""

import random
import pygame

pygame.init()

# ----------------------------------------------------------------
#  THE TWEAK ZONE
#  Change these numbers and run the game again.
#  Or change them live with the arrow keys.
# ----------------------------------------------------------------

SETTINGS = {
    "gravity":        0.5,    # how hard the bird is pulled down
    "jump_strength":  10.0,   # how much one flap pushes the bird up
    "max_fall_speed": 8.0,    # the fastest the bird can ever fall
    "scroll_speed":   4.0,    # how fast the world moves past
    "pipe_gap":       180,    # the space between the top and bottom pipe
    "pipe_frequency": 1500,   # milliseconds between new pipes
    "pipe_variation": 100,    # how much the pipe height jumps around
    "hitbox_scale":   1.0,    # size of the bird's invisible collision box
}

# name, smallest, biggest, step size, what it does
TWEAKS = [
    ("gravity",          0.0,   3.0,   0.1),
    ("jump_strength",    0.0,  25.0,   1.0),
    ("max_fall_speed",   1.0,  40.0,   1.0),
    ("scroll_speed",     0.0,  20.0,   1.0),
    ("pipe_gap",        60,   700,    10),
    ("pipe_frequency", 200,  4000,   100),
    ("pipe_variation",   0,   350,    10),
    ("hitbox_scale",     0.1,   3.0,   0.1),
]

DEFAULTS = dict(SETTINGS)

# ----------------------------------------------------------------
#  Setup
# ----------------------------------------------------------------

SCREEN_W, SCREEN_H = 864, 936
GROUND_Y = 768
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (255, 220, 90)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Flappy Bird - Tweak Edition")
clock = pygame.time.Clock()

big_font = pygame.font.SysFont("bauhaus93,arialblack,arial", 60)
panel_font = pygame.font.SysFont("consolas,couriernew,monospace", 20)
hint_font = pygame.font.SysFont("consolas,couriernew,monospace", 16)


def load_image(path, size, colour):
    """Load a picture. If it isn't there, use a coloured box instead."""
    try:
        return pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(colour)
        pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
        return surf


bg_img = load_image("img/bg.png", (SCREEN_W, SCREEN_H), (110, 190, 230))
ground_img = load_image("img/ground.png", (SCREEN_W + 60, 168), (220, 200, 120))
button_img = load_image("img/restart.png", (120, 45), (230, 230, 230))
pipe_img = load_image("img/pipe.png", (80, 500), (80, 190, 80))
bird_frames = [
    load_image(f"img/bird{n}.png", (50, 35), (250, 210, 60))
    for n in (1, 2, 3)
]


def draw_text(text, font, colour, x, y, centred=False):
    img = font.render(text, True, colour)
    rect = img.get_rect()
    if centred:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)


# ----------------------------------------------------------------
#  The bird
# ----------------------------------------------------------------

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = bird_frames
        self.index = 0
        self.counter = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0.0

    @property
    def hitbox(self):
        """The invisible box the game actually uses for crashes."""
        scale = SETTINGS["hitbox_scale"]
        box = pygame.Rect(0, 0, int(40 * scale), int(30 * scale))
        box.center = self.rect.center
        return box

    def flap(self):
        self.vel = -SETTINGS["jump_strength"]

    def update(self, state):
        if state == "playing" or state == "dead":
            self.vel += SETTINGS["gravity"]
            if self.vel > SETTINGS["max_fall_speed"]:
                self.vel = SETTINGS["max_fall_speed"]
            if self.rect.bottom < GROUND_Y:
                self.rect.y += int(self.vel)
            else:
                self.rect.bottom = GROUND_Y

        if state == "dead":
            self.image = pygame.transform.rotate(self.frames[self.index], -90)
            return

        # flap animation
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index = (self.index + 1) % len(self.frames)

        tilt = max(-90, min(30, self.vel * -3))
        self.image = pygame.transform.rotate(self.frames[self.index], tilt)


# ----------------------------------------------------------------
#  The pipes
# ----------------------------------------------------------------

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, gap):
        super().__init__()
        self.image = pipe_img
        self.rect = self.image.get_rect()
        if position == 1:        # top pipe, hanging down
            self.image = pygame.transform.flip(pipe_img, False, True)
            self.rect = self.image.get_rect()
            self.rect.bottomleft = (x, y - gap // 2)
        else:                    # bottom pipe, standing up
            self.rect.topleft = (x, y + gap // 2)

    def update(self):
        self.rect.x -= int(SETTINGS["scroll_speed"])
        if self.rect.right < 0:
            self.kill()


# ----------------------------------------------------------------
#  Game state
# ----------------------------------------------------------------

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, SCREEN_H // 2)
bird_group.add(flappy)

button_rect = button_img.get_rect(center=(SCREEN_W // 2, SCREEN_H - 140))

state = "ready"          # ready -> playing -> dead
score = 0
pass_pipe = False
ground_scroll = 0
last_pipe = pygame.time.get_ticks()

selected = 0             # which setting the arrows are pointing at
show_panel = True
show_hitbox = False
repeat_timer = 0


def reset_game():
    global state, score, pass_pipe, last_pipe
    pipe_group.empty()
    flappy.rect.center = (100, SCREEN_H // 2)
    flappy.vel = 0.0
    flappy.index = 0
    score = 0
    pass_pipe = False
    last_pipe = pygame.time.get_ticks()
    state = "ready"


def change_setting(direction):
    name, low, high, step = TWEAKS[selected]
    value = SETTINGS[name] + direction * step
    value = max(low, min(high, value))
    SETTINGS[name] = round(value, 2) if isinstance(step, float) else int(value)


def draw_panel():
    panel = pygame.Surface((300, 24 * len(TWEAKS) + 70), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 165))
    screen.blit(panel, (SCREEN_W - 310, 10))

    draw_text("SETTINGS", panel_font, WHITE, SCREEN_W - 296, 22)
    for i, (name, low, high, step) in enumerate(TWEAKS):
        colour = HIGHLIGHT if i == selected else WHITE
        marker = ">" if i == selected else " "
        value = SETTINGS[name]
        shown = f"{value:.1f}" if isinstance(step, float) else f"{value}"
        draw_text(f"{marker} {name:<15}{shown:>6}", panel_font, colour,
                  SCREEN_W - 296, 52 + i * 24)

    draw_text("UP/DOWN pick  LEFT/RIGHT change", hint_font, (200, 200, 200),
              SCREEN_W - 296, 60 + len(TWEAKS) * 24)


# ----------------------------------------------------------------
#  Main loop
# ----------------------------------------------------------------

run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_h:
                show_hitbox = not show_hitbox
            elif event.key == pygame.K_TAB:
                show_panel = not show_panel
            elif event.key == pygame.K_BACKSPACE:
                SETTINGS.update(DEFAULTS)
            elif event.key == pygame.K_UP:
                selected = (selected - 1) % len(TWEAKS)
            elif event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(TWEAKS)
            elif event.key == pygame.K_SPACE:
                if state == "ready":
                    state = "playing"
                    flappy.flap()
                elif state == "playing":
                    flappy.flap()
                elif state == "dead":
                    reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "ready":
                state = "playing"
                flappy.flap()
            elif state == "playing":
                flappy.flap()
            elif state == "dead" and button_rect.collidepoint(event.pos):
                reset_game()

    # held arrow keys change the value smoothly
    keys = pygame.key.get_pressed()
    repeat_timer -= 1
    if repeat_timer <= 0:
        if keys[pygame.K_RIGHT]:
            change_setting(1)
            repeat_timer = 4
        elif keys[pygame.K_LEFT]:
            change_setting(-1)
            repeat_timer = 4

    screen.blit(bg_img, (0, 0))

    if state == "playing":
        now = pygame.time.get_ticks()
        if now - last_pipe > SETTINGS["pipe_frequency"]:
            variation = SETTINGS["pipe_variation"]
            offset = random.randint(-variation, variation) if variation else 0
            middle = SCREEN_H // 2 + offset - 100
            gap = SETTINGS["pipe_gap"]
            pipe_group.add(Pipe(SCREEN_W, middle, 1, gap))
            pipe_group.add(Pipe(SCREEN_W, middle, -1, gap))
            last_pipe = now

        pipe_group.update()
        ground_scroll -= int(SETTINGS["scroll_speed"])
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    bird_group.update(state)

    pipe_group.draw(screen)
    bird_group.draw(screen)
    screen.blit(ground_img, (ground_scroll, GROUND_Y))

    if show_hitbox:
        pygame.draw.rect(screen, (255, 60, 60), flappy.hitbox, 2)

    # scoring
    if state == "playing" and pipe_group:
        first = min(pipe_group.sprites(), key=lambda p: p.rect.x)
        if first.rect.left < flappy.rect.centerx < first.rect.right:
            pass_pipe = True
        elif pass_pipe and flappy.rect.centerx > first.rect.right:
            score += 1
            pass_pipe = False

    # crashes
    if state == "playing":
        hit = any(flappy.hitbox.colliderect(p.rect) for p in pipe_group)
        if hit or flappy.rect.top < 0 or flappy.rect.bottom >= GROUND_Y:
            state = "dead"

    draw_text(str(score), big_font, WHITE, SCREEN_W // 2, 60, centred=True)

    if state == "ready":
        draw_text("CLICK or SPACE to start", panel_font, WHITE,
                  SCREEN_W // 2, SCREEN_H // 2 + 120, centred=True)
    if state == "dead":
        screen.blit(button_img, button_rect)
        draw_text("press R to try again", panel_font, WHITE,
                  SCREEN_W // 2, SCREEN_H - 90, centred=True)

    if show_panel:
        draw_panel()

    pygame.display.update()

pygame.quit()