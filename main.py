import importlib.machinery
import importlib.util
import os
import traceback
import pygame

BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)

pygame.init()
try:
    _screen = pygame.display.set_mode((800, 450))
    _screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 28)
    txt = font.render("Booting...", True, (180, 220, 255))
    _screen.blit(txt, (10, 10))
    pygame.display.flip()
except Exception:
    pass

GAME_FILE = os.path.join(BASE_DIR, "game_entry.py")

if not os.path.exists(GAME_FILE):
    raise FileNotFoundError(GAME_FILE)

try:
    # Ensure the game can recreate its own display without our splash in the way
    try:
        pygame.display.quit()
    except Exception:
        pass
    loader = importlib.machinery.SourceFileLoader("game_main", GAME_FILE)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
except Exception as exc:
    # Show a red error overlay on the canvas so issues are visible in-browser
    try:
        _screen = pygame.display.get_surface() or pygame.display.set_mode((800, 450))
        _screen.fill((30, 0, 0))
        font = pygame.font.SysFont(None, 24)
        msg = "Launch error:\n" + "\n".join(traceback.format_exception_only(type(exc), exc))
        y = 10
        for line in msg.splitlines():
            surf = font.render(line, True, (255, 80, 80))
            _screen.blit(surf, (10, y)); y += 24
        pygame.display.flip()
        # Keep the frame visible for longer to read
        pygame.time.delay(6000)
    except Exception:
        pass
    raise
