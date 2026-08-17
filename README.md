# Pure SDL2 Keyboard Movement Example

A sample Python project using pure SDL2 bindings (`PySDL2`) without Pygame. Renders a hardware-accelerated movable square controlled via keyboard input (Arrow keys or WASD).

## Requirements

- Python 3.10+
- PySDL2 & pysdl2-dll

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python3 main.py
```

### Controls

- **Arrow Keys** or **W / A / S / D**: Move the square (Up, Down, Left, Right)
- **Escape** or **Close Window**: Exit the application
