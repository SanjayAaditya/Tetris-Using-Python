import pygame
import random

# Constants
WIDTH, HEIGHT = 200, 300
GRID_SIZE = 25  # Size of each small grid cell

# Reduce GRID_WIDTH to make the grid shorter horizontally
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Adjust GRID_WIDTH and GRID_HEIGHT to double the number of grids
GRID_WIDTH *= 2
GRID_HEIGHT *= 2

# Calculate the new window size based on the doubled grids
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE

# Colors
WHITE = (255, 255, 255)
DARK_GRAY = (100, 100, 100)  # Slightly darker gray color
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (50, 50, 50)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

SHAPES_COLORS = [
    (255, 100, 100),  # Light Red
    (100, 255, 100),  # Light Green
    (100, 100, 255),  # Light Blue
    (255, 255, 100),  # Light Yellow
    (255, 100, 255),  # Light Magenta
    (100, 255, 255),  # Light Cyan
    (200, 200, 200),  # Light Gray
]

# Initial falling speed
INITIAL_SPEED = 10
# Speed increase per level
SPEED_INCREASE = 1
# Frames per second
FPS = 60

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_tetromino = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.frame_counter = 0
        self.level = 1
        self.speed = INITIAL_SPEED
        self.acceleration_counter = 0
        self.acceleration_interval = 10  # Increase this value to change the acceleration rate
        self.initial_speed = INITIAL_SPEED
        self.locked_tetromino = None  # Store the landed tetromino

        self.spawn_tetromino()

        # Dictionary to track key states
        self.keys_held = {
            'left': False,
            'right': False,
            'down': False
        }
    def draw_grid(self):
        if self.current_tetromino:
            # Store a copy of the grid to restore it after drawing the highlight
            grid_copy = [row[:] for row in self.grid]

            # Draw the highlight behind the falling block
            for y, row in enumerate(self.current_tetromino):
                for x, cell in enumerate(row):
                    if cell:
                        grid_x = self.current_x + x
                        grid_y = self.current_y + y
                        if not self.grid[grid_y][grid_x]:
                            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, pygame.Rect(grid_x * GRID_SIZE, 0, GRID_SIZE, HEIGHT))

            # Restore the original grid
            self.grid = [row[:] for row in grid_copy]

        # Draw grid outline
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, BLACK, (x * GRID_SIZE, 0), (x * GRID_SIZE, HEIGHT))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, BLACK, (0, y * GRID_SIZE), (WIDTH, y * GRID_SIZE))

        # Draw already placed blocks
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, cell, pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, BLACK, pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)  # Outline

    def draw_tetromino(self):
        for y, row in enumerate(self.current_tetromino):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_color,
                                     pygame.Rect((self.current_x + x) * GRID_SIZE, (self.current_y + y) * GRID_SIZE,
                                                 GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(self.screen, BLACK,
                                 pygame.Rect((self.current_x + x) * GRID_SIZE, (self.current_y + y) * GRID_SIZE,
                                             GRID_SIZE, GRID_SIZE), 1)  # Outline

    def move_tetromino(self, dx, dy):
        if self.is_valid_move(dx, dy):
            self.current_x += dx
            self.current_y += dy
            return True
        return False

    def rotate_tetromino(self):
        new_tetromino = list(zip(*reversed(self.current_tetromino)))
        if self.is_valid_move(0, 0, new_tetromino):
            self.current_tetromino = new_tetromino

    def is_valid_move(self, dx, dy, tetromino=None):
        tetromino = tetromino or self.current_tetromino
        for y, row in enumerate(tetromino):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_x + x + dx
                    grid_y = self.current_y + y + dy
                    if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT) or \
                            self.grid[grid_y][grid_x]:
                        return False
        return True

    def clear_rows(self):
        rows_to_clear = []
        for y, row in enumerate(self.grid):
            if all(row):
                rows_to_clear.append(y)

        for y in reversed(rows_to_clear):
            original_color = self.grid[y][0]

            frame_count = 0

            for _ in range(5):  # Change colors 5 times for the strobing effect
                # Generate random strobing colors
                strobing_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                if frame_count % 2 == 0:
                    self.grid[y] = [original_color] * GRID_WIDTH
                else:
                    self.grid[y] = [strobing_color] * GRID_WIDTH

                self.screen.fill(DARK_GRAY)
                self.draw_grid()
                self.draw_tetromino()
                pygame.display.flip()
                self.clock.tick(self.speed)

                frame_count += 1

            del self.grid[y]
            self.grid.insert(0, [0] * GRID_WIDTH)
            self.score += 100
            self.frame_counter += 1
            if self.frame_counter >= 40:
                self.speed += SPEED_INCREASE
                self.frame_counter = 0
                self.level += 1

    def spawn_tetromino(self):
        self.current_tetromino = random.choice(SHAPES)
        self.current_color = SHAPES_COLORS[random.randint(0, len(SHAPES_COLORS) - 1)]
        self.current_x = (GRID_WIDTH - len(self.current_tetromino[0])) // 2
        self.current_y = 0

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.keys_held['left'] = -1
                elif event.key == pygame.K_RIGHT:
                    self.keys_held['right'] = 1
                elif event.key == pygame.K_DOWN:
                    self.keys_held['down'] = 1
                elif event.key == pygame.K_UP:
                    self.rotate_tetromino()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and self.keys_held.get('left') == -1:
                    self.keys_held['left'] = 0
                    self.acceleration_counter = 0
                elif event.key == pygame.K_RIGHT and self.keys_held.get('right') == 1:
                    self.keys_held['right'] = 0
                    self.acceleration_counter = 0
                elif event.key == pygame.K_DOWN and self.keys_held.get('down') == 1:
                    self.keys_held['down'] = 0
                    self.acceleration_counter = 0

        self.acceleration_counter += 1
        if self.keys_held.get('left') == -1:
            self.move_tetromino(-1, 0)
            if self.acceleration_counter % self.acceleration_interval == 0:
                self.move_tetromino(-1, 0)
        if self.keys_held.get('right') == 1:
            self.move_tetromino(1, 0)
            if self.acceleration_counter % self.acceleration_interval == 0:
                self.move_tetromino(1, 0)
        if self.keys_held.get('down') == 1:
            if not self.move_tetromino(0, 1):
                self.lock_tetromino()
                self.acceleration_counter = 0

    def run(self):
        running = True
        lock_delay = 0  # Counter for lock delay
        lock_delay_duration = 10  # Duration of lock delay in frames (adjust as needed)
        allow_adjustment = True  # Flag to allow adjustment during lock delay

        while running:
            self.handle_input()

            if not self.move_tetromino(0, 1):
                if lock_delay < lock_delay_duration:
                    # Allow adjustment during lock delay
                    if allow_adjustment:
                        self.handle_input()
                        allow_adjustment = False  # Disallow further adjustment after lock delay

                    lock_delay += 1
                else:
                    self.lock_tetromino()
                    lock_delay = 0
                    allow_adjustment = True

            self.clear_rows()

            self.screen.fill(DARK_GRAY)
            self.draw_grid()
            self.draw_tetromino()
            pygame.display.flip()
            self.clock.tick(self.speed)

    def lock_tetromino(self):
        for y, row in enumerate(self.current_tetromino):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_x + x
                    grid_y = self.current_y + y
                    self.grid[grid_y][grid_x] = self.current_color

        self.locked_tetromino = (self.current_tetromino, self.current_color, self.current_x, self.current_y)
        self.spawn_tetromino()

        if not self.is_valid_move(0, 0):
            # Quit the game or handle game over logic here
            pass


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
