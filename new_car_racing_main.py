import pygame
import random
import math
import os

pygame.init()

# =========================================================
# SCREEN
# =========================================================
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================
SKY = (105, 195, 245)
WHITE = (250, 250, 250)
BLACK = (20, 20, 20)
ROAD = (60, 60, 66)
GRASS = (45, 170, 65)
MOUNTAIN = (70, 105, 120)
ROAD_EDGE = (250, 220, 70)
RED = (225, 40, 45)
BLUE = (45, 100, 220)
ORANGE = (240, 125, 20)
PURPLE = (150, 50, 190)
CYAN = (35, 175, 160)
YELLOW = (255, 210, 25)
GREEN = (45, 220, 100)
TREE_GREEN = (30, 125, 45)
TREE_LIGHT = (40, 150, 50)
TRUNK = (105, 70, 35)

# =========================================================
# FONTS
# =========================================================
font_small = pygame.font.Font(None, max(30, H // 28))
font_medium = pygame.font.Font(None, max(50, H // 17))
font_big = pygame.font.Font(None, max(90, H // 8))

# =========================================================
# ROAD
# =========================================================
HORIZON = int(H * 0.34)

TOP_ROAD_WIDTH = int(W * 0.18)
BOTTOM_ROAD_WIDTH = int(W * 0.78)

LANES = 3


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def road_width(y):
    t = clamp(
        (y - HORIZON) / float(max(1, H - HORIZON)),
        0,
        1
    )

    return TOP_ROAD_WIDTH + (
        BOTTOM_ROAD_WIDTH - TOP_ROAD_WIDTH
    ) * t


def road_edges(y):
    width = road_width(y)

    left = W / 2 - width / 2
    right = W / 2 + width / 2

    return left, right


def lane_center(lane, y):
    left, right = road_edges(y)

    lane_width = (right - left) / LANES

    return left + lane_width * (lane + 0.5)


# =========================================================
# BEST SCORE
# =========================================================
BEST_FILE = "racing_best_score.txt"


def load_best():
    try:
        with open(BEST_FILE, "r") as file:
            return int(file.read())
    except:
        return 0


def save_best():
    try:
        with open(BEST_FILE, "w") as file:
            file.write(str(int(best_score)))
    except:
        pass


best_score = load_best()

# =========================================================
# GAME STATES
# =========================================================
COUNTDOWN = 0
PLAYING = 1
PAUSED = 2
GAMEOVER = 3

state = COUNTDOWN

countdown_start = pygame.time.get_ticks()

# =========================================================
# PLAYER
# =========================================================
PLAYER_W = int(W * 0.14)
PLAYER_H = int(H * 0.13)

player_x = W / 2
player_y = H - int(H * 0.18)

# =========================================================
# GAME VARIABLES
# =========================================================
score = 0
coins_collected = 0
nitro = 100

road_scroll = 0
enemy_timer = 0
coin_timer = 0

enemies = []
coins = []
particles = []
trees = []

# =========================================================
# TREE SYSTEM
# =========================================================
def new_tree():

    # Trees are created only outside the road.
    side = random.choice([-1, 1])

    y = random.randint(
        HORIZON + 20,
        H + 150
    )

    size = random.randint(30, 58)

    return {
        "side": side,
        "y": y,
        "size": size
    }


for i in range(26):
    trees.append(new_tree())


def tree_x(tree):
    """
    IMPORTANT:
    Tree X is calculated from its CURRENT Y.
    Therefore when perspective changes,
    tree stays outside the road.
    """

    y = tree["y"]
    size = tree["size"]

    left, right = road_edges(y)

    # Extra gap so tree cannot touch the road.
    gap = max(
        int(W * 0.035),
        int(size * 0.75)
    )

    if tree["side"] == -1:
        return left - gap
    else:
        return right + gap


def update_trees(speed):

    for tree in trees:

        tree["y"] += speed * 0.35

        if tree["y"] > H + 100:

            replacement = new_tree()

            tree["side"] = replacement["side"]
            tree["y"] = replacement["y"]
            tree["size"] = replacement["size"]


def draw_trees():

    # Draw from far to near.
    ordered = sorted(
        trees,
        key=lambda t: t["y"]
    )

    for tree in ordered:

        y = tree["y"]

        if y < HORIZON:
            continue

        t = clamp(
            (y - HORIZON) /
            float(max(1, H - HORIZON)),
            0,
            1
        )

        size = int(
            tree["size"] *
            (0.35 + 0.65 * t)
        )

        x = int(tree_x(tree))

        # Safety check:
        # Do not draw a tree if its center somehow
        # enters the road.
        left, right = road_edges(y)

        if left < x < right:
            continue

        # Trunk
        trunk_w = max(5, size // 5)

        pygame.draw.rect(
            screen,
            TRUNK,
            (
                x - trunk_w // 2,
                y - size,
                trunk_w,
                size
            )
        )

        # Tree leaves
        pygame.draw.circle(
            screen,
            TREE_GREEN,
            (
                x,
                y - size
            ),
            max(10, size // 2)
        )

        pygame.draw.circle(
            screen,
            TREE_LIGHT,
            (
                x - size // 3,
                y - size + size // 8
            ),
            max(8, size // 3)
        )

        pygame.draw.circle(
            screen,
            TREE_LIGHT,
            (
                x + size // 3,
                y - size + size // 8
            ),
            max(8, size // 3)
        )


# =========================================================
# BACKGROUND
# =========================================================
def draw_background():

    screen.fill(SKY)

    # Sun
    pygame.draw.circle(
        screen,
        (255, 230, 90),
        (
            int(W * 0.82),
            int(H * 0.12)
        ),
        int(min(W, H) * 0.055)
    )

    # Clouds
    clouds = [
        (W * .15, H * .13),
        (W * .50, H * .10),
        (W * .70, H * .18)
    ]

    for x, y in clouds:

        pygame.draw.circle(
            screen,
            WHITE,
            (int(x), int(y)),
            22
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(x + 25), int(y + 4)),
            18
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(x - 22), int(y + 5)),
            16
        )

    # Mountains
    pygame.draw.polygon(
        screen,
        MOUNTAIN,
        [
            (0, HORIZON + 5),
            (int(W * .18), int(H * .18)),
            (int(W * .34), HORIZON + 5),
            (int(W * .52), int(H * .15)),
            (int(W * .70), HORIZON + 5),
            (int(W * .86), int(H * .21)),
            (W, HORIZON + 5),
            (W, HORIZON + 80),
            (0, HORIZON + 80)
        ]
    )

    # Grass
    pygame.draw.rect(
        screen,
        GRASS,
        (
            0,
            HORIZON,
            W,
            H - HORIZON
        )
    )

    # Road
    left_top, right_top = road_edges(HORIZON)
    left_bottom, right_bottom = road_edges(H)

    pygame.draw.polygon(
        screen,
        ROAD,
        [
            (int(left_top), HORIZON),
            (int(right_top), HORIZON),
            (int(right_bottom), H),
            (int(left_bottom), H)
        ]
    )

    # Road borders
    pygame.draw.line(
        screen,
        ROAD_EDGE,
        (int(left_top), HORIZON),
        (int(left_bottom), H),
        max(5, W // 100)
    )

    pygame.draw.line(
        screen,
        ROAD_EDGE,
        (int(right_top), HORIZON),
        (int(right_bottom), H),
        max(5, W // 100)
    )


# =========================================================
# ROAD DASHES
# =========================================================
def draw_road_lines():

    for divider in range(1, LANES):

        y = (
            HORIZON
            + (road_scroll % 125)
            - 125
        )

        while y < H:

            if y >= HORIZON:

                t = clamp(
                    (y - HORIZON) /
                    float(max(1, H - HORIZON)),
                    0,
                    1
                )

                dash_h = int(10 + 65 * t)
                dash_w = max(
                    3,
                    int(W * (.006 + .012 * t))
                )

                x = lane_center(
                    divider - .5,
                    y
                )

                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        int(x - dash_w / 2),
                        int(y),
                        dash_w,
                        dash_h
                    )
                )

                y += dash_h + int(55 + 65 * t)

            else:
                y += 70


# =========================================================
# PLAYER CAR
# =========================================================
def draw_player():

    x = int(player_x)
    y = int(player_y)

    w = PLAYER_W
    h = PLAYER_H

    # Shadow
    pygame.draw.ellipse(
        screen,
        (25, 25, 25),
        (
            x - w // 2,
            y + h // 3,
            w,
            h // 4
        )
    )

    # Body
    pygame.draw.rect(
        screen,
        RED,
        (
            x - w // 2,
            y - h // 2,
            w,
            h
        ),
        border_radius=max(5, w // 9)
    )

    # White stripe
    pygame.draw.rect(
        screen,
        WHITE,
        (
            x - max(3, w // 18),
            y - h // 2,
            max(6, w // 9),
            h
        )
    )

    # Windshield
    pygame.draw.polygon(
        screen,
        (30, 75, 100),
        [
            (x - w // 3, y - h // 5),
            (x + w // 3, y - h // 5),
            (x + w // 5, y + h // 10),
            (x - w // 5, y + h // 10)
        ]
    )

    # Headlights
    light_w = max(5, w // 7)
    light_h = max(4, h // 10)

    pygame.draw.rect(
        screen,
        (255, 245, 160),
        (
            x - w // 2 + w // 9,
            y - h // 2 + h // 9,
            light_w,
            light_h
        )
    )

    pygame.draw.rect(
        screen,
        (255, 245, 160),
        (
            x + w // 2 - w // 9 - light_w,
            y - h // 2 + h // 9,
            light_w,
            light_h
        )
    )

    # Spoiler
    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - w // 3,
            y + h // 3,
            2 * w // 3,
            max(4, h // 14)
        )
    )

    # Wheels
    wheel_w = max(8, w // 7)
    wheel_h = max(15, h // 3)

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - w // 2 - wheel_w // 3,
            y - h // 3,
            wheel_w,
            wheel_h
        )
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + w // 2 - wheel_w * 2 // 3,
            y - h // 3,
            wheel_w,
            wheel_h
        )
    )

    # Nitro flame
    if nitro > 0:

        flame_length = random.randint(15, 30)

        pygame.draw.polygon(
            screen,
            ORANGE,
            [
                (x - w // 5, y + h // 2),
                (x + w // 5, y + h // 2),
                (x, y + h // 2 + flame_length)
            ]
        )


# =========================================================
# ENEMY CAR
# =========================================================
def draw_enemy(x, y, scale, color):

    w = max(
        18,
        int(PLAYER_W * scale)
    )

    h = max(
        28,
        int(PLAYER_H * scale)
    )

    x = int(x)
    y = int(y)

    # Shadow
    pygame.draw.ellipse(
        screen,
        BLACK,
        (
            x - w // 2,
            y + h // 4,
            w,
            max(5, h // 5)
        )
    )

    # Body
    pygame.draw.rect(
        screen,
        color,
        (
            x - w // 2,
            y - h // 2,
            w,
            h
        ),
        border_radius=max(3, w // 8)
    )

    # Windshield
    pygame.draw.polygon(
        screen,
        (30, 75, 95),
        [
            (x - w // 3, y - h // 5),
            (x + w // 3, y - h // 5),
            (x + w // 5, y + h // 10),
            (x - w // 5, y + h // 10)
        ]
    )

    # Lights
    lw = max(3, w // 7)
    lh = max(3, h // 10)

    pygame.draw.rect(
        screen,
        (255, 240, 150),
        (
            x - w // 2 + w // 8,
            y - h // 2 + h // 10,
            lw,
            lh
        )
    )

    pygame.draw.rect(
        screen,
        (255, 240, 150),
        (
            x + w // 2 - w // 8 - lw,
            y - h // 2 + h // 10,
            lw,
            lh
        )
    )


# =========================================================
# COIN
# =========================================================
def draw_coin(x, y, scale):

    radius = max(
        6,
        int(18 * scale)
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (int(x), int(y)),
        radius
    )

    pygame.draw.circle(
        screen,
        (255, 240, 100),
        (int(x), int(y)),
        max(2, radius // 2)
    )


# =========================================================
# PARTICLES
# =========================================================
def make_crash_particles(x, y):

    for i in range(55):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            2,
            9
        )

        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(20, 55),
            "size": random.randint(3, 8)
        })


def update_particles():

    for p in particles[:]:

        p["x"] += p["vx"]
        p["y"] += p["vy"]

        p["vy"] += .15

        p["life"] -= 1

        if p["life"] <= 0:

            particles.remove(p)

        else:

            pygame.draw.circle(
                screen,
                ORANGE,
                (
                    int(p["x"]),
                    int(p["y"])
                ),
                p["size"]
            )


# =========================================================
# ENEMY SPAWN
# =========================================================
def spawn_enemy():

    # ALWAYS BELOW THE HORIZON.
    spawn_y = HORIZON + random.randint(
        35,
        70
    )

    lane_list = [0, 1, 2]
    random.shuffle(lane_list)

    selected_lane = None

    for lane in lane_list:

        free = True

        for enemy in enemies:

            if (
                enemy["lane"] == lane
                and enemy["y"] < HORIZON + 230
            ):
                free = False
                break

        if free:

            selected_lane = lane
            break

    if selected_lane is None:
        return

    colors = [
        BLUE,
        ORANGE,
        PURPLE,
        CYAN
    ]

    enemies.append({
        "lane": selected_lane,
        "y": spawn_y,
        "speed": random.uniform(.75, 1.05),
        "color": random.choice(colors)
    })


# =========================================================
# COIN SPAWN
# =========================================================
def spawn_coin():

    coins.append({
        "lane": random.randint(0, 2),
        "y": HORIZON + random.randint(60, 150)
    })


# =========================================================
# BUTTONS
# =========================================================
left_button = pygame.Rect(
    int(W * .04),
    H - int(H * .14),
    int(W * .20),
    int(H * .09)
)

right_button = pygame.Rect(
    int(W * .28),
    H - int(H * .14),
    int(W * .20),
    int(H * .09)
)

nitro_button = pygame.Rect(
    W - int(W * .25),
    H - int(H * .14),
    int(W * .21),
    int(H * .09)
)

pause_button = pygame.Rect(
    W - int(W * .13),
    int(H * .035),
    int(W * .09),
    int(H * .065)
)


def draw_buttons():

    pygame.draw.rect(
        screen,
        (35, 35, 35),
        left_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 35, 35),
        right_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 35, 35),
        nitro_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 35, 35),
        pause_button,
        border_radius=8
    )

    text = font_medium.render(
        "<",
        True,
        WHITE
    )

    screen.blit(
        text,
        text.get_rect(
            center=left_button.center
        )
    )

    text = font_medium.render(
        ">",
        True,
        WHITE
    )

    screen.blit(
        text,
        text.get_rect(
            center=right_button.center
        )
    )

    text = font_small.render(
        "NITRO",
        True,
        WHITE
    )

    screen.blit(
        text,
        text.get_rect(
            center=nitro_button.center
        )
    )

    text = font_small.render(
        "II",
        True,
        WHITE
    )

    screen.blit(
        text,
        text.get_rect(
            center=pause_button.center
        )
    )


# =========================================================
# RESET GAME
# =========================================================
def reset_game():

    global state
    global countdown_start
    global score
    global coins_collected
    global nitro
    global player_x
    global road_scroll
    global enemy_timer
    global coin_timer

    score = 0
    coins_collected = 0
    nitro = 100

    player_x = W / 2

    road_scroll = 0
    enemy_timer = 0
    coin_timer = 0

    enemies.clear()
    coins.clear()
    particles.clear()

    state = COUNTDOWN

    countdown_start = pygame.time.get_ticks()


# =========================================================
# MAIN LOOP
# =========================================================
running = True

while running:

    dt = clock.tick(60) / 1000.0

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            elif event.key == pygame.K_p:

                if state == PLAYING:
                    state = PAUSED

                elif state == PAUSED:
                    state = PLAYING

            elif event.key == pygame.K_r:

                if state == GAMEOVER:
                    reset_game()

    # -----------------------------------------------------
    # BACKGROUND
    # -----------------------------------------------------
    draw_background()

    # =====================================================
    # COUNTDOWN
    # =====================================================
    if state == COUNTDOWN:

        draw_trees()
        draw_road_lines()
        draw_player()

        elapsed = (
            pygame.time.get_ticks()
            - countdown_start
        ) / 1000.0

        if elapsed < 1:
            message = "3"

        elif elapsed < 2:
            message = "2"

        elif elapsed < 3:
            message = "1"

        elif elapsed < 3.7:
            message = "GO!"

        else:
            state = PLAYING
            message = ""

        if message:

            text = font_big.render(
                message,
                True,
                WHITE
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(W // 2, H // 2)
                )
            )

    # =====================================================
    # PLAYING
    # =====================================================
    elif state == PLAYING:

        # -------------------------------------------------
        # DIFFICULTY
        # -------------------------------------------------
        difficulty = min(
            2.2,
            1.0 + score / 900.0
        )

        speed = 7.0 * difficulty

        # -------------------------------------------------
        # TREES
        # -------------------------------------------------
        update_trees(speed)

        # Trees are drawn BEFORE cars.
        draw_trees()

        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------
        keys = pygame.key.get_pressed()

        move_left = (
            keys[pygame.K_LEFT]
            or keys[pygame.K_a]
        )

        move_right = (
            keys[pygame.K_RIGHT]
            or keys[pygame.K_d]
        )

        nitro_active = keys[pygame.K_SPACE]

        mouse_down = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        if mouse_down:

            if left_button.collidepoint(mouse_pos):
                move_left = True

            if right_button.collidepoint(mouse_pos):
                move_right = True

            if nitro_button.collidepoint(mouse_pos):
                nitro_active = True

            if pause_button.collidepoint(mouse_pos):
                state = PAUSED

        # -------------------------------------------------
        # PLAYER MOVEMENT
        # -------------------------------------------------
        if move_left:
            player_x -= W * .85 * dt

        if move_right:
            player_x += W * .85 * dt

        # -------------------------------------------------
        # NITRO
        # -------------------------------------------------
        if nitro_active and nitro > 0:

            speed *= 1.6
            nitro -= 45 * dt

        else:

            nitro += 8 * dt

        nitro = clamp(
            nitro,
            0,
            100
        )

        # -------------------------------------------------
        # PLAYER ROAD LIMIT
        # -------------------------------------------------
        left_edge, right_edge = road_edges(
            player_y
        )

        player_x = clamp(
            player_x,
            left_edge + PLAYER_W * .55,
            right_edge - PLAYER_W * .55
        )

        # -------------------------------------------------
        # ROAD SCROLL
        # -------------------------------------------------
        road_scroll += speed

        # Score
        score += speed * dt * .55

        # -------------------------------------------------
        # ROAD LINES
        # -------------------------------------------------
        draw_road_lines()

        # -------------------------------------------------
        # ENEMY SPAWN
        # -------------------------------------------------
        enemy_timer += dt

        enemy_delay = max(
            .55,
            1.25 - score / 1800
        )

        if enemy_timer >= enemy_delay:

            enemy_timer = 0

            spawn_enemy()

        # -------------------------------------------------
        # COIN SPAWN
        # -------------------------------------------------
        coin_timer += dt

        if coin_timer >= 1.5:

            coin_timer = 0

            if random.random() < .8:
                spawn_coin()

        # -------------------------------------------------
        # PLAYER COLLISION RECT
        # -------------------------------------------------
        player_rect = pygame.Rect(
            int(player_x - PLAYER_W * .35),
            int(player_y - PLAYER_H * .40),
            int(PLAYER_W * .70),
            int(PLAYER_H * .80)
        )

        crashed = False

        # =================================================
        # ENEMIES
        # =================================================
        for enemy in enemies[:]:

            enemy["y"] += (
                speed *
                enemy["speed"]
            )

            y = enemy["y"]

            # Never draw above road horizon.
            if y < HORIZON:
                continue

            t = clamp(
                (y - HORIZON) /
                float(max(1, H - HORIZON)),
                0,
                1
            )

            scale = .25 + .75 * t

            # Enemy X is ALWAYS calculated from
            # its lane and CURRENT road position.
            x = lane_center(
                enemy["lane"],
                y
            )

            draw_enemy(
                x,
                y,
                scale,
                enemy["color"]
            )

            ew = max(
                15,
                int(PLAYER_W * scale)
            )

            eh = max(
                25,
                int(PLAYER_H * scale)
            )

            enemy_rect = pygame.Rect(
                int(x - ew * .35),
                int(y - eh * .38),
                int(ew * .70),
                int(eh * .76)
            )

            if player_rect.colliderect(
                enemy_rect
            ):
                crashed = True

            if y > H + 100:

                enemies.remove(enemy)

                score += 10

        # =================================================
        # COINS
        # =================================================
        for coin in coins[:]:

            coin["y"] += speed

            y = coin["y"]

            if y < HORIZON:
                continue

            t = clamp(
                (y - HORIZON) /
                float(max(1, H - HORIZON)),
                0,
                1
            )

            scale = .35 + .65 * t

            x = lane_center(
                coin["lane"],
                y
            )

            draw_coin(
                x,
                y,
                scale
            )

            radius = max(
                7,
                int(18 * scale)
            )

            coin_rect = pygame.Rect(
                int(x - radius),
                int(y - radius),
                radius * 2,
                radius * 2
            )

            if player_rect.colliderect(
                coin_rect
            ):

                coins.remove(coin)

                coins_collected += 1
                score += 25

                nitro = min(
                    100,
                    nitro + 10
                )

                continue

            if y > H + 80:

                coins.remove(coin)

        # =================================================
        # CRASH
        # =================================================
        if crashed:

            make_crash_particles(
                player_x,
                player_y
            )

            state = GAMEOVER

            if int(score) > best_score:

                best_score = int(score)

                save_best()

        # Player on top of everything.
        draw_player()

        update_particles()

        # =================================================
        # HUD
        # =================================================
        text = font_small.render(
            "SCORE: " + str(int(score)),
            True,
            WHITE
        )

        screen.blit(
            text,
            (20, 18)
        )

        text = font_small.render(
            "COINS: " + str(coins_collected),
            True,
            WHITE
        )

        screen.blit(
            text,
            (
                20,
                18 + font_small.get_height()
            )
        )

        text = font_small.render(
            "BEST: " + str(best_score),
            True,
            WHITE
        )

        screen.blit(
            text,
            (
                20,
                18 + font_small.get_height() * 2
            )
        )

        # Nitro bar
        bar_x = int(W * .43)
        bar_y = 20
        bar_w = int(W * .28)
        bar_h = 20

        pygame.draw.rect(
            screen,
            BLACK,
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h
            )
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                bar_x,
                bar_y,
                int(bar_w * nitro / 100),
                bar_h
            )
        )

        draw_buttons()

    # =====================================================
    # PAUSE
    # =====================================================
    elif state == PAUSED:

        draw_trees()
        draw_road_lines()

        # Draw existing enemies
        for enemy in enemies:

            y = enemy["y"]

            if y >= HORIZON:

                t = clamp(
                    (y - HORIZON) /
                    float(max(1, H - HORIZON)),
                    0,
                    1
                )

                scale = .25 + .75 * t

                x = lane_center(
                    enemy["lane"],
                    y
                )

                draw_enemy(
                    x,
                    y,
                    scale,
                    enemy["color"]
                )

        # Draw coins
        for coin in coins:

            y = coin["y"]

            if y >= HORIZON:

                t = clamp(
                    (y - HORIZON) /
                    float(max(1, H - HORIZON)),
                    0,
                    1
                )

                scale = .35 + .65 * t

                x = lane_center(
                    coin["lane"],
                    y
                )

                draw_coin(
                    x,
                    y,
                    scale
                )

        draw_player()

        overlay = pygame.Surface(
            (W, H),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 165)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        text = font_big.render(
            "PAUSED",
            True,
            WHITE
        )

        screen.blit(
            text,
            text.get_rect(
                center=(W // 2, H // 2)
            )
        )

        text = font_small.render(
            "PRESS P TO CONTINUE",
            True,
            WHITE
        )

        screen.blit(
            text,
            text.get_rect(
                center=(
                    W // 2,
                    H // 2 + 80
                )
            )
        )

    # =====================================================
    # GAME OVER
    # =====================================================
    elif state == GAMEOVER:

        draw_trees()
        draw_road_lines()

        for enemy in enemies:

            y = enemy["y"]

            if y >= HORIZON:

                t = clamp(
                    (y - HORIZON) /
                    float(max(1, H - HORIZON)),
                    0,
                    1
                )

                scale = .25 + .75 * t

                x = lane_center(
                    enemy["lane"],
                    y
                )

                draw_enemy(
                    x,
                    y,
                    scale,
                    enemy["color"]
                )

        draw_player()

        update_particles()

        overlay = pygame.Surface(
            (W, H),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        text = font_big.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            text,
            text.get_rect(
                center=(W // 2, H * .32)
            )
        )

        text = font_medium.render(
            "SCORE: " + str(int(score)),
            True,
            WHITE
        )

        screen.blit(
            text,
            text.get_rect(
                center=(W // 2, H * .47)
            )
        )

        text = font_medium.render(
            "BEST: " + str(best_score),
            True,
            YELLOW
        )

        screen.blit(
            text,
            text.get_rect(
                center=(W // 2, H * .55)
            )
        )

        text = font_small.render(
            "TAP SCREEN OR PRESS R",
            True,
            WHITE
        )

        screen.blit(
            text,
            text.get_rect(
                center=(W // 2, H * .70)
            )
        )

        # Tap to restart
        if pygame.mouse.get_pressed()[0]:

            reset_game()

    # =====================================================
    # DISPLAY
    # =====================================================
    pygame.display.flip()

pygame.quit()