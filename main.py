"""Sample pure SDL2 application with non-blocking input and continuous background game updates."""

import ctypes
import math
import sys
import time
import sdl2
from dataclasses import dataclass

WINDOW_WIDTH: int = 500
WINDOW_HEIGHT: int = 1000

GRID_CELL_SIZE = 50

WINDOW_TITLE: str = "Pure SDL2 Game Loop Example"
SQUARE_SIZE: int = 50
MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS: float = 0.05

PLAYER_MOVEMENT_SPEED_PIXELS_PER_SECOND: float = 350.0
AUTOMATIC_FALL_SPEED_PIXELS_PER_SECOND: float = 80.0

VISIBLE_ROWS = 20
VISIBLE_COLUMNS = 10
HIDDEN_ROWS = 2

type Color = tuple[int, int, int, int]

BACKGROUND_COLOR: Color = (30, 30, 35, 255)
SQUARE_COLOR: Color = (70, 160, 240, 255)

PALETTE: dict[int, Color] = {
    0: (0,0,0,255),
    1: (255,0,0,255),
    2: (0,255,0,255),
    3: (0,0,255,255),
    4: (255,255,0,255),
    5: (0,255,255,255),
    6: (255,0,255,255),
    7: (255,255,255,255)
}

type ShapeType = list[tuple[int] | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]]

SHAPES: dict[int, list[ShapeType]] = {
    0: [
        [
            (1, 1), 
            (1, 1)
        ]
    ],
    1: [
        [
            (1, 1, 0), 
            (0, 1, 1)
        ],
        [
            (0, 1), 
            (1, 1),
            (1, 0)
        ],
    ],
    2: [
        [
            (0, 1, 1), 
            (1, 1, 0)
        ],
        [
            (1, 0), 
            (1, 1),
            (0, 1)
        ],
    ],
    3: [
        [
          (0, 1, 0), 
          (1, 1, 1)
        ],
        [
          (1, 0), 
          (1, 1),
          (1, 0),           
        ],
        [
          (1, 1, 1),
          (0, 1, 0), 
        ],
        [
          (0, 1), 
          (1, 1),
          (0, 1),           
        ],        
    ],
    4: [
        [
            (1, 0, 0), 
            (1, 1, 1)
        ],
        [
            (1, 1), 
            (1, 0),
            (1, 0)
        ],
        [
            (1, 1, 1), 
            (0, 0, 1)
        ],
        [
            (0, 1), 
            (0, 1),
            (1, 1)
        ],
    ],
    5: [
        [
            (1, 1, 1),
            (1, 0, 0), 
        ],
        [
            (1, 1), 
            (0, 1),
            (0, 1)
        ],
        [
            (0, 0, 1),
            (1, 1, 1), 
        ],
        [
            (1, 0), 
            (1, 0),
            (1, 1)
        ],
    ],    
    6: [
        [(1, 1, 1, 1)],
        [
            (1,),
            (1,),
            (1,),
            (1,)
        ]
    ],    
}

@dataclass
class WindowState:
    window: sdl2.SDL_Window
    renderer: sdl2.SDL_Renderer

class Piece:
    color: int
    shape: ShapeType

    def __init__(self, color: int, shape: ShapeType):
        self.color = color
        self.shape = shape

class PieceState:
    color: int
    row_start: int
    col_start: int
    shape: ShapeType

    def __init__(self, color:int, row_start:int, col_start:int, shape: ShapeType):
        self.color = color
        self.row_start = row_start
        self.col_start = col_start
        self.shape = shape

    def row_end(self):
        return self.row_start + len(self.shape) - 1

    def col_end(self):
        return self.col_start + len(self.shape[0]) - 1

@dataclass
class InputEvent:
    is_running: bool
    horizontal_movement: int
    vertical_movement: int

@dataclass
class GameState:
    board: list[list[int]]
    upcoming_pieces: list[Piece]
    piece: PieceState = PieceState(0, 0, 0, SHAPES[0][0])
    time: float = 0
    level: int = 0
    score: int = 0
    is_running: bool = False


