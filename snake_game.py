import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
ANIMATION_STEPS = 10  # Number of steps for smooth movement

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)  # Color for barriers
DARK_GRAY = (64, 64, 64)  # Darker shade for barrier borders
YELLOW = (255, 255, 0)  # Color for snake eyes
LIGHT_GRAY = (192, 192, 192)  # Lighter shade for barrier highlights
VERY_DARK_GRAY = (32, 32, 32)  # Very dark shade for barrier shadows
GOLD = (255, 215, 0)  # Color for bonus food
HOVER_COLOR = (100, 255, 100)  # Color for menu hover effect

# Game states
MENU = "menu"
PLAYING = "playing"
HISTORY = "history"

# Snake characteristics
SNAKE_SPEED = 60  # Increased for smoother animation
SNAKE_BLOCK_SIZE = 20
SNAKE_COLOR = GREEN
SNAKE_HEAD_COLOR = (0, 200, 0)  # Slightly darker green for head

# Food characteristics
FOOD_COLOR = RED
FOOD_SIZE = 20
BONUS_FOOD_COLOR = GOLD
BONUS_FOOD_POINTS = 5
BONUS_FOOD_CHANCE = 0.2  # 20% chance to spawn bonus food

# Barrier characteristics
BARRIER_COLOR = GRAY
BARRIER_BORDER_COLOR = DARK_GRAY
BASE_NUM_BARRIERS = 4  # Base number of wall structures
MIN_WALL_LENGTH = 5  # Minimum length of each wall
MAX_WALL_LENGTH = 8  # Maximum length of each wall

class Barrier:
    def __init__(self, position):
        self.position = position
        self.color = BARRIER_COLOR
        self.border_color = BARRIER_BORDER_COLOR
        self.pattern_offset = random.randint(0, 100)  # Random pattern offset
        self.shine_angle = random.uniform(0, 2 * 3.14159)  # Random shine angle

    def render(self, surface):
        # Base rectangle
        r = pygame.Rect((self.position[0] * GRID_SIZE,
                        self.position[1] * GRID_SIZE),
                       (GRID_SIZE, GRID_SIZE))
        
        # Draw main barrier color with gradient effect
        for i in range(GRID_SIZE):
            # Calculate gradient color
            gradient_factor = i / GRID_SIZE
            current_color = (
                int(self.color[0] * (1 - gradient_factor * 0.3)),
                int(self.color[1] * (1 - gradient_factor * 0.3)),
                int(self.color[2] * (1 - gradient_factor * 0.3))
            )
            pygame.draw.line(surface, current_color,
                           (r.left, r.top + i),
                           (r.right, r.top + i))

        # Draw 3D effect
        # Top and left edges (lighter)
        pygame.draw.line(surface, LIGHT_GRAY,
                        (r.left, r.top),
                        (r.right, r.top), 2)
        pygame.draw.line(surface, LIGHT_GRAY,
                        (r.left, r.top),
                        (r.left, r.bottom), 2)
        
        # Bottom and right edges (darker)
        pygame.draw.line(surface, VERY_DARK_GRAY,
                        (r.left, r.bottom),
                        (r.right, r.bottom), 2)
        pygame.draw.line(surface, VERY_DARK_GRAY,
                        (r.right, r.top),
                        (r.right, r.bottom), 2)

        # Draw pattern
        pattern_spacing = 4
        for i in range(0, GRID_SIZE, pattern_spacing):
            # Draw diagonal lines
            start_x = r.left + (i + self.pattern_offset) % GRID_SIZE
            pygame.draw.line(surface, DARK_GRAY,
                           (start_x, r.top),
                           (start_x + pattern_spacing, r.bottom),
                           1)

        # Draw shine effect
        shine_width = 3
        shine_pos = int((GRID_SIZE / 2) * (1 + math.sin(self.shine_angle)))
        pygame.draw.line(surface, LIGHT_GRAY,
                        (r.left + shine_pos, r.top),
                        (r.left + shine_pos + shine_width, r.top),
                        1)

        # Draw corner highlights
        corner_size = 3
        # Top-left corner
        pygame.draw.line(surface, WHITE,
                        (r.left, r.top),
                        (r.left + corner_size, r.top), 1)
        pygame.draw.line(surface, WHITE,
                        (r.left, r.top),
                        (r.left, r.top + corner_size), 1)
        
        # Bottom-right corner
        pygame.draw.line(surface, VERY_DARK_GRAY,
                        (r.right, r.bottom),
                        (r.right - corner_size, r.bottom), 1)
        pygame.draw.line(surface, VERY_DARK_GRAY,
                        (r.right, r.bottom),
                        (r.right, r.bottom - corner_size), 1)

        # Draw border
        pygame.draw.rect(surface, self.border_color, r, 1)

        # Update pattern offset and shine angle for animation
        self.pattern_offset = (self.pattern_offset + 1) % 100
        self.shine_angle += 0.1

