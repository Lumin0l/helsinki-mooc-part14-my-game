### Disclaimer from Imanol, the creator ###
# It was a challenge to make this game, and it is not perfect. There is no "win" condition—the objective is simply to last as long as possible, and that's it.
# It has several flaws: the player can't shoot coins at certain angles (I did my best but couldn't figure it out), and the bottom of the screen is not properly bordered, so some sprites get cut off halfway.
# Hitboxes are also not optimized, and only headshots count, which is a bit unfair.
# Nonetheless, as a teacher once said, "Perfection is the enemy of completion," and I am uploading this on the eve of the last exam. So, I'm happy with the result, and I hope you enjoy it too.
# Thank you for your time, and have a great day!


import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1080, 720
BACKGROUND_COLOR = (139, 0, 0)
PLAYER_SPEED = 3
ARROW_LENGTH = 40
ROTATION_SPEED = 3
MONSTER_SPAWN_INTERVAL = 10000  # Monsters take a bit to spawn, adjust if you want a more hardcore experience
DOOR_LIFETIME = 5000
INITIAL_MONSTER_LIMIT = 3
MONSTER_SPEED_RANGE = (2, 4)
COIN_SPEED = 5
COIN_SPAWN_INTERVAL = 10000
COIN_SPAWN_OFFSET = 40
# Double line breaks are intentional, text was a bit crowded otherwise
STORY_STRING = """You are a trans-human who turned into a robot. But that had a cost.\n
Now, those who lent you money to achieve this goal are coming to get their money back, AS GHOSTS!!!!\n
It is your duty to repay your debts and enjoy life as a robot. In more "gamey" terms, you have to survive as long as possible."""
MECHANICS_STRING = """Use arrow keys to move, A and D to aim, and SPACE to shoot coins.\n
Coins can be used to hit the ghosts and send them to debt-collector heaven, they will also spawn at random locations every 10 seconds and can be collected by the robot.\n
Totally on purpose *ahem* coins will only be collected or eliminate ghosts with headshots, so AIM FOR THE HEAD!!!\nGood luck!!"""
FONT = pygame.font.Font(None, 36)

# Game states
START_SCREEN_PART1 = 0
START_SCREEN_PART2 = 1
GAME_RUNNING = 2
GAME_OVER = 3

# Initialize game window
class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Robot Survival")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = START_SCREEN_PART1
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
            elif self.state == GAME_RUNNING:
                if event.type == pygame.USEREVENT:
                    self.spawn_door()
                elif event.type == pygame.USEREVENT + 1:
                    self.spawn_coin()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.shoot_coin()
            elif self.state == START_SCREEN_PART1 or self.state == START_SCREEN_PART2:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_start_screen_click()
            elif self.state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_game_over_click()
    
    def update(self):
        if self.state == GAME_RUNNING:
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
            elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
            self.monster_limit = INITIAL_MONSTER_LIMIT + (elapsed_time // 30)
    
    def draw(self):
        self.window.fill(BACKGROUND_COLOR)
        if self.state == START_SCREEN_PART1:
            self.draw_start_screen_part1()
        elif self.state == START_SCREEN_PART2:
            self.draw_start_screen_part2()
        elif self.state == GAME_RUNNING:
            self.player.draw(self.window)
            for door in self.doors:
                door.draw(self.window)
            for monster in self.monsters:
                monster.draw(self.window)
            for coin in self.coins:
                coin.draw(self.window)
            self.draw_timer_and_score()
        elif self.state == GAME_OVER:
            self.draw_game_over_screen()
        pygame.display.flip()

    # So silly, took me a while of messing with "f" before checking...: https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
    def blit_text(self, surface, text, pos, font=FONT, color=(255, 255, 255)):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = WIDTH, HEIGHT
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
    
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
        self.state = GAME_OVER
        self.end_time = pygame.time.get_ticks()
    
    def draw_timer_and_score(self):
        font = pygame.font.Font(None, 36)
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = font.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.window.blit(timer_text, (WIDTH - 200, 10))
        self.window.blit(score_text, (WIDTH - 200, 50))
    
    def draw_start_screen_part1(self):
        font = pygame.font.Font(None, 74)
        title_text = font.render("Robot Payback", True, (255, 255, 255))
        self.window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        font = pygame.font.Font(None, 36)
        self.blit_text(self.window, STORY_STRING, (150, 260))
        continue_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(self.window, ( 28, 173, 52 ), continue_button)
        continue_text = font.render("Continue", True, (255, 255, 255))
        self.window.blit(continue_text, (continue_button.x + 50, continue_button.y + 10))

    def draw_start_screen_part2(self):
        font = pygame.font.Font(None, 36)
        self.blit_text(self.window, MECHANICS_STRING, (100, 150))        
        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(self.window, (28, 173, 52), start_button)
        start_text = font.render("Start", True, (255, 255, 255))
        self.window.blit(start_text, (start_button.x + 50, start_button.y + 10))
    
    def draw_game_over_screen(self):
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        self.window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
        
        font = pygame.font.Font(None, 36)
        elapsed_time = (self.end_time - self.start_time) // 1000
        stats_text = font.render(f"Time: {elapsed_time}s, Score: {self.score}", True, (255, 255, 255))
        self.window.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2))
        
        restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(self.window, (0, 255, 0), restart_button)
        restart_text = font.render("Restart", True, (0, 0, 0))
        self.window.blit(restart_text, (restart_button.x + 50, restart_button.y + 10))
        
        exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 50)
        pygame.draw.rect(self.window, (255, 0, 0), exit_button)
        exit_text = font.render("Exit", True, (0, 0, 0))
        self.window.blit(exit_text, (exit_button.x + 70, exit_button.y + 10))
    
    def handle_start_screen_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == START_SCREEN_PART1:
            continue_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
            if continue_button.collidepoint(mouse_pos):
                self.state = START_SCREEN_PART2
        elif self.state == START_SCREEN_PART2:
            start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
            if start_button.collidepoint(mouse_pos):
                self.state = GAME_RUNNING
                self.start_time = pygame.time.get_ticks()
    
    def handle_game_over_click(self):
        mouse_pos = pygame.mouse.get_pos()
        restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 50)
        if restart_button.collidepoint(mouse_pos):
            self.reset_game()
        elif exit_button.collidepoint(mouse_pos):
            self.running = False
    
    def reset_game(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.monsters = []
        self.doors = []
        self.coins = []
        self.monster_limit = INITIAL_MONSTER_LIMIT
        self.start_time = pygame.time.get_ticks()
        self.score = 0
        self.state = GAME_RUNNING

class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.image = pygame.image.load("door.png")
    
    def update(self):
        pass
    
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
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.robot_width:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.robot_height:
            self.y += PLAYER_SPEED
        
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