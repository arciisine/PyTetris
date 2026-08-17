"""Sample pure SDL2 application moving a square with keyboard input."""

import ctypes
import math
import sys
import time
import sdl2

WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600
WINDOW_TITLE: str = "Pure SDL2 Keyboard Movement Example"
SQUARE_SIZE: int = 50
MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS: float = 0.05

def initialize_window() -> tuple[sdl2.SDL_Window, sdl2.SDL_Renderer]:
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
    sdl2.SDL_DestroyRenderer(renderer_pointer)
    sdl2.SDL_DestroyWindow(window_pointer)
    sdl2.SDL_Quit()
    sys.exit(0)

def run_application() -> None:
    """Run main game loop."""

    (window_pointer, renderer_pointer) = initialize_window()

    horizontal_position: float = (WINDOW_WIDTH - SQUARE_SIZE) / 2.0
    vertical_position: float = (WINDOW_HEIGHT - SQUARE_SIZE) / 2.0
    movement_speed_pixels_per_second: float = 350.0

    previous_time_in_seconds: float = time.perf_counter()

    is_running: bool = True
    event_instance: sdl2.SDL_Event = sdl2.SDL_Event()

    while is_running:
        current_time_in_seconds: float = time.perf_counter()
        delta_time_in_seconds: float = (
            current_time_in_seconds - previous_time_in_seconds
        )
        previous_time_in_seconds = current_time_in_seconds

        if delta_time_in_seconds > MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS:
            delta_time_in_seconds = MAXIMUM_ALLOWED_DELTA_TIME_IN_SECONDS

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

        horizontal_position += (
            horizontal_movement_direction
            * movement_speed_pixels_per_second
            * delta_time_in_seconds
        )
        vertical_position += (
            vertical_movement_direction
            * movement_speed_pixels_per_second
            * delta_time_in_seconds
        )

        horizontal_position = max(
            0.0,
            min(horizontal_position, float(WINDOW_WIDTH - SQUARE_SIZE)),
        )
        vertical_position = max(
            0.0,
            min(vertical_position, float(WINDOW_HEIGHT - SQUARE_SIZE)),
        )

        # Clear screen with background color
        sdl2.SDL_SetRenderDrawColor(renderer_pointer, 30, 30, 35, 255)
        sdl2.SDL_RenderClear(renderer_pointer)

        # Draw square
        sdl2.SDL_SetRenderDrawColor(renderer_pointer, 70, 160, 240, 255)
        square_rectangle: sdl2.SDL_Rect = sdl2.SDL_Rect(
            int(round(horizontal_position)),
            int(round(vertical_position)),
            SQUARE_SIZE,
            SQUARE_SIZE,
        )
        sdl2.SDL_RenderFillRect(renderer_pointer, ctypes.byref(square_rectangle))

        # Present rendered frame
        sdl2.SDL_RenderPresent(renderer_pointer)

    destroy_window(window_pointer, renderer_pointer)


if __name__ == "__main__":
    run_application()
