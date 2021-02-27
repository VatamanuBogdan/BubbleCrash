from pygame import Vector2
import random as rand
import pygame
import pygame.gfxdraw
import math


class Colors:
    colors = (
        (66, 135, 245),
        (245, 66, 135),
        (44, 230, 109),
        (255, 158, 74),
        (127, 3, 252)
    )


class Bubble:
    def __init__(self, pos, radius, color, surface, velocity):
        self.pos, self.velocity = pos, velocity
        self.radius, self.color = radius, color
        self.__surface = surface
        self.__born_time = pygame.time.get_ticks()
        self.__chain = []
        self.__deploy = False
        self.blocked = False

    def __bubbles_collision(self, bubbles):
        def collision(ball):
            return (self.pos - ball.pos).length() <= self.radius + ball.radius

        def line_equation():
            p1, p2 = self.pos, self.pos + self.velocity
            return 1 / (p2.x - p1.x), 1 / (p1.y - p2.y), p1.y / (p2.y - p1.y) - p1.x / (p2.x - p1.x)

        def collision_point(direction, bubble):
            a, b, c = direction
            pos = bubble.pos
            inter = Vector2(
                (b * (b * pos.x - a * pos.y) - a * c) / (a ** 2 + b ** 2),
                (a * (-b * pos.x + a * pos.y) - b * c) / (a ** 2 + b ** 2)
            )
            return inter - self.velocity.normalize() * math.sqrt(
                (self.radius + bubble.radius) ** 2 - (pos - inter).length() ** 2)

        direction = line_equation()
        position, collide = self.pos, False
        for bubble in bubbles:
            if bubble is not self and bubble.blocked and collision(bubble):
                point = collision_point(direction, bubble)
                if point.y > position.y:
                    position = point
                collide = True
        if collide:
            for bubble in bubbles:
                if bubble is not self and bubble.blocked and self.color == bubble.color\
                                                    and (position - bubble.pos).length() < 125:
                    self.__chain.append(bubble)
                    bubble.__chain.append(self)
            self.pos, self.__deploy, self.blocked = position, True, True

    def update_position(self, delta_time, bubbles):
        if not self.blocked:
            self.pos += delta_time * self.velocity
            if self.pos.y <= self.radius:
                self.pos.y = self.radius
                self.blocked = self.__deploy = True
            if self.pos.x <= 0 or self.pos.x >= 800:
                self.velocity.x *= -1
            self.pos.x = max(0, min(800, self.pos.x))
            self.__bubbles_collision(bubbles)

    def deploy(self):
        if not self.__deploy: return
        queue, destroy = [self], set()
        while queue:
            node = queue.pop(0)
            destroy.add(node)
            select = [bubble for bubble in node.__chain if bubble not in destroy]
            queue.extend(select)
        self.__deploy = False
        return None if len(destroy) < 4 else destroy

    def render(self):
        def render_particle(color):
            for bubble in self.__chain:
                mid = (self.pos + bubble.pos) / 2
                x, y = (rand.random() - 0.5) * 25 + mid[0], (rand.random() - 0.5) * 25 + mid[1]
                pygame.gfxdraw.filled_circle(self.__surface, int(x), int(y), 5, color)

        light = (math.sin((self.__born_time + pygame.time.get_ticks()) / 500) + 1) / 8 + 0.2
        color = self.color + (int(255 * light),)
        pygame.gfxdraw.aacircle(self.__surface, int(self.pos.x), int(self.pos.y), self.radius, color)
        pygame.gfxdraw.filled_circle(self.__surface, int(self.pos.x), int(self.pos.y), self.radius, color)
        render_particle(color)


class Cannon:
    sensitivity = 0.005

    def __init__(self, pos, color, surface):
        self.pos, self.color = pos, color
        self.surface, self.original_texture = surface, pygame.image.load('Resources/cannon.png')
        self.unit, self.angle = Vector2(0, -1), -math.pi / 2
        self.next_color = rand.choice(Colors.colors) + (100, )
        self.texture = self.original_texture
        self.original_ray = pygame.Surface((80, 1000)).convert_alpha()
        self.original_ray.fill(self.next_color[0:3] + (50, ))
        self.ray = self.original_ray

    def throw_bubble(self):
        bubble = Bubble(self.unit * 120 + self.pos, 50, self.next_color[0:3], self.surface, 100 * self.unit)
        self.next_color = rand.choice(Colors.colors)
        self.original_ray.fill(self.next_color + (50, ))
        self.next_color += (100, )
        return bubble

    def rotate(self, angle):
        self.angle = min(max(-math.pi + 0.25, angle), -0.25)
        self.unit = Vector2(math.cos(self.angle), math.sin(self.angle))
        self.texture = pygame.transform.rotozoom(self.original_texture, math.degrees(-self.angle - math.pi / 2), 1.0)
        self.ray = pygame.transform.rotozoom(self.original_ray, math.degrees(-self.angle - math.pi / 2), 1.0)

    def follow_mouse(self):
        self.rotate(self.angle + pygame.mouse.get_rel()[0] * self.sensitivity)

    def render(self):
        bubble_pos = self.unit * 120 + self.pos
        bubble_pos = (int(bubble_pos[0]), int(bubble_pos[1]))
        self.surface.blit(self.ray, self.ray.get_rect(center=self.pos))
        pygame.gfxdraw.aacircle(self.surface, bubble_pos[0], bubble_pos[1], 40, self.next_color)
        pygame.gfxdraw.filled_circle(self.surface, bubble_pos[0], bubble_pos[1], 40, self.next_color)
        self.surface.blit(self.texture, self.texture.get_rect(center=self.pos))
