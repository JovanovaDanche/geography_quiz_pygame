import pygame
import sys
import random
from label import Label, draw_wrapped_text, fontsize
from utils.api import get_country_data

buttons = pygame.sprite.Group()

class Button(pygame.sprite.Sprite):
    def __init__(self, screen, position, text, size, command=None):
        super().__init__()
        self.screen = screen
        self.text = text
        self.command = command
        self.font = pygame.font.SysFont("Arial", size)
        self.image = pygame.Surface((500, 45), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=position)
        self.default_color = (244, 244, 244)
        self.hover_color = (74, 144, 226)
        self.text_color = (249, 211, 66)
        self.hover_text_color = (255, 255, 255)
        self.corner_radius = 12
        buttons.add(self)

    def update(self):
        mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())
        bg_color = self.hover_color if mouse_over else self.default_color
        text_color = self.hover_text_color if mouse_over else self.text_color

        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, bg_color, self.image.get_rect(), border_radius=self.corner_radius)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

def generate_questions(mode="capital", level="easy"):
    all_data = get_country_data()
    valid_data = [c for c in all_data if c.get("capital") and c["capital"] != "N/A"]

    regions = {
        "easy": ["Europe", "North America"],
        "medium": ["Asia", "South America"],
        "hard": ["Africa", "Oceania"]
    }.get(level, [])

    filtered = [c for c in valid_data if c["region"] in regions]

    questions = []
    for country in random.sample(filtered, min(10, len(filtered))):
        if mode == "capital":
            question_text = f"What is the capital of {country['country']}?"
            correct_answer = country['capital']
            wrong_answers = random.sample(
                [c['capital'] for c in valid_data if c['capital'] != correct_answer], 3
            )
        else:
            question_text = f"Which country has the capital {country['capital']}?"
            correct_answer = country['country']
            wrong_answers = random.sample(
                [c['country'] for c in valid_data if c['country'] != correct_answer], 3
            )

        options = [correct_answer] + wrong_answers
        random.shuffle(options)

        questions.append({
            "question": question_text,
            "options": options,
            "correct": options.index(correct_answer)
        })

    return questions
def show_loading_screen(screen):
    screen.fill((255, 245, 180))
    font = pygame.font.SysFont("Arial", 48, bold=True)
    text_surface = font.render("Loading new game...", True, (74, 144, 226))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
def main_loop(screen, clock, mode="capital"):
    buttons.empty()
    TOTAL_TIME = 60
    questions = (
        generate_questions(mode, "easy") +
        generate_questions(mode, "medium") +
        generate_questions(mode, "hard")
    )

    qnum = 1
    points = 0
    question_answered = False
    score_label = Label(screen, "Score: 0", 50, 550, 30, color=(74, 144, 226))

    def kill_buttons():
        for btn in buttons:
            btn.kill()

    def check_score(answered="wrong"):
        nonlocal qnum, points, question_answered
        question_answered = True
        if answered == "right":
            points += 1
        if qnum < len(questions):
            qnum += 1
            score_label.change_text(f"Score: {points}")
            show_question(qnum)
            question_answered = False
            return None
        else:
            return show_end_screen(screen, points, len(questions))

    def on_right():
        return check_score("right")

    def on_false():
        return check_score("wrong")

    def show_question(qnum):
        kill_buttons()
        question = questions[qnum - 1]

        level_label = "Easy" if qnum <= 10 else "Medium" if qnum <= 20 else "Hard"
        question_text = f"[{level_label}] Question {qnum} of {len(questions)}: {question['question']}"

        y_positions = [200, 260, 320, 380]
        center_x = (800 - 500) // 2
        for i, option in enumerate(question["options"]):
            Button(
                screen,
                (center_x, y_positions[i]),
                option,
                30,
                command=on_right if i == question["correct"] else on_false
            )

        nonlocal current_question_text
        current_question_text = question_text

    current_question_text = ""
    show_question(qnum)
    start_ticks = pygame.time.get_ticks()

    retry_btn = Button(screen, (660, 10), "Retry", 24, command=lambda: "retry")
    exit_btn = Button(screen, (660, 60), "Exit", 24, command=lambda: "menu")

    retry_btn.image = pygame.Surface((120, 40), pygame.SRCALPHA)
    retry_btn.rect = retry_btn.image.get_rect(topleft=(660, 10))
    exit_btn.image = pygame.Surface((120, 40), pygame.SRCALPHA)
    exit_btn.rect = exit_btn.image.get_rect(topleft=(660, 60))

    running = True
    while running:
        screen.fill((255, 245, 180))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_btn.rect.collidepoint(event.pos):
                    show_loading_screen(screen)
                    return main_loop(screen, clock, mode)
                elif exit_btn.rect.collidepoint(event.pos):
                    return "menu"
                else:
                    for btn in buttons:
                        if btn.rect.collidepoint(event.pos) and btn.command:
                            if not question_answered:
                                result = btn.command()
                                if result == "retry":
                                    show_loading_screen(screen)
                                    return main_loop(screen, clock, mode)
                                elif result == "menu":
                                    return "menu"
                                elif result == "new_game":
                                    return main_loop(screen, clock, mode)

        elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000
        remaining_time = max(0, TOTAL_TIME - elapsed_time)

        timer_label = Label(screen, f"Time Left: {remaining_time}s", 500, 550, 30, color=(74, 144, 226))
        timer_label.draw()
        score_label.draw()
        draw_wrapped_text(screen, current_question_text, 0, 110, fontsize(28), (0, 0, 255), 700, center=True)

        retry_btn.update()
        exit_btn.update()
        buttons.update()

        buttons.draw(screen)
        screen.blit(retry_btn.image, retry_btn.rect)
        screen.blit(exit_btn.image, exit_btn.rect)

        if remaining_time <= 0:
            result = show_end_screen(screen, points, len(questions))
            if result == "new_game":
                return main_loop(screen, clock, mode)
            return

        pygame.display.flip()
        clock.tick(60)

def show_end_screen(screen, score, total):
    buttons.empty()
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_small = pygame.font.SysFont("Arial", 40)

    message = "YOU WIN!" if score >= total * 0.9 else "YOU LOSE!"
    color = (0, 255, 0) if message == "YOU WIN!" else (255, 0, 0)

    msg_surface = font_big.render(message, True, color)
    score_surface = font_small.render(f"Final Score: {score} / {total}", True, (255, 255, 255))

    msg_rect = msg_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    score_rect = score_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))

    button_x = (screen.get_width() - 500) // 2
    button_y = screen.get_height() // 2 + 60

    def on_new_game():
        return "new_game"

    new_game_btn = Button(screen, (button_x, button_y), "New Game", 36, command=on_new_game)

    while True:
        screen.blit(overlay, (0, 0))
        screen.blit(msg_surface, msg_rect)
        screen.blit(score_surface, score_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_game_btn.rect.collidepoint(event.pos):
                    return "new_game"

        new_game_btn.update()
        buttons.draw(screen)
        pygame.display.flip()

def main_loop_capital(screen, clock):
    return main_loop(screen, clock, mode="capital")

def main_loop_country(screen, clock):
    return main_loop(screen, clock, mode="country")