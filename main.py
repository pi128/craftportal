import importlib.machinery
import importlib.util
import os

BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)

GAME_FILE = os.path.join(BASE_DIR, "game_web.py")

if not os.path.exists(GAME_FILE):
    raise FileNotFoundError(GAME_FILE)

loader = importlib.machinery.SourceFileLoader("game_main", GAME_FILE)
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)