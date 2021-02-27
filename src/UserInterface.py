import pygame


class UserInterface:
    def __init__(self, surf):
        self.__surf = surf
        self.__font = pygame.font.Font('Resources/font.ttf', 48)
        # score text
        self.__score_title = self.__font.render('Score: ', True, (44, 230, 109))
        self.__score_title_rect = self.__score_title.get_rect()
        self.__score_title_rect.top, self.__score_title_rect.left = 940, 20
        # score value
        self.__score = None
        self.__score_value = None
        self.__score_value_rect = None
        self.score = 0
        # limit bubbles line
        self.__limit_line_y = 0
        self.__limit_line = pygame.Surface((self.__surf.get_rect().size[0], 2)).convert_alpha(self.__surf)
        self.__limit_line_rect = None
        # bubbles to random
        self.__random_bar_val = None
        self.__bubbles_to_random = None
        self.__bubbles_to_random_rect = None
        self.random_val = 0

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        self.__score = value
        self.__score_value = self.__font.render(str(self.__score), True, (66, 135, 245))
        self.__score_value_rect = self.__score_value.get_rect()
        w1, w2 = self.__score_title_rect.size[0], self.__score_value_rect.size[0]
        x_pos, y_pos = self.__score_title_rect.center
        self.__score_value_rect.center = x_pos + (w1 + w2) // 2, y_pos

    @property
    def limit_line(self):
        return self.__limit_line_y

    @limit_line.setter
    def limit_line(self, value):
        self.__limit_line_y = value
        self.__limit_line_rect = self.__limit_line.get_rect()
        self.__limit_line_rect.center = (self.__surf.get_rect().size[0] // 2, 800)
        self.__limit_line.fill((44, 230, 109, 70))

    @property
    def random_val(self):
        return self.__random_bar_val

    @random_val.setter
    def random_val(self, value):
        self.__random_bar_val = value
        self.__bubbles_to_random = self.__font.render('O ' * self.__random_bar_val, True, (66, 135, 245))
        self.__bubbles_to_random_rect = self.__bubbles_to_random.get_rect()
        self.__bubbles_to_random_rect.top = 940
        self.__bubbles_to_random_rect.right = 700

    def render(self):
        self.__surf.blit(self.__score_title, self.__score_title_rect)
        self.__surf.blit(self.__score_value, self.__score_value_rect)
        self.__surf.blit(self.__limit_line, self.__limit_line_rect)
        self.__surf.blit(self.__bubbles_to_random, self.__bubbles_to_random_rect)

