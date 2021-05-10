import pygame
import pygame.event
import pygame.draw
import pygame.sprite
import pygame.time
import pygame.image
import pygame.display
import pygame.key
import pygame.transform

import random


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self, top: float, left: float):
        super().__init__()

        self.images = {
            "upflap": "./flappy-bird-assets/sprites/bluebird-upflap.png",
            "downflap": "./flappy-bird-assets/sprites/bluebird-downflap.png",
            "midflap": "./flappy-bird-assets/sprites/bluebird-midflap.png",
        }

        self.swap_image(self.images["midflap"])

        self.rect = self.image.get_rect()
        self.rect.top = top - self.rect.height / 2
        self.rect.left = left - self.rect.width / 2

        self.speed_x = 0
        self.speed_y = 0
        self.speed_y_limit = 30

    def swap_image(self, image_path: str):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image,
                                           (self.image.get_width() + 20, 
                                            self.image.get_height() + 20))

    def rotate_image(self, angle: float):
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self, **kwargs):
        if kwargs.get("is_jumping"):
            self.speed_y = -10

        if self.speed_y < 0:
            self.swap_image(self.images["downflap"])
            self.rotate_image(20)
        else:
            self.swap_image(self.images["upflap"])
            self.rotate_image(-20)
        if self.speed_y < self.speed_y_limit:
            self.speed_y += 0.5

        self.rect.move_ip(self.speed_x, self.speed_y)

        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0
        if self.rect.bottom > pygame.display.get_window_size()[1]:
            self.rect.bottom = pygame.display.get_window_size()[1]
            self.speed_y = 0


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("./flappy-bird-assets/sprites/background-day.png")
        self.image = pygame.transform.scale(self.image, pygame.display.get_window_size())
        self.rect = self.image.get_rect()

    def update(self):
        pass


class Pipe(pygame.sprite.Sprite):
    def __init__(self, left: float, backspace: float = 0, position: str = "top"):
        super().__init__()

        self.image = pygame.image.load("./flappy-bird-assets/sprites/pipe-green.png")
        self.rect = self.image.get_rect()

        self.rect.left = left

        fixed_backspace = 350

        if position == "top":
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect.top = -(fixed_backspace - backspace)
        elif position == "bottom":
            self.rect.bottom = fixed_backspace + pygame.display.get_window_size()[1] + backspace

    def update(self):
        if self.rect.left + self.rect.width < 0:
            self.kill()

        self.rect.move_ip(-2, 0)


class Floor(pygame.sprite.Sprite):
    def __init__(self, left: float = 0):
        super().__init__()

        self.image = pygame.image.load("./flappy-bird-assets/sprites/base.png")
        self.rect = self.image.get_rect()

        self.rect.left = left
        self.rect.bottom = pygame.display.get_window_size()[1]

    def update(self):
        if self.rect.left + self.rect.width < 0:
            self.kill()

        self.rect.move_ip(-2, 0)


class Game:
    def __init__(self, window_size: tuple[int, int], fps: int = 60):
        self.window_size = window_size
        self.fps = fps

        pygame.init()

        self.display = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()

        self.background = pygame.sprite.RenderPlain(Background())
        self.floor = pygame.sprite.Group(Floor(), Floor(self.window_size[0] / 2))
        self.player = pygame.sprite.RenderPlain(Player(self.window_size[0] / 2, self.window_size[1] / 2))
        self.pipes = pygame.sprite.Group(
            Pipe(800),
            Pipe(800, position="bottom"),
            # Pipe(800, backspace=10),
            # Pipe(800, backspace=200, position="bottom")
        )

        self.running = True

    def add_pipe(self):
        height = random.randint(-300, 100)

        if len(self.pipes) < 4:
            distance = 1600
        else:
            distance = 1200

        bottom_pipe = Pipe(distance, backspace=height, position="bottom")
        upper_pipe = Pipe(distance, backspace=height)

        self.pipes.add(bottom_pipe, upper_pipe)

    def add_floor(self):
        self.floor.add(Floor((self.window_size[0] / 2 * 2)))

    def loop(self):
        while self.running:
            self.events = pygame.event.get()

            jumping = False

            for e in self.events:
                if e.type == pygame.QUIT:
                    self.running = False

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP:
                        jumping = True

            self.display.fill(Color.BLACK)
            self.clock.tick(self.fps)

            if len(self.pipes) < 6:
                self.add_pipe()
            if len(self.floor) < 3:
                self.add_floor()

            self.player.update(is_jumping=jumping)
            self.pipes.update()
            self.floor.update()
 
            self.background.draw(self.display)
            self.pipes.draw(self.display)
            self.player.draw(self.display)
            self.floor.draw(self.display)

            collision = pygame.sprite.spritecollideany(self.player.sprites()[0], self.pipes)

            if collision:
                self.running = False

            pygame.display.flip()


if __name__ == "__main__":
    game = Game((600, 640))
    game.loop()