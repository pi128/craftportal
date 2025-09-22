import importlib.machinery
import importlib.util
import os
import sys

# Ensure we run from project root for relative asset paths
BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)

GAME_PATH = os.path.join(BASE_DIR, "Hackathon (For Real)(foReal).py")

if not os.path.exists(GAME_PATH):
    raise FileNotFoundError(f"Game file not found: {GAME_PATH}")

loader = importlib.machinery.SourceFileLoader("game_main", GAME_PATH)
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
