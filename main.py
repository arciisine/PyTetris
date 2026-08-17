"""Sample SDL-based application moving a square using keyboard input."""

import sys
import pygame


def run_application() -> None:
    """Initialize SDL, configure window, and run main game loop."""
    pygame.init()

    window_width: int = 800
    window_height: int = 600
    display_surface: pygame.Surface = pygame.display.set_mode(
        (window_width, window_height)
    )
    pygame.display.set_caption("SDL Keyboard Movement Example")

    clock_timer: pygame.time.Clock = pygame.time.Clock()
    frames_per_second: int = 60

    square_size: int = 50
    horizontal_position: float = (window_width - square_size) / 2.0
    vertical_position: float = (window_height - square_size) / 2.0
    movement_speed_pixels_per_second: float = 300.0

    background_color: tuple[int, int, int] = (30, 30, 35)
    square_color: tuple[int, int, int] = (70, 160, 240)

    is_running: bool = True

    while is_running:
        delta_time_in_seconds: float = clock_timer.tick(frames_per_second) / 1000.0

        for current_event in pygame.event.get():
            if current_event.type == pygame.QUIT:
                is_running = False
            elif current_event.type == pygame.KEYDOWN:
                if current_event.key == pygame.K_ESCAPE:
                    is_running = False

        keys_pressed = pygame.key.get_pressed()

        horizontal_movement_direction: float = 0.0
        vertical_movement_direction: float = 0.0

        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            horizontal_movement_direction -= 1.0
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            horizontal_movement_direction += 1.0
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            vertical_movement_direction -= 1.0
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            vertical_movement_direction += 1.0

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
            0.0, min(horizontal_position, float(window_width - square_size))
        )
        vertical_position = max(
            0.0, min(vertical_position, float(window_height - square_size))
        )

        display_surface.fill(background_color)

        square_rectangle = pygame.Rect(
            int(horizontal_position),
            int(vertical_position),
            square_size,
            square_size,
        )
        pygame.draw.rect(display_surface, square_color, square_rectangle)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_application()
