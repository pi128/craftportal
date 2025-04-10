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

# Precalculate map position
map_x = (screen_width - tile_size * map_width) // 2
map_y = (screen_height - tile_size * map_height) // 2

# Load and scale tiles once
grass_img = pygame.transform.scale(
    pygame.image.load("Sprites/Tiles/Grass/grass-1.png").convert_alpha(),
    (tile_size, tile_size),
)
path_img = pygame.transform.scale(
    pygame.image.load("Sprites/Tiles/Dirt Path/dirtpath-1.png").convert_alpha(),
    (tile_size, tile_size),
)

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

# Path-laying function
def lay_path(layout, start_x, start_y, direction, length, thickness=1):
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
                layout[y][x] = "path"

    # Store objects in a list of dictionaries

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


    barrel = pygame.image.load("Sprites/Objects/Other/barrel-medium.png").convert_alpha()

def draw_objects(screen, objects, tile_size, map_x, map_y):
    for obj in objects:
        img = pygame.transform.scale(obj["image"], (tile_size, tile_size))
        screen.blit(img, (map_x + obj["x"] * tile_size, map_y + obj["y"] * tile_size))

    tree_image = pygame.image.load("Sprites/Objects/Trees and Shrubs/tree-1.png").convert_alpha()
    
    add_object(objects, 4, 2, tree_image)

# Lay some paths
                
center_x, center_y = map_width // 2, map_height // 2
lay_path(tile_layout, center_x - 10, center_y, "horizontal", length=20, thickness=1)
lay_path(tile_layout, center_x, center_y - 5, "vertical", length=11, thickness=1)

# Draw map
def draw_map():
    for y in range(map_height):
        for x in range(map_width):
            tile = path_img if tile_layout[y][x] == "path" else grass_img
            screen.blit(tile, (map_x + x * tile_size, map_y + y * tile_size))

# Player setup
player_pos = pygame.Vector2(screen_width // 2, screen_height // 2)
facing = "down"
frame_index, frame_timer = 0, 0
frame_delay = 120
speed = 5



def will_collide(new_rect):
    for obj in objects:
        if new_rect.colliderect(obj["rect"]):
            return True
    return False

def panic_escape(player_rect, player_pos, step=5):
    directions = [
        (0, -step), (0, step), (-step, 0), (step, 0),  # up, down, left, right
        (-step, -step), (-step, step), (step, -step), (step, step)  # diagonals
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
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Calculate scaled sprite and half size for boundary cutting
    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    half_width = scaled_frame.get_width() // 2
    half_height = scaled_frame.get_height() // 2


    # Movement input
    keys = pygame.key.get_pressed()
    moved = False

    moved = False

   # Movement input
    keys = pygame.key.get_pressed()
    moved = False

        # 1. Get current frame
    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    half_width = scaled_frame.get_width() // 2
    half_height = scaled_frame.get_height() // 2


    # 1. Calculate sprite and rect FIRST
    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    half_width = scaled_frame.get_width() // 2
    half_height = scaled_frame.get_height() // 2

    player_rect = pygame.Rect(
        player_pos.x - half_width,
        player_pos.y - half_height,
        scaled_frame.get_width(),
        scaled_frame.get_height()
    )

    
 

    # Movement flags
    moved = False

        ## --- X-axis movement ---
    old_x = player_pos.x

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos.x -= speed
        facing = "left"
        moved = True
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += speed
        facing = "right"
        moved = True

    # Recalculate rect
    player_rect = pygame.Rect(
        player_pos.x - half_width,
        player_pos.y - half_height,
        scaled_frame.get_width(),
        scaled_frame.get_height()
    )

        # Roll back X if off screen or collides
    if (
        player_pos.x - half_width < 0 or
        player_pos.x + half_width > screen_width or
        will_collide(player_rect)
    ):
        player_pos.x = old_x


    # --- Y-axis movement ---
    old_y = player_pos.y

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos.y -= speed
        facing = "up"
        moved = True
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += speed
        facing = "down"
        moved = True
    if keys[pygame.K_p]:  # PANIC ESCAPE
        panic_escape(player_rect, player_pos)

    # Recalculate rect
    player_rect = pygame.Rect(
        player_pos.x - half_width,
        player_pos.y - half_height,
        scaled_frame.get_width(),
        scaled_frame.get_height()
    )

    # Roll back Y if off screen or collides
    if (
        player_pos.y - half_height < 0 or
        player_pos.y + half_height > screen_height or
        will_collide(player_rect)
    ):
        player_pos.y = old_y
                # Animation
        # Update animation frame
       # right after all movement input blocks
    if moved:
        frame_timer += dt
        if frame_timer >= frame_delay:
            frame_timer = 0
            frame_index = (frame_index + 1) % len(animations[facing])
    else:
        frame_index = 0

    # Render
    screen.fill("green")
    draw_map()
    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    screen.blit(scaled_frame, scaled_frame.get_rect(center=player_pos))
    draw_objects(screen, objects, tile_size, map_x, map_y)
    if (keys[pygame.K_q]):
        break

    pygame.display.flip()