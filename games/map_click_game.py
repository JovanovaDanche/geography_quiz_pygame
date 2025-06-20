import pygame
import json
import random
import time

# Load country coordinates
with open("assets/country_coords.json", "r") as f:
    country_data = json.load(f)

MAP_WIDTH, MAP_HEIGHT = 800, 600
MAP_IMAGE = pygame.image.load("assets/World_map.png")

def map_game_loop(screen, clock):
    font = pygame.font.SysFont(None, 30)
    countries = list(country_data.keys())
    random.shuffle(countries)
    index = 0
    result = ""
    timer_duration = 60
    start_time = time.time()

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(MAP_IMAGE, (0, 0))
        pygame.draw.rect(screen, (230, 230, 230), (0, 0, MAP_WIDTH, 40))

        target = countries[index]
        prompt = f"Click on: {target}"
        text = font.render(prompt, True, (0, 0, 0))
        screen.blit(text, (10, 10))

        elapsed_time = time.time() - start_time
        time_left = max(0, int(timer_duration - elapsed_time))
        timer_text = font.render(f"Time: {time_left}s", True, (0, 0, 0))
        screen.blit(timer_text, (650, 10))

        if result:
            result_text = font.render(result, True, (0, 128, 0) if "Correct" in result else (200, 0, 0))
            screen.blit(result_text, (10, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                true_x, true_y = country_data[target]["coords"]

                pygame.draw.circle(screen, (255, 0, 0), (true_x, true_y), 10)

                if abs(x - true_x) < 20 and abs(y - true_y) < 20:
                    result = "✅ Correct!"
                    index += 1
                    if index >= len(countries):
                        index = 0
                        random.shuffle(countries)
                    start_time = time.time()
                else:
                    result = f"❌ Wrong! Try again."

        if elapsed_time > timer_duration:
            result = f"⏰ Time's up!"
            index += 1
            if index >= len(countries):
                index = 0
                random.shuffle(countries)
            start_time = time.time()

        pygame.display.flip()
        clock.tick(30)