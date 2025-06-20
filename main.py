import pygame
import sys
from games.flag_quiz import main_loop as flag_quiz_loop
from games.map_click_game import map_game_loop
from games.capitalCity_quiz import main_loop_capital, main_loop_country
from games.questions_game import opentdb_loop

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geography Game Menu")
clock = pygame.time.Clock()

BG_COLOR = (100, 120, 140)
BUTTON_COLOR = (45, 45, 48)
HOVER_COLOR = (70, 130, 180)
TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (249, 211, 66)

title_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
button_font = pygame.font.SysFont("Segoe UI", 32)

class Button:
    def __init__(self, rect, text, command):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.command = command
        self.hovered = False

    def draw(self, surface):
        color = HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, TITLE_COLOR, self.rect, 2, border_radius=10)
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.command()

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

def capital_quiz_menu():
    buttons = [
        Button((300, 250, 200, 60), "Guess Capital", lambda: main_loop_capital(screen, clock)),
        Button((300, 350, 200, 60), "Guess Country", lambda: main_loop_country(screen, clock))
    ]

    while True:
        screen.fill(BG_COLOR)
        title = title_font.render("Capital Quiz Mode", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update_hover(mouse_pos)
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        button.check_click(event.pos)

        pygame.display.flip()
        clock.tick(60)

def main_menu():
    buttons = [
        Button((300, 200, 200, 60), "Flag Quiz", lambda: flag_quiz_loop(screen, clock)),
        Button((300, 300, 200, 60), "Capital Quiz", capital_quiz_menu),
        Button((300, 400, 200, 60), "Map Quiz", lambda: map_game_loop(screen, clock)),
        Button((300, 500, 200, 60), "Quiz", lambda: opentdb_loop(screen, clock))
    ]

    while True:
        screen.fill(BG_COLOR)
        title = title_font.render("Choose a Game", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update_hover(mouse_pos)
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        button.check_click(event.pos)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()