import pygame
import pygame.gfxdraw
import sys
import time
import random
import requests
from io import BytesIO
from label import *
from random import sample, shuffle
from utils.api import get_country_data

# Initialize pygame
pygame.init()
pygame.mixer.init()
#hit = pygame.mixer.Sound("../sounds/hit.wav")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

buttons = pygame.sprite.Group()
current_flag_image = None  # NEW: to keep flag visible

class Button(pygame.sprite.Sprite):
    def __init__(self, position, text, size,
                 colors="white on blue",
                 hover_colors="red on green",
                 style="button1",
                 borderc=(255, 255, 255),
                 command=None):
        super().__init__()
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
            self.draw_button1()
        elif self.style == "button2":
            self.draw_button2()
        self.hover()

    def draw_button1(self):
        pygame.draw.line(screen, (150, 150, 150), self.position, (self.x + self.w, self.y), 5)
        pygame.draw.line(screen, (150, 150, 150), (self.x, self.y - 2), (self.x, self.y + self.h), 5)
        pygame.draw.line(screen, (50, 50, 50), (self.x, self.y + self.h), (self.x + self.w, self.y + self.h), 5)
        pygame.draw.line(screen, (50, 50, 50), (self.x + self.w, self.y + self.h), [self.x + self.w, self.y], 5)
        pygame.draw.rect(screen, self.bg, self.rect)

    def draw_button2(self):
        pygame.draw.rect(screen, self.bg, (self.x - 50, self.y, 500, self.h))
        pygame.gfxdraw.rectangle(screen, (self.x - 50, self.y, 500, self.h), self.borderc)

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


def generate_flag_questions():
    all_data = get_country_data()
    questions = []
    valid_data = [c for c in all_data if c.get("flag") and c.get("country")]

    for country in sample(valid_data, 10):

        question_text = "Whose flag is this?"
        correct_answer = country["country"]
        wrong_answers = sample([
            c["country"] for c in valid_data
            if c["country"] != correct_answer
        ], 3)

        options = [correct_answer] + wrong_answers
        shuffle(options)

        questions.append({
            "image": country["flag"],
            "question": question_text,
            "options": options,
            "correct": options.index(correct_answer)
        })

    return questions


def on_right():
    check_score("right")


def on_false():
    check_score("wrong")


def show_flag_question(qnum):
    global current_flag_image
    kill()
    question = flag_questions[qnum - 1]

    # Load and save flag image to draw every frame
    flag_img = load_flag_image(question["image"])
    if flag_img:
        current_flag_image = pygame.transform.scale(flag_img, (300, 200))
    else:
        current_flag_image = None

    # Display question text
    title.change_text(f"Question {qnum} of {len(flag_questions)}: {question['question']}", color="blue")

    # Display answer options
    y_positions = [350, 400, 450, 500]

    for i, option in enumerate(question["options"]):
        # Number label (not interactive)
        Label(screen, f"{i + 1}.", 50, y_positions[i], 36, color="yellow").draw()

        # Actual answer (interactive)
        is_correct = (i == question["correct"])
        Button(
            (100, y_positions[i]),
            option,
            36,
            "red on yellow",
            hover_colors="blue on orange",
            style="button2",
            borderc=(255, 255, 0),
            command=on_right if is_correct else on_false
        )


def check_score(answered="wrong"):
    global qnum, points
    #hit.play()

    if answered == "right":
        points += 1

    if qnum < len(flag_questions):
        qnum += 1
        score.change_text(f"Score: {points}")
        show_flag_question(qnum)
    else:
        score.change_text(f"Game Over! Final Score: {points}")
        time.sleep(2)


def kill():
    for btn in buttons:
        btn.kill()


# Initialize game
flag_questions = generate_flag_questions()
qnum = 1
points = 0
score = Label(screen, "Score: 0", 50, 550)
title = Label(screen, "Flag Quiz", 300, 30, 40, color="blue")


def main_loop():
    show_flag_question(qnum)

    while True:
        screen.fill((0, 0, 0))  # Black background

        if current_flag_image:
            screen.blit(current_flag_image, (250, 100))
        else:
            error = Label(screen, "Flag image not available", 300, 150, 20, color="red")
            error.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn.rect.collidepoint(event.pos) and btn.command:
                        btn.command()

        title.draw()
        score.draw()
        buttons.update()
        buttons.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main_loop()
