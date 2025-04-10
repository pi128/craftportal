import pygame, sys, os
from pathlib import Path

pygame.init()

# Setup
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

tile_size = 64
map_width = 20
map_height = 11

# Animation + Input delay config
frame_delay = 150  # milli
map_switch_delay = 500 
map_switch_timer = 0

# Precalculate map position
map_x = (screen_width - tile_size * map_width) // 2
map_y = (screen_height - tile_size * map_height) // 2

# Tile image loader

tile_images = {
    "dirtpath": pygame.transform.scale(
        pygame.image.load("Sprites/Tiles/Dirt Path/dirtpath-1.png").convert_alpha(),
        (tile_size, tile_size)
    ),
    "cavepath": pygame.transform.scale(
        pygame.image.load("Sprites/Tiles/Cave/cavepath-1.png").convert_alpha(),
        (tile_size, tile_size)
    ),
}

# Character animations
def load_animation_list(file_list):
    return [pygame.image.load(f"Sprites/Characters/{file}").convert_alpha() for file in file_list]

animations = {
    "down": load_animation_list(["ForwardFacing.png", "ForwardWalk1.png", "ForwardWalk2.png"]),
    "up": load_animation_list(["BackFacing.png", "BackWalking1.png", "BackWalking2.png"]),
    "left": load_animation_list(["LeftFacing.png", "LeftWalking1.png", "LeftWalking2.png"]),
    "right": load_animation_list(["RightFacing.png", "RightWalking1.png", "RightWalking2.png"]),
}

# Tile layout initialization
tile_layout = [["" for _ in range(map_width)] for _ in range(map_height)]

# Default background tiles
grass_img = pygame.transform.scale(
    pygame.image.load("Sprites/Tiles/Grass/grass-1.png").convert_alpha(),
    (tile_size, tile_size),
)

cave_tile_img = pygame.transform.scale(
    pygame.image.load("Sprites/Tiles/Cave/CaveTile1.png").convert_alpha(),
    (tile_size, tile_size),
)

tile_images = {
    "stone": pygame.transform.scale(pygame.image.load("Sprites/MineCraft/stoneblock.png").convert_alpha(), (tile_size, tile_size)),
    "ore": pygame.transform.scale(pygame.image.load("Sprites/MineCraft/diamondblock.png").convert_alpha(), (tile_size, tile_size)),
    "empty": pygame.Surface((tile_size, tile_size))  # No comma here
}

# Path-laying function
def lay_path(layout, start_x, start_y, direction, length, thickness=1, tile_type="dirt"):
    half_thick = thickness // 2
    for i in range(length):
        for t in range(-half_thick, half_thick + 1):
            x, y = start_x, start_y
            if direction == "horizontal":
                x += i
                y += t
            elif direction == "vertical":
                x += t
                y += i
            if 0 <= x < map_width and 0 <= y < map_height:
                layout[y][x] = tile_type

# Store objects
objects = []

def add_object(obj_list, tile_x, tile_y, image):
    rect = pygame.Rect(
        map_x + tile_x * tile_size,
        map_y + tile_y * tile_size,
        tile_size,
        tile_size
    )
    obj = {
        "x": tile_x,
        "y": tile_y,
        "image": image,
        "rect": rect
    }
    obj_list.append(obj)

def draw_objects(screen, objects, tile_size, map_x, map_y):
    for obj in objects:
        img = pygame.transform.scale(obj["image"], (tile_size, tile_size))
        screen.blit(img, (map_x + obj["x"] * tile_size, map_y + obj["y"] * tile_size))

def generate_mining_map():
    layout = [["stone" for _ in range(map_width)] for _ in range(map_height)]
    visibility = [[False for _ in range(map_width)] for _ in range(map_height)]

    # 3x3 dirt base area in the center
    center_x = map_width // 2
    center_y = map_height // 2
    for y in range(center_y - 1, center_y + 2):
        for x in range(center_x - 1, center_x + 2):
            layout[y][x] = "dirt"
            visibility[y][x] = True  # starting tiles are visible

    # Random ore generation outside the 3x3 base
    from random import randint
    for y in range(map_height):
        for x in range(map_width):
            if layout[y][x] == "stone" and randint(1, 12) == 1:
                layout[y][x] = "ore"

    return layout, visibility
# Map creation
def create_main_room():
    layout = [["" for _ in range(map_width)] for _ in range(map_height)]
    lay_path(layout, 5, 5, "horizontal", 10, tile_type="dirtpath")
    lay_path(layout, 10, 2, "vertical", 6, tile_type="dirtpath")
    
    objects = []
    tree_image = pygame.image.load("Sprites/Objects/Trees and Shrubs/tree-1.png").convert_alpha()
    add_object(objects, 4, 2, tree_image)

    return layout, objects

