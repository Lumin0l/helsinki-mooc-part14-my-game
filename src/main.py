import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1080, 720  # Updated screen size
BACKGROUND_COLOR = (139, 0, 0)  # Dark red for the carpet
PLAYER_SPEED = 3
ARROW_LENGTH = 40  # Length of aim arrow
ROTATION_SPEED = 3  # Speed of arrow rotation
MONSTER_SPAWN_INTERVAL = 10000  # Time in milliseconds (10 seconds)
DOOR_LIFETIME = 5000  # Time in milliseconds (5 seconds)
INITIAL_MONSTER_LIMIT = 3
MONSTER_SPEED_RANGE = (2, 4)

# Initialize game window
class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Robot Survival")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.monsters = []
        self.doors = []
        self.monster_limit = INITIAL_MONSTER_LIMIT
        self.start_time = pygame.time.get_ticks()
        pygame.time.set_timer(pygame.USEREVENT, MONSTER_SPAWN_INTERVAL)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.USEREVENT:
                self.spawn_door()
    
    def update(self):
        self.player.update()
        for door in self.doors[:]:
            door.update()
            if door.timer_expired():
                self.spawn_monster(door.x, door.y)
                self.doors.remove(door)
        for monster in self.monsters:
            monster.update(self.player.x, self.player.y)
        # Increase monster limit every 30 seconds
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        self.monster_limit = INITIAL_MONSTER_LIMIT + (elapsed_time // 30)
    
    def draw(self):
        self.window.fill(BACKGROUND_COLOR)
        self.player.draw(self.window)
        for door in self.doors:
            door.draw(self.window)
        for monster in self.monsters:
            monster.draw(self.window)
        pygame.display.flip()
    
    def spawn_door(self):
        if len(self.monsters) + len(self.doors) < self.monster_limit:
            x, y = self.get_random_border_position()
            self.doors.append(Door(x, y))
    
    def spawn_monster(self, x, y):
        behavior = random.choice(["random", "chase"])
        self.monsters.append(Monster(x, y, behavior))
    
    def get_random_border_position(self):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return random.randint(0, WIDTH), 0
        elif side == "bottom":
            return random.randint(0, WIDTH), HEIGHT - 40
        elif side == "left":
            return 0, random.randint(0, HEIGHT)
        else:
            return WIDTH - 40, random.randint(0, HEIGHT)

class Player:
    def __init__(self, x, y):
        self.robot = pygame.image.load("robot.png")
        self.robot_width = self.robot.get_width()
        self.robot_height = self.robot.get_height()
        self.x = x - self.robot_width // 2
        self.y = y - self.robot_height // 2
        self.arrow_angle = 0
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Player movement logic
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.robot_width:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.robot_height:
            self.y += PLAYER_SPEED
        
        # Aim arrow rotation logic
        if keys[pygame.K_a]:
            self.arrow_angle -= ROTATION_SPEED
        if keys[pygame.K_d]:
            self.arrow_angle += ROTATION_SPEED
    
    def draw(self, window):
        window.blit(self.robot, (self.x, self.y))
        
        # Calculate arrow position
        arrow_x = self.x + self.robot_width // 2 + ARROW_LENGTH * math.cos(math.radians(self.arrow_angle))
        arrow_y = self.y + self.robot_height // 2 + ARROW_LENGTH * math.sin(math.radians(self.arrow_angle))
        
        pygame.draw.line(window, (255, 255, 255),
                         (self.x + self.robot_width // 2, self.y + self.robot_height // 2),
                         (arrow_x, arrow_y), 3)

class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.image = pygame.image.load("door.png")
    
    def update(self):
        pass
    
    def timer_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > DOOR_LIFETIME
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

class Monster:
    def __init__(self, x, y, behavior):
        self.x = x
        self.y = y
        self.speed = random.randint(*MONSTER_SPEED_RANGE)
        self.behavior = behavior
        self.image = pygame.image.load("monster.png")
        self.dx = random.choice([-1, 1]) * self.speed
        self.dy = random.choice([-1, 1]) * self.speed
    
    def update(self, player_x, player_y):
        if self.behavior == "chase":
            if self.x < player_x:
                self.x += self.speed
            elif self.x > player_x:
                self.x -= self.speed
            if self.y < player_y:
                self.y += self.speed
            elif self.y > player_y:
                self.y -= self.speed
        else:
            if self.x <= 0 or self.x >= WIDTH - 40:
                self.dx = -self.dx
            if self.y <= 0 or self.y >= HEIGHT - 40:
                self.dy = -self.dy
            self.x += self.dx
            self.y += self.dy
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
        

if __name__ == "__main__":
    game = Game()
    game.run()
