# Flappy Bird — Variable Tampering

A Flappy Bird clone in Python/Pygame with its physics pulled out into named settings, used in
coding club to show how changing a handful of numbers changes how a whole game feels.

```
HOW TO PLAY
  SPACE or CLICK ... flap
  R .............. restart

HOW TO TWEAK (while the game is running!)
  UP / DOWN ....... pick a setting
  LEFT / RIGHT .... change it
  H ............... show the bird's hitbox
  TAB ............. hide the settings panel (for screenshots)
  BACKSPACE ....... reset everything back to normal
```

Put the `img/` folder next to `Tweaked_Flappy.py`. If it's missing, the game still runs with
coloured boxes instead of pictures.

## Requirements

- **Python 3.9+** — check with `python --version`
- **Pygame** — `pip install pygame`
  - If pip is blocked on a school account: `pip install --user pygame`
  - If pygame won't build on a very new Python, use the maintained fork: `pip install pygame-ce`
    (same `import pygame`)

## How to run

From a terminal:

```bash
cd flappybird-tampering
python Tweaked_Flappy.py      # macOS/Linux: python3 Tweaked_Flappy.py
```

In **PyCharm** (the school machines): open the `flappybird-tampering` folder *itself* as the
project — not the whole repo — then right-click `Tweaked_Flappy.py` → **Run**. To install pygame
without admin rights, use `Settings → Project → Python Interpreter → +` and search for `pygame`;
PyCharm puts it in a project venv.

> **If you see plain coloured rectangles** instead of the bird and pipes, the game didn't find the
> `img/` folder — it falls back to boxes rather than crashing. Almost always this means it was
> launched from the wrong directory: open `flappybird-tampering` as the project root, or set the
> run configuration's *Working directory* to that folder.