from src.Entites import *
from src.UserInterface import *
import random as rand
import pygame
import os


class ThrowBubbleState:
    def __init__(self, owner, cannon, bubbles):
        self.__owner = owner
        self.__cannon, self.__bubbles = cannon, bubbles
        self.counter = None

    def prepare(self, **kwargs):
        self.counter = 4

    def __cannon_update(self, delta_time):
        self.__cannon.follow_mouse()

        if game_instance.mouse_button_click(1):
            self.counter -= 1
            self.__bubbles.add(self.__cannon.throw_bubble())

    def __bubbles_update(self, delta_time):
        spark = set()
        for bubble in self.__bubbles:
            bubble.update_position(delta_time, self.__bubbles)
        for bubble in self.__bubbles:
            res = bubble.deploy()
            if res: spark.update(res)
        return spark if len(spark) > 0 else None

    def update(self, delta_time):
        self.__cannon_update(delta_time)
        res = self.__bubbles_update(delta_time)
        if res:
            self.__owner.scene(Universe.StateEnum.SPARK_BUBBLE, spark=res)
        elif self.counter <= 0:
            self.__owner.scene(Universe.StateEnum.RANDOM_SHOOT)


class SparkBubbleState:
    TimeLimit = 2

    def __init__(self, owner, cannon, bubbles):
        self.__owner = owner
        self.__cannon, self.__bubbles = cannon, bubbles
        self.spark, self.time = None, None

    def prepare(self, **kwargs):
        self.spark = kwargs['spark']
        self.time = 0

    def __cannon_update(self, delta_time):
        self.__cannon.follow_mouse()

    def __bubbles_update(self, delta_time):
        for bubble in self.__bubbles:
            bubble.update_position(delta_time, self.__bubbles)

    def __spark_bubbles_update(self, delta_time):
        self.time += delta_time
        if self.time > self.TimeLimit:
            self.__bubbles.remove(self.spark.pop())
            self.__owner.score += 50
            self.time = 0
        if len(self.spark) <= 0:
            self.__owner.scene(Universe.StateEnum.THROW_BUBBLE)

    def update(self, delta_time):
        self.__cannon_update(delta_time)
        self.__bubbles_update(delta_time)
        self.__spark_bubbles_update(delta_time)


class RandomShotState:
    TimeLimit = 5
    Speed = 0.1

    def __init__(self, owner, cannon, bubbles):
        self.__owner = owner
        self.__cannon, self.__bubbles = cannon, bubbles
        self.__angle = None
        self.__counter = self.distance = None

    def prepare(self, **kwargs):
        self.__angle = self.__cannon.angle
        self.distance = rand.uniform(-2.89, -0.25) - self.__angle
        self.__counter = 3

    def __cannon_update(self, delta_time):
        throw = False
        delta_angle = delta_time * self.Speed
        if self.distance < 0:
            self.distance += delta_angle
            self.__angle -= delta_angle
            if self.distance >= 0:
                self.__angle += self.distance
                throw = True
        else:
            self.distance -= delta_angle
            self.__angle += delta_angle
            if self.distance <= 0:
                self.__angle -= self.distance
                throw = True
        self.__cannon.rotate(self.__angle)
        if throw:
            self.__bubbles.add(self.__cannon.throw_bubble())
            self.__counter -= 1
            self.distance = rand.uniform(-2.89, -0.25) - self.__angle

    def __bubbles_update(self, delta_time):
        for bubble in self.__bubbles:
            bubble.update_position(delta_time, self.__bubbles)

    def update(self, delta_time):
        if self.__counter <= 0:
            self.__owner.scene(Universe.StateEnum.THROW_BUBBLE)
            return
        self.__cannon_update(delta_time)
        self.__bubbles_update(delta_time)


class Universe:
    class StateEnum:
        THROW_BUBBLE = 1
        SPARK_BUBBLE = 2
        RANDOM_SHOOT = 3

    def __init__(self, window):
        self.__window = window
        self.__cannon = Cannon((400, 1000), (0, 255, 0), window)
        self.__bubbles = set()
        self.__throw_state = ThrowBubbleState(self, self.__cannon, self.__bubbles)
        self.__spark_state = SparkBubbleState(self, self.__cannon, self.__bubbles)
        self.__random_state = RandomShotState(self, self.__cannon, self.__bubbles)
        self.__scene = None
        self.__background = pygame.image.load('Resources/background.png')
        self.__user_interface = UserInterface(window)
        self.limit_line = 800
        self.score = 0
        self.scene(Universe.StateEnum.THROW_BUBBLE)

    def scene(self, type, **kwargs):
        if type == self.StateEnum.THROW_BUBBLE:
            self.__scene = self.__throw_state
            self.__scene.prepare(**kwargs)
        elif type == self.StateEnum.SPARK_BUBBLE:
            self.__scene = self.__spark_state
            self.__scene.prepare(**kwargs)
        elif type == self.StateEnum.RANDOM_SHOOT:
            self.__scene = self.__random_state
            self.__scene.prepare(**kwargs)
        else:
            raise ValueError

    def update(self, delta_time):
        self.__scene.update(delta_time)
        self.__user_interface.score = self.score
        self.__user_interface.limit_line = self.limit_line
        self.__user_interface.random_val = self.__throw_state.counter
        for bubble in self.__bubbles:
            if bubble.blocked and bubble.pos[1] + bubble.radius > self.limit_line:
                return False
        return True

    def render(self):
        self.__window.fill((84, 50, 219))
        self.__window.blit(self.__background, (0, 0))
        self.__cannon.render()
        for bubble in self.__bubbles: bubble.render()
        self.__user_interface.render()
        pygame.display.update()


class BubbleCrash:
    def __init__(self, width, height):
        pygame.init()
        display_info = pygame.display.Info()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (display_info.current_w // 2, display_info.current_h // 2)
        self.__window = pygame.display.set_mode((width, height), pygame.SRCALPHA, 32)
        pygame.display.set_icon(pygame.image.load('Resources/window_icon.png'))
        pygame.display.set_caption('Bubble Crash')
        pygame.mixer_music.load('Resources/soundtrack.wav')
        pygame.mouse.set_visible(False)
        self.width, self.height = width, height
        self.__run = True
        self.__mouse_buttons = [False] * 4
        self.__universe = Universe(self.__window)

    def mouse_button_click(self, button):
        return self.__mouse_buttons[button]

    def __input_handling(self):
        self.__mouse_buttons = [False] * 4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.__run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.__mouse_buttons[event.button] = True

    def run(self):
        last_time = pygame.time.get_ticks()
        pygame.mixer_music.play(-1)
        while self.__run:
            time = pygame.time.get_ticks()
            delta_time = (time - last_time) / 100
            self.__input_handling()
            if not self.__universe.update(delta_time):
                self.__run = False
            self.__universe.render()
            last_time = time


game_instance = BubbleCrash(800, 1000)
