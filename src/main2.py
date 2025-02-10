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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
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
        for coin in self.coins[:]:
            coin.update()
            if coin.check_collision(self.monsters):
                self.monsters.remove(coin.target)
                self.coins.remove(coin)
            elif coin.check_collision_with_player(self.player):
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
            self.coins.append(Coin(self.player.x, self.player.y, angle))
            self.player.coins -= 1
    
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
        
        # Bounce off walls
        if self.x <= 0 or self.x >= WIDTH - 20:
            self.speed_x = -self.speed_x
        if self.y <= 0 or self.y >= HEIGHT - 20:
            self.speed_y = -self.speed_y
    
    def check_collision(self, monsters):
        for monster in monsters:
            if abs(self.x - monster.x) < 20 and abs(self.y - monster.y) < 20:
                self.target = monster
                return True
        return False
    
    def check_collision_with_player(self, player):
        return abs(self.x - player.x) < 20 and abs(self.y - player.y) < 20
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

if __name__ == "__main__":
    game = Game()
    game.run()
