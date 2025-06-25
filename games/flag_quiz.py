import pygame
import sys
import time
import random
import requests
from io import BytesIO
from label import Label
from random import sample, shuffle
from utils.api import get_country_data

buttons = pygame.sprite.Group()
current_flag_image = None

class Button(pygame.sprite.Sprite):
    def __init__(self, screen, position, text, size, command=None):
        super().__init__()
        self.screen = screen
        self.text = text
        self.command = command
        self.font = pygame.font.SysFont("Arial", size)
        self.image = pygame.Surface((600, 45), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=position)
        self.default_color = (244, 244, 244)
        self.hover_color = (74, 144, 226)
        self.text_color = (249, 211, 66)
        self.hover_text_color = (255, 255, 255)
        self.corner_radius = 10
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

def show_loading_screen(screen):
    screen.fill((255, 245, 180))
    font = pygame.font.SysFont("Arial", 48, bold=True)
    text_surface = font.render("Loading new game...", True, (74, 144, 226))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def load_flag_image(url):
    try:
        response = requests.get(url)
        img_data = BytesIO(response.content)
        return pygame.image.load(img_data)
    except Exception as e:
        print(f"Error loading flag image: {e}")
        return None

def generate_flag_questions(level="easy"):
    all_data = get_country_data()
    valid_data = [c for c in all_data if c.get("flag") and c.get("country") and c.get("region")]

    if level == "easy":
        regions = ["Europe", "North America"]
    elif level == "medium":
        regions = ["Asia", "South America"]
    elif level == "hard":
        regions = ["Africa", "Oceania"]
    else:
        regions = []

    filtered = [c for c in valid_data if c["region"] in regions]

    questions = []
    for country in sample(filtered, min(10, len(filtered))):
        question_text = "Which country's flag is this?"
        correct_answer = country["country"]
        wrong_answers = sample([c["country"] for c in filtered if c["country"] != correct_answer], min(3, len(filtered) - 1))
        options = [correct_answer] + wrong_answers
        shuffle(options)

        questions.append({
            "image": country["flag"],
            "question": question_text,
            "options": options,
            "correct": options.index(correct_answer)
        })

    return questions

def show_end_screen(screen, score, total):
    buttons.empty()
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_small = pygame.font.SysFont("Arial", 40)

    if score >= total * 0.9:
        message = "YOU WIN!"
        color = (0, 255, 0)
    else:
        message = "YOU LOSE!"
        color = (255, 0, 0)

    msg_surface = font_big.render(message, True, color)
    score_surface = font_small.render(f"Final Score: {score} / {total}", True, (255, 255, 255))

    msg_rect = msg_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    score_rect = score_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))

    button_x = (screen.get_width() - 600) // 2
    button_y = screen.get_height() // 2 + 60

    def on_new_game():
        return "new_game"

    new_game_btn = Button(screen, (button_x, button_y), "New Game", 36, command=on_new_game)

    running = True
    while running:
        screen.blit(overlay, (0, 0))
        screen.blit(msg_surface, msg_rect)
        screen.blit(score_surface, score_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_game_btn.rect.collidepoint(event.pos):
                    running = False

        new_game_btn.update()
        buttons.draw(screen)
        pygame.display.flip()

def main_loop(screen, clock):
    global buttons, current_flag_image
    while True:
        buttons.empty()
        current_flag_image = None
        TOTAL_TIME = 60

        flag_questions = (
            generate_flag_questions("easy") +
            generate_flag_questions("medium") +
            generate_flag_questions("hard")
        )

        qnum = 1
        points = 0

        def kill_buttons():
            for btn in buttons:
                btn.kill()

        def check_score(answered="wrong"):
            nonlocal qnum, points, running
            if answered == "right":
                points += 1
            if qnum < len(flag_questions):
                qnum += 1
                show_flag_question(qnum)
                return True
            else:
                result = show_end_screen(screen, points, len(flag_questions))
                if result == "new_game":
                    return "new_game"
                return "menu"

        def on_right():
            return check_score("right")

        def on_false():
            return check_score("wrong")

        def show_flag_question(qnum):
            global current_flag_image
            kill_buttons()
            question = flag_questions[qnum - 1]

            if qnum <= 10:
                level_label = "Easy"
            elif qnum <= 20:
                level_label = "Medium"
            else:
                level_label = "Hard"

            flag_img = load_flag_image(question["image"])
            if flag_img:
                current_flag_image = pygame.transform.scale(flag_img, (300, 200))
            else:
                current_flag_image = None

            subtitle.change_text(question["question"])
            level_title.change_text(f"Level {level_label} : Question {qnum} of {len(flag_questions)}")

            y_base = 380
            for i, option in enumerate(question["options"]):
                Button(screen, (100, y_base + i * 55), option, 28,
                       command=on_right if i == question["correct"] else on_false)

        timer = Label(screen, "Time: 60s", 50, 20, 28, color=(74, 144, 226))
        score = Label(screen, "Score: 0", 650, 20, 28, color=(74, 144, 226))
        level_title = Label(screen, "", 400, 80, 30, color="dodgerblue", center=True)
        subtitle = Label(screen, "Which country's flag is this?", 400, 120, 35, color=(204, 196, 144), center=True)

        show_flag_question(qnum)
        start_ticks = pygame.time.get_ticks()

        retry_btn = Button(screen, (660, 10), "Retry", 24, command=lambda: "retry")
        exit_btn = Button(screen, (660, 60), "Exit", 24, command=lambda: "menu")

        retry_btn.image = pygame.Surface((120, 40), pygame.SRCALPHA)
        retry_btn.rect = retry_btn.image.get_rect(topleft=(660, 70))
        exit_btn.image = pygame.Surface((120, 40), pygame.SRCALPHA)
        exit_btn.rect = exit_btn.image.get_rect(topleft=(660, 120))

        running = True
        while running:
            screen.fill((255, 245, 180))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if retry_btn.rect.collidepoint(event.pos):
                        show_loading_screen(screen)
                        return main_loop(screen, clock)
                    elif exit_btn.rect.collidepoint(event.pos):
                        return "menu"
                    for btn in buttons:
                        if btn.rect.collidepoint(event.pos) and btn.command:
                            result = btn.command()
                            if result == "retry":
                                show_loading_screen(screen)
                                return main_loop(screen, clock)
                            elif result == "menu" or result == "new_game":
                                return "menu"

            elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000
            remaining_time = max(0, TOTAL_TIME - elapsed_time)
            timer.change_text(f"Time: {remaining_time}s")
            score.change_text(f"Score: {points}")

            timer.draw()
            score.draw()
            level_title.draw()
            subtitle.draw()

            if current_flag_image:
                screen.blit(current_flag_image, (250, 160))

            buttons.update()
            buttons.draw(screen)

            screen.blit(retry_btn.image, retry_btn.rect)
            screen.blit(exit_btn.image, exit_btn.rect)

            pygame.display.flip()
            clock.tick(60)

            if remaining_time <= 0:
                outcome = show_end_screen(screen, points, len(flag_questions))
                if outcome == "new_game":
                    return "menu"
                return
