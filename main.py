import pygame
import sys
from games.flag_quiz import main_loop as flag_quiz_loop
from games.capitalCity_quiz import main_loop as capital_quiz_loop

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geography Game Menu")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 40)

# Buttons
button_flag = pygame.Rect(300, 200, 200, 60)
button_capital = pygame.Rect(300, 300, 200, 60)

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Choose a Game", font, BLACK, screen, 400, 100)

        pygame.draw.rect(screen, GRAY, button_flag)
        draw_text("Flag Quiz", font, BLACK, screen, button_flag.centerx, button_flag.centery)

        pygame.draw.rect(screen, GRAY, button_capital)
        draw_text("Capital Quiz", font, BLACK, screen, button_capital.centerx, button_capital.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_flag.collidepoint(event.pos):
                    flag_quiz_loop(screen, clock)
                elif button_capital.collidepoint(event.pos):
                    capital_quiz_loop(screen, clock)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
