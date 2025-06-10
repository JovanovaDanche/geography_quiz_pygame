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
    def __init__(self, screen, position, text, size,
                 colors="white on blue",
                 hover_colors="red on green",
                 style="button1",
                 borderc=(255, 255, 255),
                 command=None):
        super().__init__()
        self.screen = screen
        self.text = text
        self.command = command
        self.colors = colors
        self.original_colors = colors
        self.fg, self.bg = self.colors.split(" on ")
        self.hover_colors = f"{self.bg} on {self.fg}" if hover_colors == "red on green" else hover_colors
        self.style = style
        self.borderc = borderc
        self.font = pygame.font.SysFont("Arial", size)
        self.render(self.text)
        self.x, self.y, self.w, self.h = self.text_render.get_rect()
        self.x, self.y = position
        self.rect = pygame.Rect(self.x, self.y, 500, self.h)
        self.position = position
        buttons.add(self)

    def render(self, text):
        self.text_render = self.font.render(text, 1, self.fg)
        self.image = self.text_render

    def update(self):
        self.fg, self.bg = self.colors.split(" on ")
        if self.style == "button1":
            pygame.draw.rect(self.screen, self.bg, self.rect)
        elif self.style == "button2":
            pygame.draw.rect(self.screen, self.bg, (self.x - 50, self.y, 500, self.h))
            pygame.draw.rect(self.screen, self.borderc, (self.x - 50, self.y, 500, self.h), 2)
        self.hover()

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.colors = self.hover_colors
        else:
            self.colors = self.original_colors


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
        question_text = "Whose flag is this?"
        correct_answer = country["country"]
        wrong_answers = sample(
            [c["country"] for c in filtered if c["country"] != correct_answer],
            min(3, len(filtered) - 1)
        )
        options = [correct_answer] + wrong_answers
        shuffle(options)

        questions.append({
            "image": country["flag"],
            "question": question_text,
            "options": options,
            "correct": options.index(correct_answer)
        })

    return questions
def main_loop(screen, clock):
    global buttons, current_flag_image
    buttons.empty()
    current_flag_image = None

    flag_questions = (
            generate_flag_questions("easy") +
            generate_flag_questions("medium") +
            generate_flag_questions("hard")
    )

    qnum = 1
    points = 0
    score = Label(screen, "Score: 0", 50, 550)
    title = Label(screen, "Flag Quiz", 50, 30, 40, color="blue")

    def kill_buttons():
        for btn in buttons:
            btn.kill()

    def check_score(answered="wrong"):
        nonlocal qnum, points
        if answered == "right":
            points += 1

        if qnum < len(flag_questions):
            qnum += 1
            score.change_text(f"Score: {points}")
            show_flag_question(qnum)
        else:
            score.change_text(f"Game Over! Final Score: {points}")
            pygame.time.delay(2000)
            return False
        return True

    def on_right():
        check_score("right")

    def on_false():
        check_score("wrong")

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

        title.change_text(f"[{level_label}] Question {qnum} of {len(flag_questions)}: {question['question']}",
                          color="blue")

        y_positions = [350, 400, 450, 500]
        for i, option in enumerate(question["options"]):
            Label(screen, f"{i + 1}.", 50, y_positions[i], 36, color="yellow").draw()
            is_correct = (i == question["correct"])
            Button(
                screen,
                (100, y_positions[i]),
                option,
                36,
                "red on yellow",
                hover_colors="blue on orange",
                style="button2",
                borderc=(255, 255, 0),
                command=on_right if is_correct else on_false
            )

    show_flag_question(qnum)

    running = True
    while running:
        screen.fill((0, 0, 0))

        if current_flag_image:
            screen.blit(current_flag_image, (250, 100))
        else:
            Label(screen, "Flag image not available", 300, 150, 20, color="red").draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # Return to main menu
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn.rect.collidepoint(event.pos) and btn.command:
                        running = check_score("right" if btn.command == on_right else "wrong")

        title.draw()
        score.draw()
        buttons.update()
        buttons.draw(screen)

        pygame.display.flip()
        clock.tick(60)
