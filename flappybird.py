import pygame
import pygame.event
import pygame.draw
import pygame.sprite
import pygame.time
import pygame.image
import pygame.display
import pygame.key
import pygame.transform
import pygame.mouse
import pygame.mixer

import random


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.images = {
            "upflap": "./flappy-bird-assets/sprites/bluebird-upflap.png",
            "downflap": "./flappy-bird-assets/sprites/bluebird-downflap.png",
            "midflap": "./flappy-bird-assets/sprites/bluebird-midflap.png",
        }

        self.swap_image(self.images["midflap"])

        self.rect = self.image.get_rect()
        self.rect.top = pygame.display.get_window_size()[1] / 2 - self.rect.height / 2
        self.rect.left = pygame.display.get_window_size()[0] / 2 - self.rect.width / 2

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

    def update(self, **kwargs: dict):
        if kwargs.get("is_jumping"):
            self.speed_y = -10

        if self.speed_y < 0:
            self.swap_image(self.images["downflap"])
            # self.rotate_image(20)
        else:
            self.swap_image(self.images["upflap"])
            # self.rotate_image(-20)
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

        if position == "top":
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect.top = -(pygame.display.get_window_size()[1] / 2) + backspace
        elif position == "bottom":
            self.rect.top = (pygame.display.get_window_size()[1] / 2) + backspace

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
            self.rect.left = pygame.display.get_window_size()[0]

        self.rect.move_ip(-2, 0)


class Message(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("./flappy-bird-assets/sprites/message.png")
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        
        wx = pygame.display.get_window_size()[0] / 2 - self.rect.width / 2
        wy = pygame.display.get_window_size()[1] / 2 - self.rect.height / 2

        self.rect.top = wy
        self.rect.left = wx

        self.waiting_for_input = True

    def update(self):
        right_click, _, _ = pygame.mouse.get_pressed()

        if right_click:
            self.waiting_for_input = False


class GameOver(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("./flappy-bird-assets/sprites/gameover.png")
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        
        wx = pygame.display.get_window_size()[0] / 2 - self.rect.width / 2
        wy = pygame.display.get_window_size()[1] / 2 - self.rect.height / 2

        self.rect.top = wy
        self.rect.left = wx

        self.waiting_for_input = False

    def update(self):
        right_click, _, _ = pygame.mouse.get_pressed()

        if right_click:
            self.waiting_for_input = False


class Score(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.load_score_image(0)

    def load_score_image(self, score: int):
        self.image = pygame.image.load(f"./flappy-bird-assets/sprites/{score}.png")
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = pygame.display.get_window_size()[0] / 4
        self.rect.top = pygame.display.get_window_size()[1] / 4

        self.sound = pygame.mixer.Sound("./flappy-bird-assets/audio/point.wav")

    def update(self, **kwargs: dict):
        new_score = kwargs.get("score", 0)

        if new_score > 0:
            self.sound.play()
        self.load_score_image(new_score)


class Game:
    def __init__(self, window_size: tuple[int, int], fps: int = 60):
        self.window_size = window_size
        self.fps = fps

        pygame.init()
        pygame.display.set_caption("Flappybird")

        self.display = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()

        self.background = pygame.sprite.RenderPlain()
        self.floor = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.spawn_player()

        self.is_dead = True
        self.is_gameover = False
        self.score_value = 0
        self.pipelines: list[pygame.Rect] = []
        self.last_collided_pipeline = None

        self.hit_audio = pygame.mixer.Sound("./flappy-bird-assets/audio/hit.wav")
        self.wing_audio = pygame.mixer.Sound("./flappy-bird-assets/audio/wing.wav")

        self.message = pygame.sprite.RenderPlain(Message())
        self.gameover = pygame.sprite.RenderPlain(GameOver())
        self.score = pygame.sprite.RenderPlain(Score())

        self.add_floor(4)
        self.add_pipe(10)

        self.running = True

    def spawn_player(self):
        self.player = pygame.sprite.RenderPlain(Player())

    def add_pipe(self, quantity: int):
        for i in range(quantity):
            height = random.randint(-100, 100)

            if len(self.pipes) > 0:
                distance = self.pipes.sprites()[-1].rect.left + 300
            else:
                distance = pygame.display.get_window_size()[0]

            upper_pipe = Pipe(distance, backspace=height - 70)
            bottom_pipe = Pipe(distance, backspace=height, position="bottom")

            self.pipes.add(bottom_pipe, upper_pipe)

            self.pipelines.append(pygame.Rect(
                bottom_pipe.rect.left + bottom_pipe.rect.width * 2, 
                upper_pipe.rect.top + upper_pipe.rect.height, upper_pipe.rect.width / 4, upper_pipe.rect.height
            ))

    def add_floor(self, quantity: int):
        for i in range(quantity):
            floor = Floor()
            floor.rect.left = floor.rect.width * len(self.floor)
            self.floor.add(floor)

    def loop(self):
        self.events = pygame.event.get()

        jumping = False

        for e in self.events:
            if e.type == pygame.QUIT:
                self.running = False

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if not jumping and self.is_dead:
                        self.is_dead = False
                        self.is_gameover = False
                        self.spawn_player()
                    jumping = True
                    self.wing_audio.play()


        self.display.fill(Color.BLACK)
        self.clock.tick(self.fps)

        if len(self.pipes) < 6:
            self.add_pipe(2)

        if not self.is_dead and not self.is_gameover:
            self.player.update(is_jumping=jumping)
            self.pipes.update()

        self.floor.update()
        self.message.update()
        self.gameover.update()

        self.background.draw(self.display)

        if not self.is_dead and not self.is_gameover:
            self.pipes.draw(self.display)
            self.score.draw(self.display)

        # pygame.draw.rect(self.display, (255, 0, 0, 128), self.player.sprites()[0].rect)
        self.player.draw(self.display)
        self.floor.draw(self.display)
        
        if self.is_dead and not self.is_gameover:
            self.message.draw(self.display)
        if self.is_dead and self.is_gameover:
            self.gameover.draw(self.display)

        for line in self.pipelines:
            line.move_ip(-2, 0)

        collision_floor, collision_pipe = None, None

        if not self.is_dead and not self.is_gameover:
            collision_floor = pygame.sprite.spritecollideany(self.player.sprites()[0], self.floor)
            collision_pipe = pygame.sprite.spritecollideany(self.player.sprites()[0], self.pipes)
            collision_pipeline = self.player.sprites()[0].rect.collidelistall(self.pipelines)

            if collision_pipeline:
                if self.last_collided_pipeline != collision_pipeline[0]:
                    if self.score_value > 9:
                        self.score_value = 0
                    self.score_value += 1
                    self.score.update(score=self.score_value)
                    self.last_collided_pipeline = collision_pipeline[0]

        if not self.is_dead and collision_floor or collision_pipe:
            self.gameover.draw(self.display)
            self.hit_audio.play()
            self.is_dead = True
            self.is_gameover = True
            self.pipelines = []
            self.pipes = pygame.sprite.Group()
            self.player = pygame.sprite.RenderPlain()
            self.score_value = 0
            self.score.update(score=self.score_value)

            print("dead")


        pygame.display.flip()

    def start(self):
        while self.running:
            self.loop()


if __name__ == "__main__":
    game = Game((800, 640))
    game.start()