import pygame
import random
from shapely.geometry import Point
from svg_parser import load_country_polygons

MAP_PATH = "assets/europe_map.png"
SVG_PATH = "svg/Blank_map_of_Europe_(with_disputed_regions).svg"

id_to_name = {
    "be": "Belgium", "hr": "Croatia", "es": "Spain", "al": "Albania", "at": "Austria",
    "by": "Belarus", "bg": "Bulgaria", "ch": "Switzerland", "cy": "Cyprus", "dz": "Algeria",
    "ge": "Georgia", "gi": "Gibraltar", "hu": "Hungary", "il": "Israel", "iq": "Iraq",
    "ir": "Iran", "lb": "Lebanon", "li": "Liechtenstein", "lu": "Luxembourg", "ma": "Morocco",
    "mc": "Monaco", "me": "Montenegro", "mk": "North Macedonia", "pt": "Portugal", "sk": "Slovakia",
    "sm": "San Marino", "sy": "Syria", "tr-europe": "Turkey", "va": "Vatican City",
    "south_ossetia": "Georgia", "golan_heights": "Syria", "se": "Sweden", "am": "Armenia",
    "ba": "Bosnia and Herzegovina", "ee": "Estonia", "xk": "Kosovo", "ua": "Ukraine",
    "tn": "Tunisia", "ro": "Romania", "mt": "Malta", "nl": "Netherlands", "no": "Norway", "gl": "Greenland"
}


def map_game_loop(screen, clock):
    game_duration = 5 * 60 * 1000  # 5 minutes
    start_time = pygame.time.get_ticks()

    map_img = pygame.image.load(MAP_PATH)
    font = pygame.font.SysFont("Segoe UI", 36)
    timer_font = pygame.font.SysFont("Segoe UI", 23)

    polygons_by_id = load_country_polygons(SVG_PATH)

    countries = {}
    for cid, poly in polygons_by_id.items():
        if cid in id_to_name:
            countries[id_to_name[cid]] = poly

    if not countries:
        error_msg = "No valid countries found in SVG!"
        print(error_msg)
        error_text = font.render(error_msg, True, (255, 0, 0))
        screen.blit(error_text, (50, 50))
        pygame.display.flip()
        pygame.time.wait(3000)
        return

    score = 0
    remaining_countries = list(countries.keys())
    random.shuffle(remaining_countries)
    current_country = remaining_countries.pop()
    feedback = ""
    feedback_time = 0

    running = True
    game_over = False
    game_over_time = 0

    hint_button = pygame.Rect(screen.get_width() - 100, 60, 80, 25)
    hint_active = False
    hint_start_time = 0

    exit_button = pygame.Rect(screen.get_width() - 100, 100, 80, 25)

    while running:
        screen.fill((0, 0, 0))
        screen.blit(map_img, (0, 0))

        elapsed = pygame.time.get_ticks() - start_time
        remaining_time = max(0, game_duration - elapsed)

        prompt = font.render(f"Click on: {current_country}", True, (255, 255, 255))
        screen.blit(prompt, (20, 530))

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (630, 530))

        minutes = remaining_time // 60000
        seconds = (remaining_time % 60000) // 1000
        timer_text = timer_font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(timer_text, (screen.get_width() - 120, 20))

        mouse_pos = pygame.mouse.get_pos()

        if hint_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (74, 144, 226), hint_button, border_radius=12)
            hint_text = timer_font.render("Hint", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (255, 255, 255), hint_button, border_radius=12)
            hint_text = timer_font.render("Hint", True, (249, 211, 66))
        text_rect = hint_text.get_rect(center=hint_button.center)
        screen.blit(hint_text, text_rect)

        if exit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (74, 144, 226), exit_button, border_radius=12)
            exit_text = timer_font.render("Exit", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (255, 255, 255), exit_button, border_radius=12)
            exit_text = timer_font.render("Exit", True, (249, 211, 66))
        exit_text_rect = exit_text.get_rect(center=exit_button.center)
        screen.blit(exit_text, exit_text_rect)

        if remaining_time <= 0 and not game_over:
            feedback = "Time's up!"
            feedback_time = pygame.time.get_ticks()
            game_over = True
            game_over_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_pos = event.pos
                point = Point(mouse_pos)

                if hint_button.collidepoint(mouse_pos) and not hint_active:
                    hint_active = True
                    hint_start_time = pygame.time.get_ticks()

                if exit_button.collidepoint(mouse_pos):
                    running = False
                    break

                clicked = None
                for name, poly in countries.items():
                    if name in ["Monaco", "Vatican City", "Liechtenstein", "San Marino", "Gibraltar", "Syria"]:
                        if poly.buffer(5).contains(point):
                            clicked = name
                            break
                    elif poly.contains(point):
                        clicked = name
                        break

                if clicked:
                    if clicked == current_country:
                        score += 1
                        feedback = "Correct! +1"
                        feedback_time = pygame.time.get_ticks()

                        if remaining_countries:
                            current_country = remaining_countries.pop()
                        else:
                            feedback = "Game over! You guessed all countries!"
                            feedback_time = pygame.time.get_ticks()
                            game_over = True
                            game_over_time = pygame.time.get_ticks()
                    else:
                        feedback = "Wrong!"
                        feedback_time = pygame.time.get_ticks()

        if pygame.time.get_ticks() - feedback_time < 1000:
            color = (0, 255, 0) if "Correct" in feedback or "guessed all" in feedback else (255, 0, 0)
            fb_text = font.render(feedback, True, color)
            screen.blit(fb_text, (300, 200))

        if hint_active:
            center = countries[current_country].centroid
            pygame.draw.circle(screen, (255, 255, 0), (int(center.x), int(center.y)), 60, 4)
            if pygame.time.get_ticks() - hint_start_time > 3000:
                hint_active = False

        if game_over and pygame.time.get_ticks() - game_over_time > 2000:
            running = False

        pygame.display.flip()
        clock.tick(60)
