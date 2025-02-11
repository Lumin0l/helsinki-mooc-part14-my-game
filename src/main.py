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
COIN_SPEED = 5
COIN_SPAWN_INTERVAL = 10000  # Time in milliseconds (10 seconds)
COIN_SPAWN_OFFSET = 20

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
        self.coins = []
        self.monster_limit = INITIAL_MONSTER_LIMIT
        self.start_time = pygame.time.get_ticks()
        self.score = 0
        pygame.time.set_timer(pygame.USEREVENT, MONSTER_SPAWN_INTERVAL)
        pygame.time.set_timer(pygame.USEREVENT + 1, COIN_SPAWN_INTERVAL)
    
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
            elif event.type == pygame.USEREVENT + 1:
                self.spawn_coin()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.shoot_coin()
    
    def update(self):
        self.player.update()
        for door in self.doors[:]:
            door.update()
            if door.timer_expired():
                self.spawn_monster(door.x, door.y)
                self.doors.remove(door)
        for monster in self.monsters[:]:
            monster.update(self.player.x, self.player.y)
            if self.check_collision(monster, self.player):
                self.game_over()
        for coin in self.coins[:]:
            coin.update()
            if coin.check_collision(self.monsters):
                self.monsters.remove(coin.target)
                self.coins.remove(coin)
                self.score += 1
            if coin.check_collision_with_player(self.player):
                self.player.coins += 1
                self.coins.remove(coin)
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
        for coin in self.coins:
            coin.draw(self.window)
        self.draw_timer_and_score()
        pygame.display.flip()
    
    def spawn_door(self):
        if len(self.monsters) + len(self.doors) < self.monster_limit:
            x, y = self.get_random_border_position()
            self.doors.append(Door(x, y))
    
    def spawn_monster(self, x, y):
        behavior = random.choice(["random", "chase"])
        self.monsters.append(Monster(x, y, behavior))
    
    def shoot_coin(self):
        if self.player.coins > 0:
            angle = self.player.arrow_angle
            spawn_x = self.player.x + self.player.robot_width // 2 + COIN_SPAWN_OFFSET * math.cos(math.radians(angle))
            spawn_y = self.player.y + self.player.robot_height // 2 + COIN_SPAWN_OFFSET * math.sin(math.radians(angle))
            self.coins.append(Coin(spawn_x, spawn_y, angle))
            self.player.coins -= 1
    
    def spawn_coin(self):
        x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.coins.append(Coin(x, y, 0))
    
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
    
    def check_collision(self, monster, player):
        return abs(monster.x - player.x) < 20 and abs(monster.y - player.y) < 20
    
    def game_over(self):
        self.running = False
        print(f"Game Over! You lasted {pygame.time.get_ticks() - self.start_time} milliseconds and scored {self.score} points.")
    
    def draw_timer_and_score(self):
        font = pygame.font.Font(None, 36)
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = font.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.window.blit(timer_text, (WIDTH - 200, 10))
        self.window.blit(score_text, (WIDTH - 200, 50))

class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.image = pygame.image.load("door.png")
    
    def update(self):
        pass  # No movement or logic needed for the door itself
    
    def timer_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= DOOR_LIFETIME
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

class Player:
    def __init__(self, x, y):
        self.robot = pygame.image.load("robot.png")
        self.robot_width = self.robot.get_width()
        self.robot_height = self.robot.get_height()
        self.x = x - self.robot_width // 2
        self.y = y - self.robot_height // 2
        self.arrow_angle = 0
        self.coins = 10
    
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

class Coin:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed_x = COIN_SPEED * math.cos(math.radians(angle))
        self.speed_y = COIN_SPEED * math.sin(math.radians(angle))
        self.image = pygame.image.load("coin.png")

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off walls correctly
        if self.x <= 0 or self.x >= WIDTH - self.image.get_width():
            self.speed_x = -self.speed_x
        if self.y <= 0 or self.y >= HEIGHT - self.image.get_height():
            self.speed_y = -self.speed_y

    def check_collision(self, monsters):
        for monster in monsters:
            if abs(self.x - monster.x) < 20 and abs(self.y - monster.y) < 20:
                self.target = monster
                return True
        return False

    def check_collision_with_player(self, player):
        """ Returns True if the coin collides with the player. """
        return (
            abs(self.x - player.x) < 20 and
            abs(self.y - player.y) < 20
        )

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))


if __name__ == "__main__":
    game = Game()
    game.run()