def initialize_window() -> WindowState:
    """Initialize SDL2 video and events subsystem, window, and hardware renderer."""
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_EVENTS) != 0:
        error_message: str = sdl2.SDL_GetError().decode("utf-8")
        print(f"Error initializing SDL: {error_message}", file=sys.stderr)
        sys.exit(1)

    window_pointer = sdl2.SDL_CreateWindow(
        WINDOW_TITLE.encode("utf-8"),
        sdl2.SDL_WINDOWPOS_CENTERED,
        sdl2.SDL_WINDOWPOS_CENTERED,
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        sdl2.SDL_WINDOW_SHOWN,
    )
    if not window_pointer:
        error_message = sdl2.SDL_GetError().decode("utf-8")
        print(f"Error creating SDL window: {error_message}", file=sys.stderr)
        sdl2.SDL_Quit()
        sys.exit(1)

    renderer_flags: int = (
        sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
    )
    renderer_pointer = sdl2.SDL_CreateRenderer(
        window_pointer,
        -1,
        renderer_flags,
    )
    if not renderer_pointer:
        error_message = sdl2.SDL_GetError().decode("utf-8")
        print(f"Error creating SDL renderer: {error_message}", file=sys.stderr)
        sdl2.SDL_DestroyWindow(window_pointer)
        sdl2.SDL_Quit()
        sys.exit(1)

    return WindowState(
        window=window_pointer,
        renderer=renderer_pointer
    )


def destroy_window(
    window: WindowState
) -> None:
    """Clean up SDL resources and exit application."""
    sdl2.SDL_DestroyRenderer(window.renderer)
    sdl2.SDL_DestroyWindow(window.window)
    sdl2.SDL_Quit()
    sys.exit(0)


def process_input(
    event_instance: sdl2.SDL_Event,
) -> InputEvent:
    """Process pending SDL events and keyboard inputs without blocking."""
    is_running: bool = True
    horizontal_movement_direction: float = 0.0
    vertical_movement_direction: float = 0.0

    while sdl2.SDL_PollEvent(ctypes.byref(event_instance)) != 0:
        if event_instance.type == sdl2.SDL_QUIT:
            is_running = False
        elif event_instance.type == sdl2.SDL_KEYDOWN:
            if event_instance.key.keysym.sym == sdl2.SDLK_ESCAPE:
                is_running = False
            elif event_instance.key.repeat != 0:
                continue
            elif event_instance.key.keysym.sym == sdl2.SDLK_LEFT:
                horizontal_movement_direction = -1.0
            elif event_instance.key.keysym.sym == sdl2.SDLK_RIGHT:
                horizontal_movement_direction = 1.0
            elif event_instance.key.keysym.sym == sdl2.SDLK_UP:
                vertical_movement_direction = -1.0
            elif event_instance.key.keysym.sym == sdl2.SDLK_DOWN:
                vertical_movement_direction = 1.0                

    if horizontal_movement_direction != 0.0 and vertical_movement_direction != 0.0:
        movement_vector_length: float = math.hypot(
            horizontal_movement_direction, vertical_movement_direction
        )
        horizontal_movement_direction /= movement_vector_length
        vertical_movement_direction /= movement_vector_length

    return InputEvent(
        is_running=is_running,
        horizontal_movement=int(horizontal_movement_direction),
        vertical_movement=int(vertical_movement_direction)
    )


