from algorithms.selection_sort import SelectionSort
from algorithms.insertion_sort import InsertionSort
from algorithms.bubble_sort import BubbleSort
from algorithms.quick_sort import QuickSort
from algorithms.shell_sort import ShellSort
from algorithms.merge_sort import MergeSort
from algorithms.tree_sort import TreeSort
from algorithms.bogo_sort import BogoSort
import pygame.freetype
import pygame
import math


class Page:
    def __init__(self):
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def add_widgets(self, *widgets):
        self.widgets.extend(widgets)

    def update(self, window):
        for widget in self.widgets:
            widget.update(window)


class Label:
    def __init__(self, text, size=20, pos=None, center=None):
        self.text = text
        self.size = size
        self.pos = pos
        self.center = center

    def update(self, window):
        text_rect = window.font.get_rect(self.text, size=self.size)
        if not self.pos is None:
            dest = (self.pos[0] * window.size[0], self.pos[1] * window.size[1])
        else:
            dest = (self.center[0] * window.size[0] - text_rect[2] / 2,
                    self.center[1] * window.size[1] - text_rect[3] / 2)
        window.font.render_to(window.window, dest, self.text,
                              (255, 255, 255), size=self.size)


class Button:
    def __init__(self, text, callback, size=20, pos=None, center=None, keep=False, toggled=False):
        self.text = text
        self.size = size
        self.callback = callback
        self.pos = pos
        self.center = center
        self.keep = keep
        self.clicked = toggled

    def update(self, window):
        if not self.pos is None:
            rect = pygame.Rect(
                self.pos[0] * window.size[0], self.pos[1] * window.size[1], 200, 30)
        else:
            rect = pygame.Rect(
                self.center[0] * window.size[0] - 100, self.center[1] * window.size[1] - 15, 200, 30)

        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos) or self.clicked:
            if window.clicked or self.clicked:
                color = (150, 150, 150)
                rect[0] += 2
                rect[1] += 2
                rect[2] -= 4
                rect[3] -= 4
                if window.clicked == 5 and not self.clicked:
                    if self.keep:
                        for widget in window.opened_page.widgets:
                            if isinstance(widget, Button):
                                widget.clicked = False
                        self.clicked = True
                    self.callback()
            else:
                color = (150, 150, 150)
        else:
            color = (100, 100, 100)

        pygame.draw.rect(window.window, color, rect, border_radius=3)

        text_rect = window.font.get_rect(self.text, size=self.size)
        dest = (rect.centerx - text_rect[2] //
                2, rect.centery - text_rect[3] // 2)
        window.font.render_to(window.window, dest, self.text, size=self.size)


class Slider:
    def __init__(self, start, end, value, pos, callback, show=False, integer=False):
        self.start = start
        self.end = end
        self.value = value
        self.pos = pos
        self.callback = callback
        self.float_value = (value - start) / (end - start)
        self.clicked = False
        self.show = show
        self.integer = integer

    def update(self, window):
        rect = self.pos[0] * window.size[0], self.pos[1] * \
            window.size[1] - 2, 100, 4
        pygame.draw.rect(window.window, (100, 100, 100), rect, border_radius=3)

        radius = 8
        circle_pos = (rect[0] + self.float_value *
                      rect[2], rect[1] + rect[3] / 2)
        mouse_pos = pygame.mouse.get_pos()

        if math.dist(circle_pos, mouse_pos) <= radius and window.clicked:
            self.clicked = (circle_pos[0] - mouse_pos[0],
                            circle_pos[1] - mouse_pos[1])
        elif self.clicked and not any(pygame.mouse.get_pressed()):
            self.clicked = False
            self.callback(self.value)

        if self.clicked:
            self.float_value = min(
                1, max(0, (mouse_pos[0] + self.clicked[0] - rect[0]) / rect[2]))
            self.value = (self.start + self.float_value *
                          (self.end - self.start))
            if self.integer:
                self.value = round(self.value)
                self.float_value = ((self.value - self.start) /
                                    (self.end - self.start))
            color = (200, 200, 200)
        else:
            color = (150, 150, 150)

        pygame.draw.circle(window.window, color, circle_pos, radius)
        if self.show:
            height = window.font.get_rect("A")[3]
            window.font.render_to(
                window.window, (rect[0] + rect[2] + height, rect[1] - height / 2), str(self.value), (255, 255, 255))


class SortingChart:
    def __init__(self, values, algorithm):
        self.values = values
        self.algorithm = algorithm()
        self.sorted = False
        self.paused = True
        self.iteration_delay = 400
        self.cooldown = 0

        self.array = [i for i in values]
        # self.algorithm.shuffle(self.array)

    def set_speed(self, value):
        self.iteration_delay = 400 - min(400, value)

    def set_values(self, value_count):
        self.values = range(value_count)
        self.array = [i for i in self.values]

    def toggle_pause(self):
        self.paused = not self.paused

    def set_paused(self, value):
        self.paused = value

    def reset(self):
        self.paused = True
        self.sorted = False
        self.algorithm.shuffle(self.array)
        self.algorithm.reset()

    @staticmethod
    def get_algorithms():
        return {
            "Selection Sort": SelectionSort,
            "Insertion Sort": InsertionSort,
            "Bubble Sort": BubbleSort,
            "Quick Sort": QuickSort,
            "Shell Sort": ShellSort,
            "Merge Sort": MergeSort,
            "Tree Sort": TreeSort,
            "Bogo Sort": BogoSort,
        }

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm()

    def update(self, window):
        if self.cooldown > self.iteration_delay and not (self.paused or self.sorted):
            self.cooldown = 0
            self.algorithm.sort(self.array)

        bar_width = (window.size[0] - 250) // len(self.array)
        bar_height = (window.size[1] - 10) // len(self.array)
        for i, x in enumerate(self.array):
            if i == self.algorithm.highlight_sorting:
                color = (100, 255, 150)
            elif i == self.algorithm.highlight_comparing:
                color = (255, 150, 200)
            elif i in self.algorithm.highlight_sorted:
                color = (200, 200, 200)
            else:
                color = (100, 100, 100)

            pygame.draw.rect(
                window.window,
                color,
                (245 + bar_width * 0.1 + i * bar_width, window.size[1] - 5 - bar_height * (x + 1), bar_width * 0.9, bar_height * (x + 1))
            )


class Window:
    def __init__(self, title, n):
        pygame.init()

        info = pygame.display.Info()
        self.size = (info.current_w / 3 * 2, info.current_h / 5 * 3)
        self.window = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.font = pygame.freetype.SysFont(None, 15)
        self.clicked = False
        pygame.display.set_caption(title)

        #self.iterations = 0
        #self.algorithm = SelectionSort()
        #self.timer = 0
        #self.paused = True
        #self.done = False
        #self.speed = 200
        #self.button_cooldown = 0

        self.page_sorting = Page()
        self.page_options = Page()
        self.opened_page = self.page_options
        self.sorting_chart = SortingChart(range(20), SelectionSort)

        self.page_sorting.add_widgets(
            Button(
                "Options",
                lambda: (self.open_page(self.page_options),
                         self.sorting_chart.set_paused(True)),
                pos=(0.015, 0.03)
            ),
            Button(
                "Play/Pause",
                self.sorting_chart.toggle_pause,
                pos=(0.015, 0.13)
            ),
            Button(
                "Randomize",
                self.sorting_chart.reset,
                pos=(0.015, 0.23)
            ),
            self.sorting_chart,
        )

        self.page_options.add_widgets(
            Label("Sorting Algorithms", center=(0.5, 0.1), size=30),
            Label("Algorithm", center=(0.3, 0.2)),

            Label("Options", center=(0.8, 0.2)),
            Label("Speed", pos=(0.65, 0.3)),
            Slider(0, 400, 200, (0.8, 0.32), self.sorting_chart.set_speed),
            Label("Numbers", pos=(0.65, 0.4)),
            Slider(1, 100, 20, (0.8, 0.42), self.sorting_chart.set_values, show=True, integer=True),

            Button(
                "Done",
                lambda: self.open_page(self.page_sorting),
                center=(0.5, 0.9)
            )
        )

        for i, (name, algorithm) in enumerate(SortingChart.get_algorithms().items()):
            button = Button(
                name,
                lambda a=algorithm: self.sorting_chart.set_algorithm(a),
                center=(0.15 + 0.3 * (i % 2), 0.3 + 0.09 * (i // 2)),
                keep=True,
                toggled=isinstance(self.sorting_chart.algorithm, algorithm)
            )
            self.page_options.add_widget(button)

    def open_page(self, page):
        self.opened_page = page

    #def reset(self):
    #    self.iterations = 0
    #    self.done = False
    #    self.paused = True

    def events(self):
        if self.clicked:
            self.clicked -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.clicked = 5

    def run(self):
        while True:
            # Get events
            self.events()
            self.window.fill((0, 0, 0))
            self.opened_page.update(self)

            # Gear
            """
            center = (15, 15)
            radius = 10
            points = []
            for i in range(36):
                angle = i * math.pi / 18
                points.append((
                    round(center[0] + math.cos(angle) *
                          (radius + radius // 3 * (i // 2 % 2)), 2),
                    round(center[1] + math.sin(angle) *
                          (radius + radius // 3 * (i // 2 % 2)), 2)
                ))
            pygame.draw.polygon(self.window, (255, 255, 255), points)
            pygame.draw.circle(self.window, (0, 0, 0), center, radius // 1.5)
            """

            # Buttons
            """
            # Draw buttons
            buttons = [
                "Fps: " + str(round(self.clock.get_fps())),
                "",
                "> Selection Sort",
                "> Insertion Sort",
                "> Bubble Sort",
                "> Quick Sort",
                "> Bogo Sort",
                "",
                "> Iterate",
                "> Play",
                "> Measure",
                "> Randomize",
                "> Increase Speed",
                "> Decrease Speed",
                "",
                "Stats:",
                " Iterations: " + str(self.iterations),
            ]
            if isinstance(self.algorithm, SelectionSort):
                buttons[2] = "-" + buttons[2][1:]
            elif isinstance(self.algorithm, InsertionSort):
                buttons[3] = "-" + buttons[3][1:]
            elif isinstance(self.algorithm, BubbleSort):
                buttons[4] = "-" + buttons[4][1:]
            elif isinstance(self.algorithm, QuickSort):
                buttons[5] = "-" + buttons[5][1:]
            elif isinstance(self.algorithm, BogoSort):
                buttons[6] = "-" + buttons[6][1:]

            if not self.paused:
                buttons[9] = "> Pause"

            self.button_cooldown += 1
            for i, text in enumerate(buttons):
                color = (255, 255, 255)

                if text and text[0] == ">":
                    m = pygame.mouse.get_pos()
                    hover = m[0] < 100 and i < (m[1] - 10) / 20 < i + 1
                    if hover:
                        color = (200, 200, 200)

                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    if self.button_cooldown > 10 and mouse_pressed and hover:
                        self.button_cooldown = 0
                        if text == "> Selection Sort":
                            self.algorithm = SelectionSort()
                            self.reset()
                        elif text == "> Insertion Sort":
                            self.algorithm = InsertionSort()
                            self.reset()
                        elif text == "> Bubble Sort":
                            self.algorithm = BubbleSort()
                            self.reset()
                        elif text == "> Quick Sort":
                            self.algorithm = QuickSort()
                            self.reset()
                        elif text == "> Bogo Sort":
                            self.algorithm = BogoSort()
                            self.reset()
                        elif text == "> Iterate":
                            self.iter()
                            self.paused = True
                        elif text == "> Play":
                            self.paused = False
                        elif text == "> Pause":
                            self.paused = True
                        elif text == "> Randomize":
                            SelectionSort.shuffle(self.array)
                            self.algorithm.reset()
                            self.reset()
                        elif text == "> Increase Speed":
                            self.speed = max(10, self.speed - 10)
                        elif text == "> Decrease Speed":
                            self.speed += 10

                self.font.render_to(
                    self.window,
                    (10, 10 + 20 * i),
                    text,
                    color
                )
            """

            """
            # Draw chart
            for i, x in enumerate(self.array):
                if i == self.algorithm.highlight_sorting:
                    color = (100, 255, 150)
                elif i == self.algorithm.highlight_comparing:
                    color = (255, 150, 200)
                elif i in self.algorithm.highlight_sorted:
                    color = (200, 200, 200)
                else:
                    color = (100, 100, 100)
                pygame.draw.rect(
                    self.window,
                    color,
                    (205 + i * 25, self.size[1] - 5 - 20 * x, 20, 20 * x)
                )
            """

            # Update display
            pygame.display.flip()
            self.sorting_chart.cooldown += self.clock.tick(60)

            # Sorting iteration
            #if self.timer > self.speed:
            #    self.timer = 0
            #    if not (self.paused or self.done):
            #        self.iter()
    """
    def iter(self):
        self.algorithm.sort(self.array)
        if self.algorithm.done:
            self.done = True
            return
        self.iterations += 1
    """

if __name__ == "__main__":
    Window("Sorting Algorithms", 20).run()