from ursina import *
from django_questions import questions


class StartScreen(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.background_texture = 'static/img/black.jpg'
        self.background = Entity(model='quad', scale=(16, 9), texture=self.background_texture)
        self.custom_font = 'static/font/quiz_font.ttf'
        self.start_button = Button(text='Начать игру', texture=load_texture('static/img/button_1.png'),
                                   parent=self, scale=(0.4, 0.1), color=color.black10, radius=0.3, y=-0.05)
        self.start_button.text_entity.font = self.custom_font
        self.start_button.on_click = self.start_game
        start_text = 'Привет, игрок!'
        self.start_text_entity = Text(text=start_text, parent=self, color=color.white, font=self.custom_font,
                                      scale=(1, 1), y=0.38, x=-0.130)

        self.exit_button = Button(text='Выход', texture=load_texture('static/img/button_1.png'), parent=self,
                                  scale=(0.4, 0.1), color=color.black10, radius=0.3, y=-0.18)

        self.exit_button.text_entity.font = self.custom_font
        self.exit_button.on_click = application.quit

    def start_game(self):
        self.disable()
        quiz_game = QuizGame()

    def set_start_text(self, start_text):
        wrapped_text = self.wrap_text(start_text, 20)
        self.start_text_entity.text = wrapped_text

    def wrap_text(self, text, width):
        lines = []
        line = ''
        for word in text.split():
            if len(line) + len(word) <= width:
                line += word + ' '
            else:
                lines.append(line)
                line = word + ' '
        if line:
            lines.append(line)
        return '\n'.join(lines)


class FactWindow(Entity):
    def __init__(self, custom_font, fact_text, callback, **kwargs):
        super().__init__(parent=camera.ui, model='quad', scale=(0.45, 0.4), color=color.black10, position=(-0, 0.05),
                         **kwargs)
        self.custom_font = custom_font
        self.fact_text_entity = Text(text=fact_text, parent=self, font=self.custom_font, scale=(2, 2), y=0.48, x=-0.41)
        self.set_fact_text(fact_text)
        self.continue_button = Button(text='Продолжить', texture=load_texture('static/img/button_1.png'), parent=self,
                                      scale=(0.4, 0.1), color=color.black10, radius=0.3, on_click=callback, y=-0.4,
                                      x=0)
        self.continue_button.text_entity.scale *= 0.6
        self.continue_button.text_entity.font = custom_font
        self.continue_button.enabled = False
        self.text_animation_text = ''
        self.text_animation_index = 0
        self.time_since_last_letter = 0

    def set_fact_text(self, fact_text):
        wrapped_text = self.wrap_text(fact_text, 29)
        self.fact_text_entity.text = wrapped_text

    def wrap_text(self, text, width):
        lines = []
        line = ''
        for word in text.split():
            if len(line) + len(word) <= width:
                line += word + ' '
            else:
                lines.append(line)
                line = word + ' '
        if line:
            lines.append(line)
        return '\n'.join(lines)


class QuizGame(Entity):
    def __init__(self):
        super().__init__()

        self.but_texture = load_texture('static/img/button_1.png')

        self.background_texture = 'static/img/black.jpg'

        self.custom_font = 'static/font/quiz_font.ttf'

        self.questions = questions

        self.score = 0
        self.current_question_index = 0

        self.background = Entity(model='quad', scale=(16, 9), texture=self.background_texture)
        self.stars_text = Text(text=f'{self.score}', font=self.custom_font, scale=(1.5, 1), y=0.436, x=-0.03)

        self.question_text = Text(text="", font=self.custom_font, scale=(1.3, 1), y=0.26, x=-0.21)

        self.option_buttons = []

        self.button_positions = [
            (-0.5, -0.19),
            (-0.5, -0.10),
            (0.5, -0.19),
            (0.5, -0.10)
        ]

        self.text_animation_text = ''
        self.text_animation_index = 0
        self.time_since_last_letter = 0

        self.fact_window = FactWindow(self.custom_font, '', self.continue_game, enabled=False)
        self.current_question_buttons = []

        for i, option in enumerate(["A", "B", "C", "D"]):
            button = Button(
                text=option,
                texture=load_texture('static/img/button_3.png'),
                font=self.custom_font,
                color=color.black10,
                scale=(0.6, 0.07),
                position=self.button_positions[i],
                enabled=True,
                radius=0.3
            )
            button.text_entity.font = self.custom_font
            button.on_click = lambda button=button: self.check_answer(button)
            self.option_buttons.append(button)

        self.next_question()

    def next_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.animate_question_text(question_data["question"])
            options = question_data["options"]
            correct_option_index = question_data["correct_option"]

            for i, button in enumerate(self.option_buttons):
                button.text = options[i]
                button.text_entity.scale = (0.08, 0.45)
                button.color = color.black
                button.alpha = 0.9
                button.scale = (0.6, 0.07)
                button.enabled = True
                button.disabled = False
                self.question_text.enabled = True
                if i == correct_option_index:
                    button.correct = True
                else:
                    button.correct = False

            self.current_question_index += 1
        else:
            self.game_over()

    def animate_question_text(self, text):
        wrapped_text = self.wrap_text(text, 20)
        self.question_text.text = ""
        self.text_animation_text = wrapped_text
        self.text_animation_index = 0
        self.time_since_last_letter = 0

    def wrap_text(self, text, width):
        lines = []
        line = ''
        for word in text.split():
            if len(line) + len(word) <= width:
                line += word + ' '
            else:
                lines.append(line)
                line = word + ' '
        if line:
            lines.append(line)
        return '\n'.join(lines)

    def animate_text(self):
        if self.text_animation_index < len(self.text_animation_text):
            self.time_since_last_letter += time.dt
            if self.time_since_last_letter > 0.02:
                self.question_text.text += self.text_animation_text[self.text_animation_index]
                self.text_animation_index += 1
                self.time_since_last_letter = 0

    def update(self):
        self.animate_text()

    def show_fact_window(self, fact_text):
        self.fact_window.enabled = True
        self.fact_window.set_fact_text(fact_text)
        for button in self.option_buttons:
            button.enabled = False
            self.question_text.enabled = False
        self.fact_window.continue_button.enabled = True

    def continue_game(self):
        self.fact_window.enabled = False
        self.fact_window.continue_button.enabled = False
        for button in self.current_question_buttons:
            button.enabled = True

        self.next_question()

    def check_answer(self, button):
        if self.option_buttons.index(button) == self.questions[self.current_question_index - 1]["correct_option"]:
            button.color = color.white10
            Audio('static/audio/correct.wav')
            self.score += 1
            invoke(self.show_fact_window, delay=1,
                   fact_text=self.questions[self.current_question_index - 1]["fact_text"])
            self.current_question_buttons = self.option_buttons[:]
        else:
            button.color = color.red
            button.disabled = True
            button.animate_scale((0.5, 0.06), duration=0.4, curve=curve.in_out_circ)
            Audio('static/audio/no.wav')
            if self.score > 0:
                self.score -= 1

        self.stars_text.text = f'{self.score}'
        self.current_question_buttons = []

    def game_over(self):
        self.text = Text(text='Поздравляем!', font=self.custom_font, scale=(1.5, 1.5), position=(-0.17, 0.2))
        self.score = Text(text=f'Вот сколько очков ты набрал: {self.score} из 5!', font=self.custom_font,
                          position=(-0.29, 0.0))

        self.restart_button = Button(text='Начать снова', texture=load_texture('static/img/button_1.png'),
                                     scale=(0.4, 0.1), color=color.black10, radius=0.3, y=-0.15)
        self.restart_button.text_entity.font = self.custom_font
        self.restart_button.on_click = self.game_restart

        self.exit_button = Button(text='Выход', texture=load_texture('static/img/button_1.png'),
                                  scale=(0.4, 0.1), color=color.black10, radius=0.3, y=-0.3)
        self.exit_button.text_entity.font = self.custom_font
        self.exit_button.on_click = application.quit

        for button in self.option_buttons:
            button.enabled = False

    def game_restart(self):
        self.text.enabled = False
        self.score.enabled = False
        self.stars_text.enabled = False
        self.restart_button.enabled = False
        self.exit_button.enabled = False
        self.quiz_game = QuizGame()


if __name__ == "__main__":
    app = Ursina(fullscreen=True)
    Cursor(texture=load_texture("static/img/cursor_1.png"), scale=(0.02, 0.02))
    mouse.visible = False
    window.fps_counter.enabled = False
    window.cog_button.enabled = False
    start_screen = StartScreen(enabled=True)
    app.run()
