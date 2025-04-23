import pygame, sys, os
from pathlib import Path
from pygame.locals import *

pygame.init()
pygame.mixer.init()
resolution = (1280,720)

# Pause Menu
pause = False
def draw_pause():
    pygame.draw.rect(surface, (128, 128, 128, 150), [0, 0, resolution[0], resolution[1]])
    screen.blit(surface, (0,0))

game_pause_img = pygame.image.load('Sprites/MineCraft/game_paused.png')
game_pause_scaled = pygame.transform.scale(game_pause_img, (500,200))
game_pause_rect = game_pause_img.get_rect(center=(resolution[0]//2-125, resolution[1]//2-250))

pause_x_img = pygame.image.load('Sprites/MineCraft/x_out.png')
pause_x_scaled = pygame.transform.scale(pause_x_img, (128,90))
pause_x_rect = pause_x_scaled.get_rect(topleft=(0,0))

pause_quit_img = pygame.image.load('Sprites/MineCraft/pause_quit.png')
pause_quit_scaled =  pygame.transform.scale(pause_quit_img, (300,100))
pause_quit_rect = pause_quit_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2))

main_menu_img = pygame.image.load('Sprites/MineCraft/main_menu.png')
main_menu_scaled = pygame.transform.scale(main_menu_img, (300,100))
main_menu_rect = main_menu_scaled.get_rect(center=(resolution[0]//2, 465))

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

settings_img = pygame.image.load('Sprites/MineCraft/settings.png')
settings_scaled = pygame.transform.scale(settings_img, (300, 100))
settings_rect = settings_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2+105))

over_settings_img = pygame.image.load('Sprites/MineCraft/over_settings.png')
over_settings_scaled = pygame.transform.scale(over_settings_img, (300, 100))
over_settings_rect = over_settings_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2+105))

quit_img = pygame.image.load('Sprites/MineCraft/quit.png')
quit_scaled = pygame.transform.scale(quit_img, (300, 100))
quit_rect = quit_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2+210))

