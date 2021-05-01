from abc import abstractmethod

import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.key
import pygame.time
import pygame.sprite


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class Game:
    def __init__(self, width: int, height: int):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((self.width, self.height))

        self.game_objects: list[GameObject] = []
        self.running = True

    def loop(self):
        while self.running:
            self.clock.tick(60)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
            
            key_pressed = pygame.key.get_pressed()

            self.display.fill(Color.BLACK)

            for obj in self.game_objects:
                obj.update(self.display, key_pressed)

            pygame.display.flip()


class GameObject:
    @abstractmethod
    def update(self, surface: pygame.Surface, key_pressed: int): ...


class Structure(GameObject):
    def __init__(self, game: Game, left: float, top: float):
        self.game = game
        self.width = 80
        self.height = 20
        self.rect = pygame.Rect(left, top, self.width, self.height)

    def update(self, surface: pygame.Surface, key_pressed: int):
        pygame.draw.rect(surface, Color.RED, self.rect)
        

class Player(GameObject):
    def __init__(self, game: Game):
        self.game = game
        self.moving = False
        self.speed = 10
        self.width = 80
        self.height = 20
        self.rect = pygame.Rect((self.game.width / 2) - self.width / 2, 
                                self.game.height - self.height, 
                                self.width, 
                                self.height)

    def update(self, surface: pygame.Surface, key_pressed: int):
        if key_pressed[pygame.K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
            self.moving = "left"

        if key_pressed[pygame.K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
            self.moving = "right"

        if not key_pressed[pygame.K_RIGHT] or not key_pressed[pygame.K_LEFT]:
            self.moving = None

        if self.rect.right > self.game.width:
            self.rect.right = self.game.width
        if self.rect.left < 0:
            self.rect.left = 0

        pygame.draw.rect(surface, Color.BLUE, self.rect)


class Ball(GameObject):
    def __init__(self, game: Game):
        self.game = game
        self.direction = "down"
        self.speed_x = 5
        self.speed_y = 5
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect((self.game.width / 2) - self.width / 2, 
                                (self.game.height / 3) - self.height / 2, 
                                self.width, 
                                self.height)

    def update(self, surface: pygame.Surface, key_pressed: int):
        self.rect.move_ip(self.speed_x, self.speed_y)

        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = -self.speed_y
        if self.rect.bottom > self.game.height:
            self.game.running = False

        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x = -self.speed_x
        if self.rect.right > self.game.width:
            self.rect.right = self.game.width
            self.speed_x = -self.speed_x

        for obj in self.game.game_objects:
            if type(obj) is Player:
                if self.rect.colliderect(obj.rect) == 1:
                    self.speed_y = -self.speed_y

                    if obj.moving == "left":
                        self.speed_x = -2
                    if obj.moving == "right":
                        self.speed_x = 2

            if type(obj) is Structure:
                if self.rect.colliderect(obj.rect) == 1:
                    self.game.game_objects.remove(obj)
                    self.speed_y = -self.speed_y

        pygame.draw.ellipse(surface, Color.WHITE, self.rect)


if __name__ == "__main__":
    game = Game(800, 640)
    game.game_objects = [
        Player(game),
        Ball(game),
        Structure(game, 0, 0),
        Structure(game, 82, 0),
        Structure(game, 164, 0),
        Structure(game, 246, 0),
        Structure(game, 328, 0),
        Structure(game, 410, 0),
        Structure(game, 492, 0),
    ]
    game.loop()