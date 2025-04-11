import pygame, sys, os
from pathlib import Path
from pygame.locals import *

pygame.init()

# Pause Menu
# pause = False

# Start Menu
resolution = (1280,720)
img = pygame.image.load('Sprites/MineCraft/portalcraft.png')
img_rect = img.get_rect(topleft=(0,0))
img_scaled = pygame.transform.scale(img, (1280, 720))
play = False
play_screen = pygame.display.set_mode(resolution)

start = pygame.image.load('Sprites/MineCraft/start.png')
start_scaled = pygame.transform.scale(start, (300, 100))
start_rect = start_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2))

over_start = pygame.image.load('Sprites/MineCraft/over_start.png')
over_start_scaled = pygame.transform.scale(over_start, (300, 100))
over_start_rect = start_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2))

# Flash interval for buttons
flash = 30
frame = 0
highlight = True

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
mine_delay = 300 
last_mine_time = 0

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
    "diamond": pygame.transform.scale(pygame.image.load("Sprites/MineCraft/diamondblock.png").convert_alpha(), (tile_size, tile_size)),
    "empty": cave_tile_img, 
    "iron": pygame.transform.scale(pygame.image.load("Sprites/MineCraft/ironblock.png").convert_alpha(), (tile_size, tile_size)),
    "gold": pygame.transform.scale(pygame.image.load("Sprites/MineCraft/goldblock.png").convert_alpha(), (tile_size, tile_size)),
    "dirt": pygame.transform.scale(pygame.image.load("Sprites/MineCraft/dirtblock.png").convert_alpha(), (tile_size, tile_size)),
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

    # 3x3 dirtpath base area in the center
    center_x = map_width // 2
    center_y = map_height // 2
    for y in range(center_y - 1, center_y + 2):
        for x in range(center_x - 1, center_x + 2):
            layout[y][x] = "dirtpath"
            visibility[y][x] = True  # starting tiles are visible

    # Random ore generation outside the 3x3 base
    from random import randint
    for y in range(map_height):
        for x in range(map_width):
            if layout[y][x] == "stone" and randint(1, 10) <= 2:  # ~20% chance for ore
                ore_type = randint(1, 4)
                if ore_type == 1:
                    layout[y][x] = "diamond"
                elif ore_type == 2:
                    layout[y][x] = "iron"
                elif ore_type == 3:
                    layout[y][x] = "gold"
                elif ore_type == 4:
                    layout[y][x] = "coal"

    return layout, visibility
# Map creation
def create_main_room():
    layout = [["grass" for _ in range(map_width)] for _ in range(map_height)]
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
                layout[y][x] = "diamond"


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

caveentrance_image = pygame.image.load("Sprites/Tiles/Cave/CaveEntrance.png").convert_alpha()
add_object(maps["main"]["objects"], 10, 0, caveentrance_image)

gate_image = pygame.image.load("Sprites\Tiles\Dirt Path\dirtpath-4.png").convert_alpha()
add_object(maps["main"]["objects"], 19, 5, gate_image)

current_map = "main"
tile_layout = maps[current_map]["layout"]
objects = maps[current_map]["objects"]
tile_img = maps[current_map]["tile"]
visibility = maps[current_map].get("visibility", [[True]*map_width for _ in range(map_height)])


# Draw map with custom tiles
def draw_map():
    for y in range(map_height):
        for x in range(map_width):
            draw_x = map_x + x * tile_size
            draw_y = map_y + y * tile_size

            # Always draw the base tile (like cave tile for fallback)
            screen.blit(tile_img, (draw_x, draw_y))  # uses grass or cave depending on map

            tile_type = tile_layout[y][x]

            # Handle cave visibility logic
            if current_map == "cave" and not visibility[y][x]:
                tile = tile_images["stone"]
                screen.blit(tile, (draw_x, draw_y))
            else:
                if tile_type in tile_images:
                    tile = tile_images[tile_type]
                    if tile_type in ("diamond", "iron", "gold", "coal"):
                        small_tile = pygame.transform.scale(tile, (48, 48))
                        screen.blit(small_tile, (draw_x + 8, draw_y + 8))
                    else:
                        screen.blit(tile, (draw_x, draw_y))
                        
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

