import pygame, sys

# Initialize pygame
pygame.init()

# Set up the display

width, height = 1280, 960
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("My First Pygame Window")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                           
    # Fill the screen with a color
    screen.fill((125, 198, 83))  # RGB color: sky blue

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()