def update_game_state(
    game: GameState,
    event: InputEvent,
    delta_time_in_seconds: float,
) -> GameState:
    """Perform continuous background game updates combined with player movement."""
    game.piece.col_start += event.horizontal_movement
    game.piece.row_start += event.vertical_movement

    # # 1. Player-controlled movement
    # updated_horizontal_position: float = (
    #     horizontal_position
    #     + horizontal_movement_direction
    #     * PLAYER_MOVEMENT_SPEED_PIXELS_PER_SECOND
    #     * delta_time_in_seconds
    # )
    # updated_vertical_position: float = (
    #     vertical_position
    #     + vertical_movement_direction
    #     * PLAYER_MOVEMENT_SPEED_PIXELS_PER_SECOND
    #     * delta_time_in_seconds
    # )

    # # 2. Continuous autonomous game operation (e.g. continuous downward gravity)
    # updated_vertical_position += (
    #     AUTOMATIC_FALL_SPEED_PIXELS_PER_SECOND * delta_time_in_seconds
    # )

    # # 3. Boundary constraints (wrap around or clamp)
    # updated_horizontal_position = max(
    #     0.0,
    #     min(updated_horizontal_position, float(WINDOW_WIDTH - SQUARE_SIZE)),
    # )
    # if updated_vertical_position > float(WINDOW_HEIGHT - SQUARE_SIZE):
    #     # Reset to top when reaching bottom boundary
    #     updated_vertical_position = 0.0
    # elif updated_vertical_position < 0.0:
    #     updated_vertical_position = 0.0

    # return (updated_horizontal_position, updated_vertical_position)
    return game


def render_frame(
    window: WindowState,
    game: GameState,
) -> None:
    """Render background and active game elements."""
    # Clear screen with background color
    sdl2.SDL_SetRenderDrawColor(
        window.renderer,
        *BACKGROUND_COLOR,
    )
    sdl2.SDL_RenderClear(window.renderer)

    # Draw moving square
    for (row_num, row) in enumerate(game.board):
        for (col_num, col) in enumerate(row):
            vertical_position = GRID_CELL_SIZE * (row_num - HIDDEN_ROWS)
            horizontal_position = GRID_CELL_SIZE * col_num
            if vertical_position < 0:
                continue

            if (
                (row_num >= game.piece.row_start and row_num <= game.piece.row_end())
                and 
                (col_num >= game.piece.col_start and col_num <= game.piece.col_end())
            ):
                col = game.piece.shape[row_num - game.piece.row_start][col_num - game.piece.col_start]

            if col == 0:
                continue

            color = PALETTE[col]
            sdl2.SDL_SetRenderDrawColor(
                window.renderer,
                *color
            )
            
            square_rectangle: sdl2.SDL_Rect = sdl2.SDL_Rect(
                horizontal_position,
                vertical_position,
                SQUARE_SIZE,
                SQUARE_SIZE,
            )
            sdl2.SDL_RenderFillRect(window.renderer, ctypes.byref(square_rectangle))

    # Present rendered frame to display
    sdl2.SDL_RenderPresent(window.renderer)


def run_application() -> None:
    """Run the continuous non-blocking main game loop."""
    window = initialize_window()

    board = [[0] * VISIBLE_COLUMNS] * (VISIBLE_ROWS + HIDDEN_ROWS)
    piece = PieceState(
        color=5,
        row_start=3,
        col_start=3,
        shape=SHAPES[3][1]
    )
    game = GameState(
        is_running=True,
        upcoming_pieces=[],
        board=board,
        piece=piece
    )

    previous_time_in_seconds: float = time.perf_counter()
    event_instance: sdl2.SDL_Event = sdl2.SDL_Event()

    while game.is_running:
        current_time_in_seconds: float = time.perf_counter()
        delta_time_in_seconds: float = (
            current_time_in_seconds - previous_time_in_seconds
        )
        previous_time_in_seconds = current_time_in_seconds

        if delta_time_in_seconds > MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS:
            delta_time_in_seconds = MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS

        # Stage 1: Non-blocking input processing
        input_event  = process_input(event_instance)

        if not input_event.is_running:
            game = game.is_running=False

        # Stage 2: Continuous autonomous game updates
        game = update_game_state(
            game,
            input_event,
            delta_time_in_seconds,
        )

        # Stage 3: Render frame
        render_frame(
            window,
            game,
        )

    destroy_window(window)


if __name__ == "__main__":
    run_application()