class Snake:
    def __init__(self):
        self.length = 3  # Start with 3 segments
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        # Initialize body segments
        for i in range(self.length - 1):
            self.positions.append((GRID_WIDTH // 2 - i - 1, GRID_HEIGHT // 2))
        self.direction = RIGHT  # Start moving right
        self.color = SNAKE_COLOR
        self.score = 0
        self.animation_step = 0
        self.next_positions = []
        self.is_moving = False

    def get_head_position(self):
        return self.positions[0]

    def update(self, barriers):
        if not self.is_moving:
            self.animation_step = 0
            cur = self.get_head_position()
            x, y = self.direction
            next_head = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
            
            # Check for collision with barriers
            if any(next_head == barrier.position for barrier in barriers):
                return False
                
            if next_head in self.positions[3:]:
                return False
            
            # Calculate next positions for all segments
            self.next_positions = [next_head]
            for i in range(len(self.positions) - 1):
                self.next_positions.append(self.positions[i])
            
            # Add a new position if the snake has grown
            if len(self.next_positions) < self.length:
                self.next_positions.append(self.positions[-1])
                
            self.is_moving = True
            return True

        # Update animation step
        self.animation_step += 1
        if self.animation_step >= ANIMATION_STEPS:
            self.positions = self.next_positions
            # Only remove the last position if we haven't grown
            if len(self.positions) > self.length:
                self.positions.pop()
            self.is_moving = False
            return True

        return True

    def reset(self):
        self.length = 3  # Reset to 3 segments
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        # Initialize body segments
        for i in range(self.length - 1):
            self.positions.append((GRID_WIDTH // 2 - i - 1, GRID_HEIGHT // 2))
        self.direction = RIGHT
        self.score = 0
        self.animation_step = 0
        self.next_positions = []
        self.is_moving = False

    def get_interpolated_position(self, pos1, pos2, step):
        if not self.is_moving:
            return pos1
        x1, y1 = pos1
        x2, y2 = pos2
        progress = step / ANIMATION_STEPS
        return (x1 + (x2 - x1) * progress, y1 + (y2 - y1) * progress)

    def render(self, surface):
        for i, p in enumerate(self.positions):
            # Calculate color gradient for body segments
            if i == 0:
                color = SNAKE_HEAD_COLOR
            else:
                # Create gradient effect for body
                gradient_factor = i / len(self.positions)
                color = (
                    int(SNAKE_COLOR[0] * (1 - gradient_factor * 0.3)),
                    int(SNAKE_COLOR[1] * (1 - gradient_factor * 0.3)),
                    int(SNAKE_COLOR[2] * (1 - gradient_factor * 0.3))
                )
            
            # Calculate interpolated position for all segments
            if self.is_moving:
                if i < len(self.next_positions):
                    current_pos = self.get_interpolated_position(p, self.next_positions[i], self.animation_step)
                else:
                    current_pos = p
            else:
                current_pos = p
                
            # Convert grid position to screen position
            screen_x = current_pos[0] * GRID_SIZE
            screen_y = current_pos[1] * GRID_SIZE
            
            # Draw snake segment
            r = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, r)
            pygame.draw.rect(surface, WHITE, r, 1)
            
            # Draw eyes for the head
            if i == 0:
                # Calculate eye positions based on direction
                eye_size = 4
                if self.direction == UP:
                    left_eye = (r.left + 5, r.top + 5)
                    right_eye = (r.right - 5, r.top + 5)
                elif self.direction == DOWN:
                    left_eye = (r.left + 5, r.bottom - 5)
                    right_eye = (r.right - 5, r.bottom - 5)
                elif self.direction == LEFT:
                    left_eye = (r.left + 5, r.top + 5)
                    right_eye = (r.left + 5, r.bottom - 5)
                else:  # RIGHT
                    left_eye = (r.right - 5, r.top + 5)
                    right_eye = (r.right - 5, r.bottom - 5)
                
                # Draw eyes
                pygame.draw.circle(surface, YELLOW, left_eye, eye_size)
                pygame.draw.circle(surface, YELLOW, right_eye, eye_size)
                # Draw pupils
                pygame.draw.circle(surface, BLACK, left_eye, eye_size//2)
                pygame.draw.circle(surface, BLACK, right_eye, eye_size//2)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = FOOD_COLOR
        # Initialize with default position, will be randomized in main game loop

    def randomize_position(self, barriers, snake_positions):
        while True:
            self.position = (random.randint(0, GRID_WIDTH-1),
                           random.randint(0, GRID_HEIGHT-1))
            # Make sure food doesn't spawn on barriers or snake
            if not any(self.position == barrier.position for barrier in barriers) and \
               self.position not in snake_positions:
                break

    def render(self, surface):
        r = pygame.Rect((self.position[0] * GRID_SIZE,
                        self.position[1] * GRID_SIZE),
                       (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, WHITE, r, 1)

class BonusFood:
    def __init__(self):
        self.position = None
        self.color = BONUS_FOOD_COLOR
        self.active = False
        self.spawn_time = 0
        self.duration = 5000  # 5 seconds in milliseconds

    def spawn(self, barriers, snake_positions, food_position):
        if not self.active and random.random() < BONUS_FOOD_CHANCE:
            while True:
                self.position = (random.randint(0, GRID_WIDTH-1),
                               random.randint(0, GRID_HEIGHT-1))
                if (not any(self.position == barrier.position for barrier in barriers) and 
                    self.position not in snake_positions and 
                    self.position != food_position):
                    self.active = True
                    self.spawn_time = pygame.time.get_ticks()
                    break

    def update(self):
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.spawn_time > self.duration:
                self.active = False
                self.position = None

    def render(self, surface):
        if self.active:
            r = pygame.Rect((self.position[0] * GRID_SIZE,
                           self.position[1] * GRID_SIZE),
                          (GRID_SIZE, GRID_SIZE))
            # Draw bonus food with star effect
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, WHITE, r, 1)
            # Draw star effect
            center_x = r.centerx
            center_y = r.centery
            for i in range(5):
                angle = i * 72 - 90
                x = center_x + int(GRID_SIZE/2 * math.cos(math.radians(angle)))
                y = center_y + int(GRID_SIZE/2 * math.sin(math.radians(angle)))
                pygame.draw.line(surface, WHITE, (center_x, center_y), (x, y), 2)

# Directional constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def create_barriers(level):
    barriers = []
    num_barriers = BASE_NUM_BARRIERS + (level - 1) * 2  # Add 2 more barriers per level
    
    # Create walls in different directions
    for _ in range(num_barriers):
        # Randomly choose wall direction (horizontal or vertical)
        is_horizontal = random.choice([True, False])
        
        # Choose starting position
        if is_horizontal:
            start_x = random.randint(2, GRID_WIDTH - MAX_WALL_LENGTH - 2)
            start_y = random.randint(2, GRID_HEIGHT - 2)
            wall_length = random.randint(MIN_WALL_LENGTH, MAX_WALL_LENGTH)
            
            # Create horizontal wall
            for x in range(wall_length):
                pos = (start_x + x, start_y)
                # Avoid center area where snake starts
                if abs(pos[0] - GRID_WIDTH//2) > 3 or abs(pos[1] - GRID_HEIGHT//2) > 3:
                    barriers.append(Barrier(pos))
        else:
            start_x = random.randint(2, GRID_WIDTH - 2)
            start_y = random.randint(2, GRID_HEIGHT - MAX_WALL_LENGTH - 2)
            wall_length = random.randint(MIN_WALL_LENGTH, MAX_WALL_LENGTH)
            
            # Create vertical wall
            for y in range(wall_length):
                pos = (start_x, start_y + y)
                # Avoid center area where snake starts
                if abs(pos[0] - GRID_WIDTH//2) > 3 or abs(pos[1] - GRID_HEIGHT//2) > 3:
                    barriers.append(Barrier(pos))
    
    return barriers

class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.options = ["Start Game", "History", "Exit"]
        self.selected = 0
        self.history = []  # List to store game history
        self.load_history()

    def load_history(self):
        try:
            with open("snake_history.txt", "r") as f:
                self.history = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.history = []

    def save_history(self):
        with open("snake_history.txt", "w") as f:
            for entry in self.history:
                f.write(entry + "\n")

    def add_to_history(self, score, level):
        timestamp = pygame.time.get_ticks() // 1000  # Convert to seconds
        entry = f"Score: {score} | Level: {level} | Time: {timestamp}s"
        self.history.insert(0, entry)
        if len(self.history) > 10:  # Keep only last 10 entries
            self.history.pop()
        self.save_history()

    def render(self, surface):
        surface.fill(BLACK)
        
        # Draw title
        title = self.font.render("Snake Game", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 150))
        surface.blit(title, title_rect)

        # Draw options
        for i, option in enumerate(self.options):
            color = HOVER_COLOR if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, 300 + i * 100))
            surface.blit(text, rect)

    def render_history(self, surface):
        surface.fill(BLACK)
        
        # Draw title
        title = self.font.render("Game History", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        surface.blit(title, title_rect)

        # Draw history entries
        for i, entry in enumerate(self.history):
            text = self.small_font.render(entry, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, 150 + i * 40))
            surface.blit(text, rect)

        # Draw back button
        back_text = self.font.render("Back", True, WHITE)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100))
        surface.blit(back_text, back_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]
        return None

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game with Menu')
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()

    menu = Menu()
    game_state = MENU
    snake = None
    food = None
    bonus_food = None
    barriers = None
    level = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if game_state == MENU:
                selected = menu.handle_event(event)
                if selected == "Start Game":
                    game_state = PLAYING
                    snake = Snake()
                    food = Food()
                    bonus_food = BonusFood()
                    level = 1
                    barriers = create_barriers(level)
                    food.randomize_position(barriers, snake.positions)
                elif selected == "History":
                    game_state = HISTORY
                elif selected == "Exit":
                    pygame.quit()
                    sys.exit()
            
            elif game_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT
                    elif event.key == pygame.K_ESCAPE:
                        game_state = MENU
            
            elif game_state == HISTORY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        game_state = MENU

        # Update game state
        if game_state == PLAYING:
            # Update snake
            if not snake.update(barriers):
                menu.add_to_history(snake.score, level)
                game_state = MENU

            # Check if snake ate the food
            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 1
                food.randomize_position(barriers, snake.positions)
                bonus_food.spawn(barriers, snake.positions, food.position)
                
                # Check for level up
                if snake.length % 10 == 0:
                    level += 1
                    barriers = create_barriers(level)

            # Check if snake ate the bonus food
            if bonus_food.active and snake.get_head_position() == bonus_food.position:
                snake.score += BONUS_FOOD_POINTS
                bonus_food.active = False
                bonus_food.position = None

            # Update bonus food
            bonus_food.update()

        # Draw everything
        surface.fill(BLACK)
        
        if game_state == MENU:
            menu.render(surface)
        elif game_state == PLAYING:
            # Draw barriers first
            for barrier in barriers:
                barrier.render(surface)
                
            snake.render(surface)
            food.render(surface)
            bonus_food.render(surface)
            
            # Draw score and level
            score_text = menu.small_font.render(f'Score: {snake.score}', True, WHITE)
            level_text = menu.small_font.render(f'Level: {level}', True, WHITE)
            surface.blit(score_text, (10, 10))
            surface.blit(level_text, (10, 50))
        elif game_state == HISTORY:
            menu.render_history(surface)

        screen.blit(surface, (0, 0))
        pygame.display.update()
        clock.tick(SNAKE_SPEED)

if __name__ == '__main__':
    main() 