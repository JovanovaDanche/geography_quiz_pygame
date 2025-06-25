import pygame
import sys
import requests
import random
import html
import threading
import time
from label import Label, draw_wrapped_text
from pygame.sprite import Group

buttons = Group()

class Button(pygame.sprite.Sprite):
    def __init__(self, screen, position, text, size, command=None, width=600, height=45):
        super().__init__()
        self.screen = screen
        self.text = text
        self.command = command
        self.font = pygame.font.SysFont("Arial", size)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
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

def show_end_screen(screen, score, total):
    buttons.empty()
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_small = pygame.font.SysFont("Arial", 40)

    message = "YOU WIN!" if score >= total * 0.9 else "YOU LOSE!"
    color = (0, 255, 0) if "WIN" in message else (255, 0, 0)

    msg_surface = font_big.render(message, True, color)
    score_surface = font_small.render(f"Final Score: {score} / {total}", True, (255, 255, 255))

    msg_rect = msg_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    score_rect = score_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))

    def on_new_game():
        return "retry"

    new_game_btn = Button(screen, ((screen.get_width() - 600) // 2, screen.get_height() // 2 + 60), "New Game", 36, command=on_new_game)

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
                    return "retry"

        new_game_btn.update()
        buttons.draw(screen)
        pygame.display.flip()

def opentdb_loop(screen, clock):


    def fetch_questions(level):
        url = f"https://opentdb.com/api.php?amount=10&category=22&difficulty={level}&type=multiple"
        questions = []
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get('results', [])
            for item in data:
                q = html.unescape(item["question"])
                correct = html.unescape(item["correct_answer"])
                opts = [html.unescape(a) for a in item["incorrect_answers"]] + [correct]
                random.shuffle(opts)
                questions.append({
                    "question": q,
                    "options": opts,
                    "correct": opts.index(correct),
                    "difficulty": level.capitalize()
                })
        except Exception as e:
            print(f"Error fetching {level} questions: {e}")
        return questions

    easy_qs = fetch_questions("easy")
    medium_qs = []
    hard_qs = []

    def fetch_medium():
        time.sleep(10)
        nonlocal medium_qs
        medium_qs = fetch_questions("medium")

    def fetch_hard():
        time.sleep(5)
        nonlocal hard_qs
        hard_qs = fetch_questions("hard")

    t1 = threading.Thread(target=fetch_medium)
    t2 = threading.Thread(target=fetch_hard)
    t1.start()
    t2.start()

    questions = easy_qs
    qidx = 0
    points = 0

    timer = Label(screen, "Time: 60s", 50, 20, 28, color=(74, 144, 226))
    score_label = Label(screen, "Score: 0", 650, 20, 28, color=(74, 144, 226))
    title = Label(screen, "", 400, 150, 30, color="dodgerblue", center=True)
    subtitle = Label(screen, "Get Ready!", 400, 200, 32, color=(204, 196, 144), center=True)


    def kill_buttons():
        for b in list(buttons):
            b.kill()

    def show_question():
        kill_buttons()
        if qidx < len(questions):
            q = questions[qidx]
            title.change_text(f"[{q['difficulty']}] Question {qidx+1}/30")
            subtitle.change_text(q['question'])
            for i, opt in enumerate(q['options']):
                Button(screen, (100, 260 + i * 60), opt, 28, command=lambda is_right=(i == q['correct']): handle_answer(is_right))
                Button(screen, (screen.get_width() - 150, 70), "Exit", 24, command=lambda: "menu", width=100, height=40)

        else:
            return show_end_screen(screen, points, len(questions))

    def handle_answer(is_right):
        nonlocal points, qidx, questions
        if is_right:
            points += 1
        qidx += 1

        if qidx == 10:
            t1.join()
            t2.join()
            questions.extend(medium_qs)
            questions.extend(hard_qs)

        show_question()

    show_question()
    start = pygame.time.get_ticks()

    while True:
        screen.fill((255, 245, 180))
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "menu"
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for b in list(buttons):
                    if b.rect.collidepoint(ev.pos):
                        res = b.command()
                        if res in ("retry", "menu"):
                            return res

        elapsed = (pygame.time.get_ticks() - start) // 1000
        time_left = max(0, 60 - elapsed)
        if time_left <= 0:
            return show_end_screen(screen, points, len(questions))

        timer.change_text(f"Time: {time_left}s")
        score_label.change_text(f"Score: {points}")

        timer.draw()
        score_label.draw()
        title.draw()
        if qidx < len(questions):
            font_28 = pygame.font.SysFont("Arial", 28)
            draw_wrapped_text(screen, questions[qidx]['question'], 100,     190, font_28, (204, 196, 144), 600,
                              center=True)

        buttons.update()
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(60)
