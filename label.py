import pygame



pygame.init()
def fontsize(size):
	font = pygame.font.SysFont("Arial", size)
	return font

font_default = fontsize(20)


labels = []
class Label:
    def __init__(self, screen, text, x, y, size=20, color="white", center=False):
        self.screen = screen
        self.text = text
        self.size = size
        self.color = pygame.Color(color)
        self.font = fontsize(size)
        self.center = center
        self.x = x
        self.y = y
        self.render()

        labels.append(self)

    def render(self):
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        if self.center:
            self.rect.center = (self.x, self.y)
        else:
            self.rect.topleft = (self.x, self.y)

    def change_text(self, new_text, color=None):
        self.text = new_text
        if color:
            self.color = pygame.Color(color)
        self.render()

    def change_font(self, font, size, color="white"):
        self.font = pygame.font.SysFont(font, size)
        self.color = pygame.Color(color)
        self.render()

    def draw(self):
        self.screen.blit(self.image, self.rect)


def show_labels():
	for _ in labels:
		_.draw()

def draw_wrapped_text(surface, text, x, y, font, color, max_width, center=False):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)

    for i, line in enumerate(lines):
        line_surf = font.render(line, True, color)
        if center:
            text_x = (surface.get_width() - line_surf.get_width()) // 2
        else:
            text_x = x
        surface.blit(line_surf, (text_x, y + i * font.get_linesize()))

'''     when you import this module
text1 = Text(win, "Ciao a tutti", 100, 100) # out of loop
text.draw() # into the loop
'''

if __name__ == '__main__':
	win = pygame.display.set_mode((600, 600))
	clock = pygame.time.Clock()


	Label(win, "Hello World", 100, 100, 36)
	second = Label(win, "GiovanniPython", 100, 200, 24, color="yellow")
	second.change_font("Arial", 40, "yellow")
	long_text = "This is a very long text label that will be automatically wrapped into multiple lines when it reaches the end of the screen."
	loop = 1
	while loop:
		win.fill(0)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				loop = 0
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					loop = 0
		show_labels()

		draw_wrapped_text(win, long_text, 50, 200, fontsize(24), (255, 255, 0), 500)
		pygame.display.update()
		clock.tick(60)

	pygame.quit()