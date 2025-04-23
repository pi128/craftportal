
import pygame
import sys
from pygame.locals import *
from random import randint, shuffle

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Audio device not available; continuing without sound.")


#  CONSTANTS

SCREEN_W, SCREEN_H = 1280, 720
TILE              = 64
MAP_W, MAP_H      = 20, 11
FPS               = 60


#  PYGAME SETUP

screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock   = pygame.time.Clock()
surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

def safe_load(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


#  SPRITES & TILES

# UI buttons & menus
pause_bg     = safe_load('Sprites/MineCraft/game_paused.png',   (500,200))
pause_x_btn  = safe_load('Sprites/MineCraft/x_out.png',         (128, 90))
pause_quit   = safe_load('Sprites/MineCraft/pause_quit.png',    (300,100))
main_menu_b  = safe_load('Sprites/MineCraft/main_menu.png',     (300,100))
start_btn    = safe_load('Sprites/MineCraft/start.png',         (300,100))
start_ov     = safe_load('Sprites/MineCraft/over_start.png',    (300,100))
settings_btn = safe_load('Sprites/MineCraft/settings.png',      (300,100))
settings_ov  = safe_load('Sprites/MineCraft/over_settings.png', (300,100))
quit_btn     = safe_load('Sprites/MineCraft/quit.png',          (300,100))
quit_ov      = safe_load('Sprites/MineCraft/over_quit.png',     (300,100))
menu_bg      = safe_load('Sprites/MineCraft/portalcraft.png',   (SCREEN_W, SCREEN_H))

# Base ground tiles
base_tiles = {
    "dirtpath": safe_load("Sprites/Tiles/Dirt Path/dirtpath-1.png", (TILE,TILE)),
    "cavepath": safe_load("Sprites/Tiles/Cave/cavepath-1.png",     (TILE,TILE)),
    "grass":    safe_load("Sprites/Tiles/Grass/grass-1.png",       (TILE,TILE)),
    "cave":     safe_load("Sprites/Tiles/Cave/CaveTile1.png",      (TILE,TILE)),
}

# Ore & other tile
ore_tiles = {
    "stone":   safe_load("Sprites/MineCraft/stoneblock.png",   (TILE,TILE)),
    "iron":    safe_load("Sprites/MineCraft/ironblock.png",    (TILE,TILE)),
    "gold":    safe_load("Sprites/MineCraft/goldblock.png",    (TILE,TILE)),
    "diamond": safe_load("Sprites/MineCraft/diamondblock.png", (TILE,TILE)),
    "dirt":    safe_load("Sprites/MineCraft/dirtblock.png",    (TILE,TILE)),
    "empty":   base_tiles["cave"],
}
tile_images = {**base_tiles, **ore_tiles}

# Objects
tree_img          = safe_load("Sprites/Objects/Trees and Shrubs/tree-1.png", (TILE,TILE))
crafting_img      = safe_load("Sprites/MineCraft/craftingTable1.png",       (TILE,TILE))
cave_entrance_img = safe_load("Sprites/Tiles/Cave/CaveEntrance.png",        (TILE,TILE))
gate_img          = safe_load("Sprites/Tiles/Dirt Path/dirtpath-4.png",     (TILE,TILE))

# Character walking animation locked the size
PLAYER_SIZE = TILE
def load_anim(files):
    return [
        pygame.transform.scale(
            safe_load(f"Sprites/Characters/{f}"),
            (PLAYER_SIZE, PLAYER_SIZE)
        )
        for f in files
    ]
animations = {
    "down":  load_anim(["ForwardFacing.png","ForwardWalk1.png","ForwardWalk2.png"]),
    "up":    load_anim(["BackFacing.png","BackWalking1.png","BackWalking2.png"]),
    "left":  load_anim(["LeftFacing.png","LeftWalking1.png","LeftWalking2.png"]),
    "right": load_anim(["RightFacing.png","RightWalking1.png","RightWalking2.png"])
}

# Mining crack animation
mining_overlays = [safe_load(f"Sprites/MineCraft/MiningNum{i}.png") for i in range(1,11)]


#  actual GAME DATA

ore_counts = {k:0 for k in ("wood","stone","iron","gold","diamond")}

ore_hardness = {
    "stone":   1,   # wood pick can mine stone
    "iron":    2,   # stone pick
    "gold":    3,   # iron pick
    "diamond": 3    # gold pick
}

mining_durations = {
    "stone":   500,
    "iron":    800,
    "gold":    1000,
    "diamond": 1500
}

# ────────────────────────────────────────────────────────────────────────────
#  MAP HELPERS
# ────────────────────────────────────────────────────────────────────────────
def lay_path(layout, x, y, dir_, length, thickness=1, kind="dirtpath"):
    half = thickness//2
    for i in range(length):
        for t in range(-half, half+1):
            tx, ty = (x+i, y+t) if dir_=="horizontal" else (x+t, y+i)
            if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
                layout[ty][tx] = kind

def add_object(obj_list, tx, ty, img, *, collidable=True):
    vr = pygame.Rect(map_x+tx*TILE, map_y+ty*TILE, TILE, TILE)
    cr = pygame.Rect(vr.x+TILE//4, vr.y+TILE//2, TILE//2, TILE//2)
    obj_list.append({"x":tx,"y":ty,"image":img,"rect":cr,"collidable":collidable})

def draw_objects(objs):
    for o in objs:
        screen.blit(pygame.transform.scale(o["image"],(TILE,TILE)),
                    (map_x+o["x"]*TILE, map_y+o["y"]*TILE))

def generate_mining_map():
    layout = [["stone"]*MAP_W for _ in range(MAP_H)]
    vis    = [[False]*MAP_W for _ in range(MAP_H)]
    cx, cy = MAP_W//2, MAP_H//2

    # central room
    for yy in range(cy-1, cy+2):
        for xx in range(cx-1, cx+2):
            layout[yy][xx] = "dirtpath"
            vis[yy][xx]    = True

    guaranteed = ["diamond"]*5 + ["iron"]*10 + ["gold"]*8
    shuffle(guaranteed)
    spots = [(x,y) for y in range(MAP_H) for x in range(MAP_W) if layout[y][x]=="stone"]
    shuffle(spots)
    for ore in guaranteed:
        x,y = spots.pop()
        layout[y][x] = ore

    # random extras
    for x,y in spots:
        if randint(1,10)<=3:
            layout[y][x] = "iron" if randint(1,3)<=2 else "gold"

    return layout, vis

def create_main_room():
    layout = [["grass"]*MAP_W for _ in range(MAP_H)]
    lay_path(layout,5,5,"horizontal",10)
    lay_path(layout,10,2,"vertical",6)
    objs = []
    for _ in range(10):
        while True:
            tx,ty = randint(0,MAP_W-1), randint(0,MAP_H-1)
            if layout[ty][tx]=="grass":
                add_object(objs,tx,ty,tree_img)
                break
    add_object(objs,4,2,tree_img)
    add_object(objs,8,5,crafting_img)
    return layout, objs

# ────────────────────────────────────────────────────────────────────────────
#  BUILD MAPS & INITIAL STATE
# ────────────────────────────────────────────────────────────────────────────
map_x = (SCREEN_W - TILE*MAP_W)//2
map_y = (SCREEN_H - TILE*MAP_H)//2

main_layout, main_objs = create_main_room()
cave_layout,  cave_vis  = generate_mining_map()

cave_dug = [[False] * MAP_W for _ in range(MAP_H)]
maps = {
    "main": {
        "layout":  main_layout,
        "objects": main_objs,
        "tile":    base_tiles["grass"],
        # optional, but keeps the .get() symmetrical
        "dug":     [[True]*MAP_W for _ in range(MAP_H)]
    },
    "cave": {
        "layout":     cave_layout,
        "objects":    [],
        "tile":       base_tiles["cave"],
        "visibility": cave_vis,
        "dug":        cave_dug        #  ←  add this line
    }
}
add_object(maps["main"]["objects"],10,0,cave_entrance_img,collidable=False)
add_object(maps["main"]["objects"],19,5,gate_img,collidable=False)

current_map  = "main"
tile_layout  = maps[current_map]["layout"]
objects      = maps[current_map]["objects"]
tile_img     = maps[current_map]["tile"]
visibility   = maps[current_map].get("visibility", [[True]*MAP_W for _ in range(MAP_H)])
dug = maps[current_map].get("dug")  

# ────────────────────────────────────────────────────────────────────────────
#  PLAYER STATE
# ────────────────────────────────────────────────────────────────────────────
player_pos    = pygame.Vector2(map_x+TILE*(MAP_W//2),
                               map_y+TILE*(MAP_H//2))
facing        = "down"
frame_idx     = 0
frame_timer   = 0
FRAME_DELAY   = 150
speed         = 5
player_tool   = 0   # 0=no pick,1=wood,2=stone,3=iron,4=gold,5=diamond

mining        = False
mining_target = None
mining_timer  = 0
mining_idx    = 0
mining_delay  = 300
last_mine_time= 0

pause         = False
first         = True

craft_msg     = ""
craft_msg_time= 0
CRAFT_DURATION= 2000
portal_msg    = ""
portal_msg_time=0
has_portal_gun=False

# ────────────────────────────────────────────────────────────────────────────
#  COLLISION HELPERS
# ────────────────────────────────────────────────────────────────────────────
def player_rect():
    col_w = TILE*0.8
    col_h = TILE*0.8
    left  = player_pos.x - col_w/2
    top   = player_pos.y + TILE/2 - col_h
    return pygame.Rect(left, top, col_w, col_h)

def tile_blocking(tx,ty):
    if not (0<=tx<MAP_W and 0<=ty<MAP_H):
        return True
    if current_map=="cave" and tile_layout[ty][tx] in ore_hardness:
        return True
    return False

def will_collide(r):
    cx,cy = r.center
    if (cx<map_x or cx>=map_x+MAP_W*TILE or
        cy<map_y or cy>=map_y+MAP_H*TILE):
        return True
    for o in objects:
        if o.get("collidable",True) and r.colliderect(o["rect"]):
            return True
    left   = int((r.left   - map_x)//TILE)
    right  = int((r.right  -1 - map_x)//TILE)
    top    = int((r.top    - map_y)//TILE)
    bottom = int((r.bottom -1 - map_y)//TILE)
    for ty in range(top, bottom+1):
        for tx in range(left, right+1):
            if 0<=tx<MAP_W and 0<=ty<MAP_H and tile_blocking(tx,ty):
                return True
    return False

def reveal_around_player(radius=1):
    px, py = player_tile()
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            ny, nx = py + dy, px + dx
            if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                visibility[ny][nx] = True

# ────────────────────────────────────────────────────────────────────────────
#  DRAW MAP WITH FOG-OF-WAR
# ────────────────────────────────────────────────────────────────────────────
def draw_map():
    for y in range(MAP_H):
        for x in range(MAP_W):
            dx, dy = map_x + x * TILE, map_y + y * TILE

            # 1) floor texture (unchanged)
            screen.blit(tile_img, (dx, dy))

            if current_map == "cave":
                if not visibility[y][x]:
                    # hidden → always look like solid stone
                    screen.blit(tile_images["stone"], (dx, dy))
                    continue
                elif not dug[y][x]:
                    # visible but NOT yet dug out → still stone
                    screen.blit(tile_images["stone"], (dx, dy))
                    continue

            # 2) either we’re on the overworld OR the cell is dug out
            tile = tile_layout[y][x]
            screen.blit(tile_images.get(tile, tile_img), (dx, dy))

            # 3) persistent crack overlay (unchanged)
            if (x, y) in persistent_overlays:
                screen.blit(persistent_overlays[(x, y)], (dx, dy))

# ────────────────────────────────────────────────────────────────────────────
#  START MENU
# ────────────────────────────────────────────────────────────────────────────
start_rect    = start_btn.get_rect(center=(SCREEN_W//2,SCREEN_H//2))
settings_rect = settings_btn.get_rect(center=(SCREEN_W//2,SCREEN_H//2+105))
quit_rect     = quit_btn.get_rect(center=(SCREEN_W//2,SCREEN_H//2+210))
flash,frame,highlight = 30,0,True

while first:
    for e in pygame.event.get():
        if e.type==QUIT: sys.exit()
        if e.type==MOUSEBUTTONDOWN:
            if start_rect.collidepoint(e.pos):
                first=False
            elif quit_rect.collidepoint(e.pos):
                sys.exit()
    frame += 1
    if frame>=flash:
        highlight = not highlight
        frame = 0
    screen.blit(menu_bg,(0,0))
    screen.blit(start_btn,    start_rect.topleft)
    screen.blit(settings_btn, settings_rect.topleft)
    screen.blit(quit_btn,     quit_rect.topleft)
    if highlight:
        screen.blit(start_ov,    start_rect.topleft)
        screen.blit(settings_ov, settings_rect.topleft)
        screen.blit(quit_ov,     quit_rect.topleft)
    pygame.display.flip()
    clock.tick(FPS)

# ────────────────────────────────────────────────────────────────────────────
#  MAIN GAME LOOP
# ────────────────────────────────────────────────────────────────────────────
persistent_overlays = {}
map_switch_delay, map_switch_timer = 500, 0

def player_tile():
    return (int((player_pos.x-map_x)//TILE),
            int((player_pos.y-map_y)//TILE))

running = True
while running:
    dt = clock.tick(FPS)
    map_switch_timer += dt

    for e in pygame.event.get():
        if e.type==QUIT:
            running=False
        elif e.type==KEYDOWN and e.key==K_ESCAPE:
            pause = not pause
        elif e.type==MOUSEBUTTONDOWN and pause:
            if pause_x_btn.get_rect(topleft=(0,0)).collidepoint(e.pos):
                pause=False
            elif pause_quit.get_rect(center=(SCREEN_W//2,SCREEN_H//2)).collidepoint(e.pos):
                running=False
            elif main_menu_b.get_rect(center=(SCREEN_W//2,465)).collidepoint(e.pos):
                pygame.event.post(pygame.event.Event(QUIT))

    if not pause:
        # ─── INPUT & MOVEMENT ──────────────────────────────────────────────
        
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if not mining:                             # ← add this line
            if keys[K_LEFT]:  dx, facing = -speed, "left"
            if keys[K_RIGHT]: dx, facing =  speed, "right"
            if keys[K_UP]:    dy, facing = -speed, "up"
            if keys[K_DOWN]:  dy, facing =  speed, "down"
        new = player_rect().move(dx,0)
        if not will_collide(new): player_pos.x += dx
        new = player_rect().move(0,dy)
        if not will_collide(new): player_pos.y += dy

        player_pos.x = max(map_x, min(player_pos.x, map_x+MAP_W*TILE-TILE))
        player_pos.y = max(map_y, min(player_pos.y, map_y+MAP_H*TILE-TILE))

        # bummy switch map
        if keys[K_m] and map_switch_timer>=map_switch_delay:
            current_map = "cave" if current_map=="main" else "main"
            tile_layout = maps[current_map]["layout"]
            objects     = maps[current_map]["objects"]
            tile_img    = maps[current_map]["tile"]
            visibility  = maps[current_map].get("visibility", [[True]*MAP_W for _ in range(MAP_H)])
            map_switch_timer = 0
            dug = maps[current_map].get("dug")      

        now = pygame.time.get_ticks()
        # Space Button logic
        if keys[K_SPACE] and now - last_mine_time >= 300:
            last_mine_time = now
            fx=fy=0
            if facing=="up":    fy=-1
            if facing=="down":  fy= 1
            if facing=="left":  fx=-1
            if facing=="right": fx= 1
            tx = int((player_pos.x-map_x)//TILE) + fx
            ty = int((player_pos.y-map_y)//TILE) + fy

            # chopping & crafting in main
            if current_map=="main" and 0<=tx<MAP_W and 0<=ty<MAP_H:
                for o in list(objects):
                    if o["image"]==tree_img and (o["x"],o["y"])==(tx,ty):
                        objects.remove(o); ore_counts["wood"] += 1; break
                if any(o["image"]==crafting_img and abs(o["x"]-tx)<=1 and abs(o["y"]-ty)<=1 for o in objects):
                    upgrades = [
                        (0,"wood",3), (1,"stone",3),
                        (2,"iron",3),(3,"gold",3),(3,"diamond",3)
                    ]
                    for tier,res,cost in upgrades:
                        if player_tool==tier and ore_counts[res]>=cost:
                            ore_counts[res]-=cost
                            player_tool += 1
                            craft_msg = f"Crafted a {res.title()} pick!"
                            craft_msg_time = now
                            break

            # mining in cave
            if current_map=="cave" and 0<=tx<MAP_W and 0<=ty<MAP_H:
                target = tile_layout[ty][tx]
                if target in ore_hardness and player_tool>=ore_hardness[target]:
                    mining = True
                    mining_target = (tx,ty)
                    mining_duration= mining_durations[target]
                    mining_delay   = mining_duration//len(mining_overlays)
                    mining_timer = mining_idx = 0
                elif target in ore_hardness:
                    craft_msg = f"Need better tool for {target}"
                    craft_msg_time = now

    # Mineing Tick
    if mining:
        mining_timer += dt
        # advanced crack animation
        new_idx = min(mining_timer // mining_delay, len(mining_overlays) - 1)
        if new_idx != mining_idx and mining_target:
            persistent_overlays[mining_target] = mining_overlays[new_idx]
        mining_idx = new_idx

        # finished?
        if mining_timer >= mining_duration and mining_target:
            mx, my = mining_target        
            kind = tile_layout[my][mx]

            # harvest the ore and leave the floor
            ore_counts[kind] += 1
            tile_layout[my][mx] = "empty"
            dug[my][mx] = True             # mark as excavated
            persistent_overlays.pop((mx, my), None)   # remove the crack


            mining = False
            mining_target = None

            # auto-craft portal-gun if you now meet the recipe i dont like this
            if (not has_portal_gun and
                ore_counts["diamond"] >= 2 and
                ore_counts["iron"]    >= 1 and
                ore_counts["gold"]    >= 1):
                ore_counts["diamond"] -= 2
                ore_counts["iron"]    -= 1
                ore_counts["gold"]    -= 1
                has_portal_gun  = True
                portal_msg      = "You crafted the Portal Gun!"
                portal_msg_time = pygame.time.get_ticks()

    #Animate the player
    moved = dx!=0 or dy!=0
    if moved:
        frame_timer += dt
        if frame_timer>=FRAME_DELAY:
            frame_timer=0
            frame_idx = (frame_idx+1)%len(animations[facing])
    else:
        frame_idx=0



    # Auto Teleport
    px, py = player_tile()
    if current_map=="main":
        for o in objects:
            if (o["x"],o["y"])==(px,py) and o["image"] in (cave_entrance_img, gate_img):
                current_map  = "cave"
                tile_layout  = maps["cave"]["layout"]
                objects      = maps["cave"]["objects"]
                tile_img     = maps["cave"]["tile"]
                visibility   = maps["cave"]["visibility"]
                player_pos.update(map_x+TILE*(MAP_W//2),
                                  map_y+TILE*(MAP_H//2))
                if pygame.mixer.get_init():
                    pygame.mixer.music.load('Sprites/MineCraft/cave_sound.mp3')
                    pygame.mixer.music.play()
                break
    if current_map == "cave" and not pause:
        reveal_around_player(radius=1)      # 1-tile halo is enough
    #Draw and display everything
    screen.fill((0,0,0))
    draw_map()
    draw_objects(objects)
    screen.blit(animations[facing][frame_idx], animations[facing][frame_idx].get_rect(center=player_pos))

    # HUD
    font = pygame.font.SysFont(None,30)
    y = 10
    for k,c in ore_counts.items():
        txt = font.render(f"{k.title()}: {c}", True, (255,255,255))
        screen.blit(txt, (10,y)); y+=30

    now = pygame.time.get_ticks()
    if craft_msg and now-craft_msg_time<CRAFT_DURATION:
        t = font.render(craft_msg, True, (255,255,0))
        screen.blit(t, (SCREEN_W//2-t.get_width()//2,50))
    if portal_msg and now-portal_msg_time<3000:
        t = font.render(portal_msg, True, (0,255,255))
        screen.blit(t, (SCREEN_W//2-t.get_width()//2,80))

    # mining overlay
    if mining and mining_target:
        mx,my = mining_target
        ov    = mining_overlays[mining_idx]
        screen.blit(pygame.transform.scale(ov,(TILE,TILE)), (map_x+mx*TILE, map_y+my*TILE))

    # pause screen
    if pause:
        surface.fill((128,128,128,150))
        screen.blit(surface,(0,0))
        screen.blit(pause_bg,    pause_bg.get_rect(center=(SCREEN_W//2,SCREEN_H//2-150)))
        screen.blit(pause_x_btn, (0,0))
        screen.blit(pause_quit,  pause_quit.get_rect(center=(SCREEN_W//2,SCREEN_H//2)))
        screen.blit(main_menu_b, main_menu_b.get_rect(center=(SCREEN_W//2,465)))

    pygame.display.flip()

pygame.quit()