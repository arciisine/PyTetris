"""Sample pure SDL2 application with non-blocking input and continuous background game updates."""

import ctypes
import math
import sys
import time
import sdl2

WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600
WINDOW_TITLE: str = "Pure SDL2 Game Loop Example"
SQUARE_SIZE: int = 50
MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS: float = 0.05

PLAYER_MOVEMENT_SPEED_PIXELS_PER_SECOND: float = 350.0
AUTOMATIC_FALL_SPEED_PIXELS_PER_SECOND: float = 80.0

BACKGROUND_COLOR: tuple[int, int, int, int] = (30, 30, 35, 255)
SQUARE_COLOR: tuple[int, int, int, int] = (70, 160, 240, 255)


def initialize_window() -> tuple[sdl2.SDL_Window, sdl2.SDL_Renderer]:
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

    return (window_pointer, renderer_pointer)


def destroy_window(
    window_pointer: sdl2.SDL_Window, renderer_pointer: sdl2.SDL_Renderer
) -> None:
    """Clean up SDL resources and exit application."""
    sdl2.SDL_DestroyRenderer(renderer_pointer)
    sdl2.SDL_DestroyWindow(window_pointer)
    sdl2.SDL_Quit()
    sys.exit(0)


def process_input(
    event_instance: sdl2.SDL_Event,
) -> tuple[bool, float, float]:
    """Process pending SDL events and keyboard inputs without blocking."""
    is_running: bool = True

    while sdl2.SDL_PollEvent(ctypes.byref(event_instance)) != 0:
        if event_instance.type == sdl2.SDL_QUIT:
            is_running = False
        elif event_instance.type == sdl2.SDL_KEYDOWN:
            if event_instance.key.keysym.sym == sdl2.SDLK_ESCAPE:
                is_running = False

    keyboard_state_pointer = sdl2.SDL_GetKeyboardState(None)

    horizontal_movement_direction: float = 0.0
    vertical_movement_direction: float = 0.0

    if (
        keyboard_state_pointer[sdl2.SDL_SCANCODE_LEFT]
        or keyboard_state_pointer[sdl2.SDL_SCANCODE_A]
    ):
        horizontal_movement_direction -= 1.0
    if (
        keyboard_state_pointer[sdl2.SDL_SCANCODE_RIGHT]
        or keyboard_state_pointer[sdl2.SDL_SCANCODE_D]
    ):
        horizontal_movement_direction += 1.0
    if (
        keyboard_state_pointer[sdl2.SDL_SCANCODE_UP]
        or keyboard_state_pointer[sdl2.SDL_SCANCODE_W]
    ):
        vertical_movement_direction -= 1.0
    if (
        keyboard_state_pointer[sdl2.SDL_SCANCODE_DOWN]
        or keyboard_state_pointer[sdl2.SDL_SCANCODE_S]
    ):
        vertical_movement_direction += 1.0

    if horizontal_movement_direction != 0.0 and vertical_movement_direction != 0.0:
        movement_vector_length: float = math.hypot(
            horizontal_movement_direction, vertical_movement_direction
        )
        horizontal_movement_direction /= movement_vector_length
        vertical_movement_direction /= movement_vector_length

    return (
        is_running,
        horizontal_movement_direction,
        vertical_movement_direction,
    )


def update_game_state(
    horizontal_position: float,
    vertical_position: float,
    horizontal_movement_direction: float,
    vertical_movement_direction: float,
    delta_time_in_seconds: float,
) -> tuple[float, float]:
    """Perform continuous background game updates combined with player movement."""
    # 1. Player-controlled movement
    updated_horizontal_position: float = (
        horizontal_position
        + horizontal_movement_direction
        * PLAYER_MOVEMENT_SPEED_PIXELS_PER_SECOND
        * delta_time_in_seconds
    )
    updated_vertical_position: float = (
        vertical_position
        + vertical_movement_direction
        * PLAYER_MOVEMENT_SPEED_PIXELS_PER_SECOND
        * delta_time_in_seconds
    )

    # 2. Continuous autonomous game operation (e.g. continuous downward gravity)
    updated_vertical_position += (
        AUTOMATIC_FALL_SPEED_PIXELS_PER_SECOND * delta_time_in_seconds
    )

    # 3. Boundary constraints (wrap around or clamp)
    updated_horizontal_position = max(
        0.0,
        min(updated_horizontal_position, float(WINDOW_WIDTH - SQUARE_SIZE)),
    )
    if updated_vertical_position > float(WINDOW_HEIGHT - SQUARE_SIZE):
        # Reset to top when reaching bottom boundary
        updated_vertical_position = 0.0
    elif updated_vertical_position < 0.0:
        updated_vertical_position = 0.0

    return (updated_horizontal_position, updated_vertical_position)


def render_frame(
    renderer_pointer: sdl2.SDL_Renderer,
    horizontal_position: float,
    vertical_position: float,
) -> None:
    """Render background and active game elements."""
    # Clear screen with background color
    sdl2.SDL_SetRenderDrawColor(
        renderer_pointer,
        *BACKGROUND_COLOR,
    )
    sdl2.SDL_RenderClear(renderer_pointer)

    # Draw moving square
    sdl2.SDL_SetRenderDrawColor(
        renderer_pointer,
        *SQUARE_COLOR
    )
    square_rectangle: sdl2.SDL_Rect = sdl2.SDL_Rect(
        int(round(horizontal_position)),
        int(round(vertical_position)),
        SQUARE_SIZE,
        SQUARE_SIZE,
    )
    sdl2.SDL_RenderFillRect(renderer_pointer, ctypes.byref(square_rectangle))

    # Present rendered frame to display
    sdl2.SDL_RenderPresent(renderer_pointer)


def run_application() -> None:
    """Run the continuous non-blocking main game loop."""
    (window_pointer, renderer_pointer) = initialize_window()

    horizontal_position: float = (WINDOW_WIDTH - SQUARE_SIZE) / 2.0
    vertical_position: float = 0.0

    previous_time_in_seconds: float = time.perf_counter()
    event_instance: sdl2.SDL_Event = sdl2.SDL_Event()
    is_running: bool = True

    while is_running:
        current_time_in_seconds: float = time.perf_counter()
        delta_time_in_seconds: float = (
            current_time_in_seconds - previous_time_in_seconds
        )
        previous_time_in_seconds = current_time_in_seconds

        if delta_time_in_seconds > MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS:
            delta_time_in_seconds = MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS

        # Stage 1: Non-blocking input processing
        (
            is_running,
            horizontal_movement_direction,
            vertical_movement_direction,
        ) = process_input(event_instance)

        # Stage 2: Continuous autonomous game updates
        (horizontal_position, vertical_position) = update_game_state(
            horizontal_position,
            vertical_position,
            horizontal_movement_direction,
            vertical_movement_direction,
            delta_time_in_seconds,
        )

        # Stage 3: Render frame
        render_frame(
            renderer_pointer,
            horizontal_position,
            vertical_position,
        )

    destroy_window(window_pointer, renderer_pointer)


if __name__ == "__main__":
    run_application()