# Cave entrance in main
caveentrance_image = pygame.image.load("Sprites/Tiles/Cave/CaveEntrance.png").convert_alpha()
add_object(maps["main"]["objects"], 10, 0, caveentrance_image)

# Gate in main
gate_image = pygame.image.load("Sprites\Tiles\Dirt Path\dirtpath-4.png").convert_alpha()
add_object(maps["main"]["objects"], 19, 5, gate_image)


# first is there so that when you click main menu in
# the pause menu you can go back to the original loop
first = True
while first:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)

        if event.type == MOUSEBUTTONDOWN:
            if start_rect.collidepoint(event.pos) or over_start_rect.collidepoint(event.pos):
                first = False
                running = True

    play_screen.blit(img_scaled, (0, 0))
    play_screen.blit(start_scaled, start_rect.topleft)
    frame += 1
    if frame >= flash:
        highlight = not highlight
        frame = 0
    if highlight:
        play_screen.blit(over_start_scaled, over_start_rect.topleft)
    pygame.display.flip()
    clock.tick(60)

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

    current_time = pygame.time.get_ticks()

    if keys[pygame.K_e] and current_time - last_mine_time >= mine_delay:
        last_mine_time = current_time  # update the time

        dx, dy = 0, 0
        if facing == "up": dy = -1
        elif facing == "down": dy = 1
        elif facing == "left": dx = -1
        elif facing == "right": dx = 1

        tx = int((player_pos.x - map_x) // tile_size) + dx
        ty = int((player_pos.y - map_y) // tile_size) + dy

        if 0 <= tx < map_width and 0 <= ty < map_height:
            if current_map == "cave":
                target_tile = tile_layout[ty][tx]
                if target_tile in ("stone", "diamond", "iron", "gold", "coal"):
                    was_ore = target_tile in ("diamond", "iron", "gold", "coal")

                    # Reveal the tile
                    visibility[ty][tx] = True
                    tile_layout[ty][tx] = "empty"

                    # Auto-reveal ores adjacent to this one
                    if was_ore:
                        for dy_ in [-1, 0, 1]:
                            for dx_ in [-1, 0, 1]:
                                if abs(dx_) + abs(dy_) != 1:
                                    continue  # skip diagonals
                                nx, ny = tx + dx_, ty + dy_
                                if (
                                    0 <= nx < map_width and
                                    0 <= ny < map_height and
                                    tile_layout[ny][nx] in ("diamond", "iron", "gold", "coal")
                                ):
                                    visibility[ny][nx] = True
                                    

    # Check for cave entrance teleport
    if current_map == "main":
        for obj in objects:
            if obj["image"] == caveentrance_image and obj["rect"].colliderect(player_rect):

                current_map = "cave"
                tile_layout = maps["cave"]["layout"]
                objects = maps["cave"]["objects"]
                tile_img = maps["cave"]["tile"]
                visibility = maps["cave"].get("visibility", [[True] * map_width for _ in range(map_height)])

                # Set player spawn to center of cave
                player_pos.x = map_x + tile_size * (map_width // 2)
                player_pos.y = map_y + tile_size * (map_height // 2)
                break

    # Check for Gate teleport
    if current_map == "main":
        for obj in objects:
            if obj["image"] == gate_image and obj["rect"].colliderect(player_rect):

                current_map = "cave"
                tile_layout = maps["cave"]["layout"]
                objects = maps["cave"]["objects"]
                tile_img = maps["cave"]["tile"]
                visibility = maps["cave"].get("visibility", [[True] * map_width for _ in range(map_height)])

                # Set player spawn to center of cave
                player_pos.x = map_x + tile_size * (map_width // 2)
                player_pos.y = map_y + tile_size * (map_height // 2)
                break
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