def create_cave_room():
    layout = [["" for _ in range(map_width)] for _ in range(map_height)]
    
    # Fill top half with stone, bottom half with dirt
    for y in range(map_height):
        for x in range(map_width):
            if y < map_height // 2:
                layout[y][x] = "stone"
            else:
                layout[y][x] = "dirt"
    
    # Random ore in the stone part
    from random import randint
    for y in range(map_height // 2):
        for x in range(map_width):
            if randint(1, 12) == 1:
                layout[y][x] = "ore"

    # Place some object for visual testing
    objects = []
    barrel_image = pygame.image.load("Sprites/Objects/Other/barrel-medium.png").convert_alpha()
    add_object(objects, 10, map_height - 3, barrel_image)

    return layout, objects

main_layout, main_objects = create_main_room()

cave_layout, cave_visibility = generate_mining_map()
cave_objects = []

maps = {
    "main": {
        "layout": main_layout,
        "objects": main_objects,
        "tile": grass_img
    },
    "cave": {
        "layout": cave_layout,
        "objects": cave_objects,
        "tile": cave_tile_img,
        "visibility": cave_visibility
    }
}

current_map = "main"
tile_layout = maps[current_map]["layout"]
objects = maps[current_map]["objects"]
tile_img = maps[current_map]["tile"]
visibility = maps[current_map].get("visibility", [[True]*map_width for _ in range(map_height)])

# Draw map with custom tiles
def draw_map():
    for y in range(map_height):
        for x in range(map_width):
            tile_type = tile_layout[y][x]
            if tile_type in tile_images:
                tile = tile_images[tile_type]
            else:
                tile = tile_img
            screen.blit(tile, (map_x + x * tile_size, map_y + y * tile_size))

# Player setup
player_pos = pygame.Vector2(screen_width // 2, screen_height // 2)
facing = "down"
frame_index, frame_timer = 0, 0
speed = 5

def will_collide(new_rect):
    for obj in objects:
        if new_rect.colliderect(obj["rect"]):
            return True
    return False

def panic_escape(player_rect, player_pos, step=5):
    directions = [
        (0, -step), (0, step), (-step, 0), (step, 0),
        (-step, -step), (-step, step), (step, -step), (step, step)
    ]
    for dx, dy in directions:
        test_rect = player_rect.move(dx, dy)
        if not will_collide(test_rect):
            player_pos.x += dx
            player_pos.y += dy
            break

# Main loop
running = True
while running:
    mapTime = clock.tick(60)
    map_switch_timer += mapTime

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    half_width = scaled_frame.get_width() // 2
    half_height = scaled_frame.get_height() // 2

    keys = pygame.key.get_pressed()
    moved = False

    player_rect = pygame.Rect(
        player_pos.x - half_width,
        player_pos.y - half_height,
        scaled_frame.get_width(),
        scaled_frame.get_height()
    )

    old_x = player_pos.x
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos.x -= speed
        facing = "left"
        moved = True
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += speed
        facing = "right"
        moved = True

    player_rect.x = player_pos.x - half_width

    if (
        player_pos.x - half_width < 0 or
        player_pos.x + half_width > screen_width or
        will_collide(player_rect)
    ):
        player_pos.x = old_x

    old_y = player_pos.y
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos.y -= speed
        facing = "up"
        moved = True
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += speed
        facing = "down"
        moved = True

    if keys[pygame.K_p]:
        panic_escape(player_rect, player_pos)

    if keys[pygame.K_m] and map_switch_timer >= map_switch_delay:
        current_map = "cave" if current_map == "main" else "main"
        tile_layout = maps[current_map]["layout"]
        objects = maps[current_map]["objects"]
        tile_img = maps[current_map]["tile"]
        visibility = maps[current_map].get("visibility", [[True]*map_width for _ in range(map_height)])
        map_switch_timer = 0

    player_rect.y = player_pos.y - half_height

    if (
        player_pos.y - half_height < 0 or
        player_pos.y + half_height > screen_height or
        will_collide(player_rect)
    ):
        player_pos.y = old_y

    # Animate
    if moved:
        frame_timer += mapTime
        if frame_timer >= frame_delay:
            frame_timer = 0
            frame_index = (frame_index + 1) % len(animations[facing])
    else:
        frame_index = 0

    if keys[pygame.K_e]:
        dx, dy = 0, 0
        if facing == "up":
            dy = -1
        elif facing == "down":
            dy = 1
        elif facing == "left":
            dx = -1
        elif facing == "right":
            dx = 1

        tx = int((player_pos.x - map_x) // tile_size) + dx
        ty = int((player_pos.y - map_y) // tile_size) + dy

        if 0 <= tx < map_width and 0 <= ty < map_height:
            if tile_layout[ty][tx] in ("stone", "ore"):
                tile_layout[ty][tx] = "empty"
                if current_map == "cave":
                    visibility[ty][tx] = True


    # Draw
    screen.fill((0, 0, 0))
    draw_map()
    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    screen.blit(scaled_frame, scaled_frame.get_rect(center=player_pos))
    draw_objects(screen, objects, tile_size, map_x, map_y)

    if keys[pygame.K_q]:
        break

    pygame.display.flip()