import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

# Load images
walk_down = [
    pygame.image.load("/Users/james/DM/craftportal/SteveSprites/ForwardFacing.png").convert_alpha(),
]

# Player state
player_pos = [300, 200]
frame = 0
moving = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update animation frame every 10 ticks
    if moving:
        frame += 0.1
        if frame >= len(walk_down):
            frame = 0

    screen.fill((30, 30, 30))
    screen.blit(walk_down[int(frame)], player_pos)
    pygame.display.flip()
    clock.tick(60)