import pygame, sys, os
from pathlib import Path
from pygame.locals import *

# -- Initialization code omitted for brevity --

# Fix: Move ore count and HUD drawing to be always visible
font = pygame.font.SysFont(None, 30)
y_offset = 10
for ore, count in ore_counts.items():
    text = font.render(f"{ore.capitalize()}: {count}", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 30

pygame.display.flip()