over_quit_img = pygame.image.load('Sprites/MineCraft/over_quit.png')
over_quit_scaled = pygame.transform.scale(over_quit_img, (300, 100))
over_quit_rect = over_quit_scaled.get_rect(center=(resolution[0]//2, resolution[1]//2+210))

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
mining = False
mining_timer = 0
mining_index = 0

craft_message = ""
craft_message_timer = 0
CRAFT_MESSAGE_DURATION = 2000  # milliseconds

has_portal_gun = False
portal_gun_message = ""
portal_gun_message_timer = 0
PORTAL_MESSAGE_DURATION = 2000  # 2 seconds

can_craft = True

mining_durations = {
    "stone": 500,
    "iron": 800,
    "gold": 1000,
    "diamond": 1500,
}

ore_counts = {
    "diamond": 0,
    "iron": 0,
    "gold": 0,
    "stone": 0,
    "wood": 0
}

has_portal_gun = False
portal_gun_message = ""
portal_gun_timer = 0

# Track mined overlay state
persistent_overlays = {}  # {(tx, ty): overlay_image}
# Later:
mining_overlays = [
    pygame.image.load(f"Sprites/MineCraft/MiningNum{i}.png").convert_alpha()
    for i in range(1, 11)
]

 
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

mining_overlays = [
    pygame.image.load(f"Sprites/MineCraft/MiningNum{i}.png").convert_alpha()
    for i in range(1, 11)
]

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
    visual_rect = pygame.Rect(
        map_x + tile_x * tile_size,
        map_y + tile_y * tile_size,
        tile_size,
        tile_size
    )
    
    # Only collide with the "trunk" (center bottom quarter of tree tile)
    collider_rect = pygame.Rect(
        visual_rect.x + tile_size // 4 ,
        visual_rect.y + tile_size // 2,
        tile_size // 2,
        tile_size // 2
    )

    obj = {
        "x": tile_x,
        "y": tile_y,
        "image": image,
        "rect": collider_rect
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
            visibility[y][x] = True

    from random import shuffle, randint

    # Guaranteed ore placements
    guaranteed_ores = ["diamond"] * 5 + ["iron"] * 10 + ["gold"] * 8
    shuffle(guaranteed_ores)

    # Find all stone positions
    stone_positions = [(x, y) for y in range(map_height) for x in range(map_width) if layout[y][x] == "stone"]
    shuffle(stone_positions)

    # Place guaranteed ores
    for ore in guaranteed_ores:
        if stone_positions:
            x, y = stone_positions.pop()
            layout[y][x] = ore

    # Add more iron/gold randomly (about 20% of remaining stone tiles)
    for x, y in stone_positions:
        roll = randint(1, 10)
        if roll <= 3:  # 30% chance to add more ore
            layout[y][x] = "iron" if roll <= 2 else "gold"

    return layout, visibility
#Weirdly needed to be on its own
tree_image = pygame.image.load("Sprites/Objects/Trees and Shrubs/tree-1.png").convert_alpha()
crafting_table_image = pygame.image.load("Sprites/MineCraft/craftingTable1.png").convert_alpha()

# Map creation
def create_main_room():

    
    layout = [["grass" for _ in range(map_width)] for _ in range(map_height)]
    lay_path(layout, 5, 5, "horizontal", 10, tile_type="dirtpath")
    lay_path(layout, 10, 2, "vertical", 6, tile_type="dirtpath")
    
    objects = []
    from random import randint

    # Place 10 trees randomly on grass tiles
    tree_count = 10
    for _ in range(tree_count):
        placed = False
        while not placed:
            tx = randint(0, map_width - 1)
            ty = randint(0, map_height - 1)
            if layout[ty][tx] == "grass":
                add_object(objects, tx, ty, tree_image)
                placed = True
   
    add_object(objects, 4, 2, tree_image)

  
    add_object(objects, 8, 5, crafting_table_image)

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

gate_image = pygame.image.load("Sprites/Tiles/Dirt Path/dirtpath-4.png").convert_alpha()
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
                    screen.blit(tile, (draw_x, draw_y))
                else:
                    tile = tile_img 
                    screen.blit(tile, (draw_x, draw_y))
                # Draw persistent mining overlay if one was left behind
                if current_map == "cave" and (x, y) in persistent_overlays:
                    overlay = pygame.transform.scale(persistent_overlays[(x, y)], (tile_size, tile_size))
                    screen.blit(overlay, (draw_x, draw_y))
                
                        
# Player setup
player_pos = pygame.Vector2(screen_width // 2, screen_height // 2)
facing = "down"
frame_index, frame_timer = 0, 0
speed = 5
player_tool_level = 1  # 1: Wood, 2: Stone, 3: Iron, 4: Diamond

ore_hardness = {
    "stone": 2,    #  New! stone requires tool level 2
    "iron": 3,
    "gold": 3,
    "diamond": 4
}


def will_collide(new_rect):
    # Object collisions
    for obj in objects:
        if new_rect.colliderect(obj["rect"]):
            return True

    # Tile collisions (e.g., stone)
    player_tile_y = int(player_pos.y // tile_size)
    player_tile_x = int(player_pos.x // tile_size)
    # Determine if near crafting table
    can_craft = False
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            ny = player_tile_y + dy
            nx = player_tile_x + dx
            if 0 <= ny < map_height and 0 <= nx < map_width:
                if tile_layout[ny][nx] == "crafting_table":
                    can_craft = True
                    break
    if can_craft:
        if player_tool_level == 1 and ore_counts["wood"] >= 3:
            ore_counts["wood"] -= 3
            player_tool_level = 2
            craft_message = "Crafted Stone Tool!"
            craft_message_timer = pygame.time.get_ticks()

        elif player_tool_level == 2 and ore_counts["stone"] >= 5:
            ore_counts["stone"] -= 5
            player_tool_level = 3
            craft_message = "Crafted Iron Tool!"
            craft_message_timer = pygame.time.get_ticks()

        elif player_tool_level == 3 and ore_counts["iron"] >= 5:
            ore_counts["iron"] -= 5
            player_tool_level = 4
            craft_message = "Crafted Gold Tool!"
            craft_message_timer = pygame.time.get_ticks()

        elif player_tool_level == 4 and ore_counts["gold"] >= 5:
            ore_counts["gold"] -= 5
            player_tool_level = 5
            craft_message = "Crafted Diamond Tool!"
            craft_message_timer = pygame.time.get_ticks()

        else:
            craft_message = "Not enough materials"
            craft_message_timer = pygame.time.get_ticks()

        can_craft = False  # prevent holding space to spam craft
    global has_portal_gun



# Cave entrance in main
caveentrance_image = pygame.image.load("Sprites/Tiles/Cave/CaveEntrance.png").convert_alpha()
add_object(maps["main"]["objects"], 10, 0, caveentrance_image)

# Gate in main
gate_image = pygame.image.load("Sprites/Tiles/Dirt Path/dirtpath-4.png").convert_alpha()
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
                click_sound = pygame.mixer.Sound('Sprites/MineCraft/click_sound.wav')
                click_sound.play()
                first = False
                running = True
            if quit_rect.collidepoint(event.pos) or over_quit_rect.collidepoint(event.pos):
                click_sound = pygame.mixer.Sound('Sprites/MineCraft/click_sound.wav')
                click_sound.play()
                sys.exit(0)

    play_screen.blit(img_scaled, (0, 0))
    play_screen.blit(start_scaled, start_rect.topleft)
    play_screen.blit(settings_scaled, settings_rect.topleft)
    play_screen.blit(quit_scaled, quit_rect.topleft)
    frame += 1
    if frame >= flash:
        highlight = not highlight
        frame = 0
    if highlight:
        play_screen.blit(over_start_scaled, over_start_rect.topleft)
        play_screen.blit(over_settings_scaled, over_settings_rect.topleft)
        play_screen.blit(over_quit_scaled, over_quit_rect.topleft)
    pygame.display.flip()
    clock.tick(60)

# Main loop
running = True
can_move = True
while running:
    mapTime = clock.tick(60)
    can_move = not mining
    map_switch_timer += mapTime

   
    if mining:
        mining_timer += mapTime
        mining_index = mining_timer // mining_delay

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause = not pause
        if event.type == MOUSEBUTTONDOWN:
            if pause_x_rect.collidepoint(event.pos):
                pause = not pause
                click_sound = pygame.mixer.Sound('/Users/sam/Desktop/click_sound.wav')
                click_sound.play()
            if pause_quit_rect.collidepoint(event.pos):
                sys.exit(0)
            if main_menu_rect.collidepoint(event.pos):
                first = True
                click_sound = pygame.mixer.Sound('/Users/sam/Desktop/click_sound.wav')
                click_sound.play()
                running = False

    current_frame = animations[facing][frame_index]
    scaled_frame = pygame.transform.scale(current_frame, (current_frame.get_width() // 4, current_frame.get_height() // 4))
    half_width = scaled_frame.get_width() // 2
    half_height = scaled_frame.get_height() // 2

    keys = pygame.key.get_pressed()
    moved = False
    collision_width = tile_size * 0.3
    collision_height = tile_size * 0.25

    def get_player_rect():
        collision_width = tile_size * 0.3
        collision_height = tile_size * 0.25
        return pygame.Rect(
            player_pos.x + (tile_size - collision_width) // 2 - 4,  # tweak -4 if needed
            player_pos.y + tile_size - collision_height,
            collision_width,
            collision_height
        )
    # Save previous position
    old_x, old_y = player_pos.x, player_pos.y

    dx, dy = 0, 0
    keys = pygame.key.get_pressed()

    # Input
    if keys[pygame.K_LEFT]:
        dx = -speed
        facing = "left"
    elif keys[pygame.K_RIGHT]:
        dx = speed
        facing = "right"

    if keys[pygame.K_UP]:
        dy = -speed
        facing = "up"
    elif keys[pygame.K_DOWN]:
        dy = speed
        facing = "down"

    # Try horizontal movement
    if dx != 0:
        test_rect = get_player_rect().move(dx, 0)
        if not will_collide(test_rect):
            player_pos.x += dx

    # Try vertical movement
    if dy != 0:
        test_rect = get_player_rect().move(0, dy)
        if not will_collide(test_rect):
            player_pos.y += dy

    # Recalculate collision box
    player_rect = get_player_rect()

    # Prevent leaving screen bounds
    if player_pos.x - half_width < 0 or player_pos.x + half_width > screen_width:
        player_pos.x = old_x
        player_rect = get_player_rect()

    if player_pos.y - half_height < 0 or player_pos.y + half_height > screen_height:
        player_pos.y = old_y
        player_rect = get_player_rect()

     
        player_rect.update(player_pos.x, player_pos.y, tile_size, tile_size)
        player_moved = False
        player_pos.x -= speed

 
    old_y = player_pos.y

    player_rect.y = player_pos.y - half_height
    if (
        player_pos.y - half_height < 0 or
        player_pos.y + half_height > screen_height or
        will_collide(player_rect)
    ):
        player_pos.y = old_y
        player_rect.y = old_y - half_height  # make sure rect matches
        # Cancel mining if the player moves
    if mining and moved:
        mining = False
        mining_target = None
        mining_timer = 0
        mining_index = 0
  

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
    if keys[pygame.K_SPACE] and current_map == "main":
        dx, dy = 0, 0
        if facing == "up": dy = -1
        elif facing == "down": dy = 1
        elif facing == "left": dx = -1
        elif facing == "right": dx = 1

        tx = int((player_pos.x - map_x) // tile_size) + dx
        ty = int((player_pos.y - map_y) // tile_size) + dy

        if 0 <= tx < map_width and 0 <= ty < map_height:
          for obj in list(objects):  # use list() to safely remove during iteration
            if obj["x"] == tx and obj["y"] == ty and obj["image"] == tree_image:
                objects.remove(obj)
                ore_counts["wood"] += 1
                break

    if keys[pygame.K_SPACE] and current_map == "main" and can_craft:
        for obj in objects:
            if obj["image"] == crafting_table_image:
                dx = abs(obj["x"] - int((player_pos.x - map_x) // tile_size))
                dy = abs(obj["y"] - int((player_pos.y - map_y) // tile_size))
                if dx <= 1 and dy <= 1:

                    if player_tool_level == 1 and ore_counts["wood"] >= 3:
                        ore_counts["wood"] -= 3
                        player_tool_level += 1
                        print("Crafted Stone Tool! Now Level 2")

                    elif player_tool_level == 2 and ore_counts["stone"] >= 3:
                        ore_counts["stone"] -= 3
                        player_tool_level += 1
                        print("Crafted Iron Tool! Now Level 3")

                    elif player_tool_level == 3 and ore_counts["iron"] >= 3:
                        ore_counts["iron"] -= 3
                        player_tool_level += 1
                        print("Crafted Gold Tool! Now Level 4")

                    elif player_tool_level == 4 and ore_counts["gold"] >= 3:
                        ore_counts["gold"] -= 3
                        player_tool_level += 1
                        print("Crafted Diamond Tool! Now Level 5")

                    else:
                        print("Not enough materials to upgrade.")

                    can_craft = False
                    break
              
        # Reset crafting when SPACE is released
    if not keys[pygame.K_SPACE]:
        can_craft = True        
    if keys[pygame.K_SPACE] and current_time - last_mine_time >= mine_delay and not mining:

        last_mine_time = current_time

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
                mined_ore_type = target_tile
                valid_mineables = ("diamond", "iron", "gold", "stone")
                was_ore = target_tile in valid_mineables

                if current_map == "cave" and target_tile in valid_mineables:
                    # Check tool level
                    #global ore_hardness

                   if target_tile in ore_hardness:
                    required_level = ore_hardness[target_tile]
                    if player_tool_level < required_level:
                        print(f"Your tool is too weak to mine {target_tile}!")
                        craft_message = f"Tool too weak for {target_tile.title()}"
                        craft_message_timer = pygame.time.get_ticks()
                        continue

                    mining_target = (tx, ty)
                    mining_duration = mining_durations[target_tile]
                    mining_delay = mining_duration // len(mining_overlays)
                    mining_timer = 0
                    mining_index = 0
                    mining = True

                # Store ore type now for accurate ore count update
                mined_ore_type = target_tile

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
        pygame.mixer.music.load('Sprites/MineCraft/cave_sound.mp3')
        pygame.mixer.music.play()
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

    #Cave Hud
    if current_map == "cave":
        font = pygame.font.SysFont(None, 30)
        y_offset = 10
        for ore, count in ore_counts.items():
            text = font.render(f"{ore.capitalize()}: {count}", True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 30
    #Main Hud
    if current_map == "main":
        font = pygame.font.SysFont(None, 30)
        y_offset = 10
        for ore, count in ore_counts.items():
            text = font.render(f"{ore.capitalize()}: {count}", True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 30

    current_time = pygame.time.get_ticks()
    if craft_message and current_time - craft_message_timer <= CRAFT_MESSAGE_DURATION:
        font = pygame.font.SysFont(None, 40)
        text = font.render(craft_message, True, (255, 255, 0))  # Yellow text
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, 50))  # Center top
    else:
        craft_message = ""
    if keys[pygame.K_q]:
        break
    # Draw mining overlay if active
    if mining and mining_target:
        # Getting tile Position
        tx, ty = mining_target

        # Re-draw the tile being mined (like ore or stone)
        tile_type = tile_layout[ty][tx]
        if tile_type in tile_images:
            tile = tile_images[tile_type]
            screen.blit(tile, (map_x + tx * tile_size, map_y + ty * tile_size))

        # Draw the mining overlay (transparent PNG)
        overlay = mining_overlays[min(mining_index, len(mining_overlays) - 1)]
        scaled_overlay = pygame.transform.scale(overlay, (tile_size, tile_size))
        screen.blit(scaled_overlay, (map_x + tx * tile_size, map_y + ty * tile_size))

    if mining and mining_timer >= mining_duration and mining_target:
        tx, ty = mining_target
        target_tile = tile_layout[ty][tx]

        if mined_ore_type in ore_counts:
            ore_counts[mined_ore_type] += 1

            # Check for instant Portal Gun crafting
        if not has_portal_gun and \
        ore_counts["diamond"] >= 2 and \
        ore_counts["iron"] >= 1 and \
        ore_counts["gold"] >= 1:

            has_portal_gun = True
            ore_counts["diamond"] -= 2
            ore_counts["iron"] -= 1
            ore_counts["gold"] -= 1
            portal_gun_message = "You crafted the Portal Gun!"
            portal_gun_message_timer = pygame.time.get_ticks()
            tile_layout[ty][tx] = "empty"
            visibility[ty][tx] = True

        # Auto-reveal adjacent ore
        for dx_, dy_ in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = tx + dx_, ty + dy_
            if 0 <= nx < map_width and 0 <= ny < map_height:
                if tile_layout[ny][nx] in ore_hardness:
                    visibility[ny][nx] = True

        # Reset mining state
        mining = False
        mining_target = None
        mining_timer = 0
        mining_index = 0

        # Instant redraw
        screen.fill((0, 0, 0))
        draw_map()
        draw_objects(screen, objects, tile_size, map_x, map_y)
        screen.blit(scaled_frame, scaled_frame.get_rect(center=player_pos))
        font = pygame.font.SysFont(None, 30)
        y_offset = 10
        for ore, count in ore_counts.items():
            text = font.render(f"{ore.capitalize()}: {count}", True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 30
        if has_portal_gun and portal_gun_message:
            time_since = pygame.time.get_ticks() - portal_gun_timer
            if time_since < 3000:  # show message for 3 seconds
                font = pygame.font.SysFont(None, 36)
                text = font.render(portal_gun_message, True, (0, 255, 255))
                screen.blit(text, (screen_width // 2 - text.get_width() // 2, 50))
            else:
                portal_gun_message = ""  # clear message after timeout
    pygame.draw.rect(screen, (255, 0, 0), player_rect, 2)
    pygame.draw.circle(screen, (255, 0, 0), (int(player_pos.x), int(player_pos.y + tile_size // 2)), 5)

    if pause:
        draw_pause()
        screen.blit(game_pause_scaled, game_pause_rect)
        screen.blit(pause_x_scaled, pause_x_rect)
        screen.blit(pause_quit_scaled, pause_quit_rect)
        screen.blit(main_menu_scaled, main_menu_rect)
        
                
    

    pygame.display.flip()
    