# CraftPortal - Web Game

A Minecraft-inspired mining and crafting game built with Pygame and deployed to the web using pygbag.

## 🎮 Play the Game

[Play CraftPortal](https://yourusername.github.io/craftportal) *(Update with your actual GitHub username)*

## 🕹️ How to Play

- **Arrow Keys**: Move your character
- **Space**: Mine blocks or chop trees
- **Escape**: Pause the game
- **Crafting**: Use the crafting table to upgrade your pickaxe
- **Mining**: Collect stone, iron, gold, and diamonds in the cave
- **Portal Gun**: Automatically crafted when you have enough materials!

## 🛠️ Development

### Local Development
```bash
# Run locally with Python
python "working version.py"

# Or run the web version
python game_web.py
```

### Web Development
```bash
# Build for web with pygbag
python -m pygbag --port 8000 .

# Then open http://localhost:8000
```

## 🚀 Deployment

This game is automatically deployed to GitHub Pages using GitHub Actions. The workflow:

1. Builds the game with pygbag
2. Uploads the web build to GitHub Pages
3. Updates automatically on every push to main

## 📁 Project Structure

- `working version.py` - Original working game
- `game_web.py` - Web-optimized version with async support
- `main.py` - Entry point for pygbag
- `Sprites/` - All game assets (images, sounds)
- `Fonts/` - Game fonts
- `.github/workflows/deploy.yml` - GitHub Actions deployment

## 🎯 Features

- **Fog of War**: Explore the cave with limited visibility
- **Resource Management**: Collect and manage different ore types
- **Crafting System**: Upgrade tools at the crafting table
- **Mining Mechanics**: Different tools required for different ores
- **Portal Gun**: End-game item with auto-crafting
- **Web Compatible**: Runs smoothly in browsers via WebAssembly
