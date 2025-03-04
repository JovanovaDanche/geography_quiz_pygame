import pygame
import pygame.gfxdraw
import sys
import time
import random
import psycopg2  # For PostgreSQL
from label import *

pygame.init()
pygame.mixer.init()
hit = pygame.mixer.Sound("sounds/hit.wav")
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

buttons = pygame.sprite.Group()


class Button(pygame.sprite.Sprite):
    ''' A button treated like a Sprite... and killed too '''

    def __init__(self, position, text, size,
                 colors="white on blue",
                 hover_colors="red on green",
                 style="button1",
                 borderc=(255, 255, 255),
                 command=lambda: print("No command activated for this button")):

        super().__init__()
        self.text = text
        self.command = command
        self.colors = colors
        self.original_colors = colors
        self.fg, self.bg = self.colors.split(" on ")
        if hover_colors == "red on green":
            self.hover_colors = f"{self.bg} on {self.fg}"
        else:
            self.hover_colors = hover_colors
        self.style = style
        self.borderc = borderc
        self.font = pygame.font.SysFont("Arial", size)
        self.render(self.text)
        self.x, self.y, self.w, self.h = self.text_render.get_rect()
        self.x, self.y = position
        self.rect = pygame.Rect(self.x, self.y, 500, self.h)
        self.position = position
        self.pressed = 1
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
        if self.command:
            self.hover()
            self.click()

    def draw_button1(self):
        lcolor = (150, 150, 150)
        lcolor2 = (50, 50, 50)
        pygame.draw.line(screen, lcolor, self.position,
                         (self.x + self.w, self.y), 5)
        pygame.draw.line(screen, lcolor, (self.x, self.y - 2),
                         (self.x, self.y + self.h), 5)
        pygame.draw.line(screen, lcolor2, (self.x, self.y + self.h),
                         (self.x + self.w, self.y + self.h), 5)
        pygame.draw.line(screen, lcolor2, (self.x + self.w, self.y + self.h),
                         [self.x + self.w, self.y], 5)
        pygame.draw.rect(screen, self.bg, self.rect)

    def draw_button2(self):
        pygame.draw.rect(screen, self.bg, (self.x - 50, self.y, 500, self.h))
        pygame.gfxdraw.rectangle(screen, (self.x - 50, self.y, 500, self.h), self.borderc)

    def check_collision(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.colors = self.hover_colors
        else:
            self.colors = self.original_colors

    def hover(self):
        self.check_collision()

    def click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] and self.pressed == 1:
                print("The answer is:'" + self.text + "'")
                self.command()
                self.pressed = 0
            if pygame.mouse.get_pressed() == (0, 0, 0):
                self.pressed = 1


# Database function to load questions from PostgreSQL
def load_questions_from_db():
    conn = psycopg2.connect(
        dbname="test",
        user="postgres",
        password="finki123",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer1, answer2, answer3, answer4, correct_answer FROM quiz_questions")

    questions = []
    for row in cursor.fetchall():
        question_text = row[0]
        answers = [row[1], row[2], row[3], row[4]]
        correct_answer = row[5]
        questions.append((question_text, answers, correct_answer))

    conn.close()
    return questions


questions = load_questions_from_db()


def on_click():
    print("Click on one answer")


def check_score(selected_answer, correct_answer):
    global qnum, points
    hit.play()
    if selected_answer == correct_answer:
        points += 1
    qnum += 1
    score.change_text(str(points))
    if qnum <= len(questions):
        title.change_text(questions[qnum - 1][0], color="cyan")
        num_question.change_text(str(qnum))
        show_question(qnum)
    else:
        score.change_text("You reached a score of " + str(points))
    time.sleep(0.5)


def show_question(qnum):
    kill()
    pos = [100, 150, 200, 250]
    random.shuffle(pos)
    question_text, answers, correct_answer = questions[qnum - 1]

    Button((10, pos[0]), answers[0], 36, "red on yellow",
           hover_colors="blue on orange", style="button2", borderc=(255, 255, 0),
           command=lambda: check_score(answers[0], correct_answer))
    Button((10, pos[1]), answers[1], 36, "red on yellow",
           hover_colors="blue on orange", style="button2", borderc=(255, 255, 0),
           command=lambda: check_score(answers[1], correct_answer))
    Button((10, pos[2]), answers[2], 36, "red on yellow",
           hover_colors="blue on orange", style="button2", borderc=(255, 255, 0),
           command=lambda: check_score(answers[2], correct_answer))
    Button((10, pos[3]), answers[3], 36, "red on yellow",
           hover_colors="blue on orange", style="button2", borderc=(255, 255, 0),
           command=lambda: check_score(answers[3], correct_answer))


def kill():
    for _ in buttons:
        _.kill()


qnum = 1
points = 0
num_question = Label(screen, str(qnum), 0, 0)
score = Label(screen, "Score", 50, 300)
title = Label(screen, questions[qnum - 1][0], 10, 10, 55, color="cyan")
write1 = Label(screen, "PYQUIZ", 50, 350, 20, color="red")


def loop():
    show_question(qnum)
    while True:
        screen.fill(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        buttons.update()
        buttons.draw(screen)
        show_labels()
        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    loop()
