import os
os.environ['KIVY_TEXT'] = 'pil'

import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(text="User Name"))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text="Password"))
        self.password = TextInput(multiline=False)
        self.add_widget(self.password)


class MyApp(App):
    def build(self):
        self.root = root = LoginScreen()
        root.bind(size=self._update_rect, pos=self._update_rect)
        with root.canvas.before:
            Color(1, 0, 0, .75)  # green; colors range from 0-1 not 0-255
            self.rect = Rectangle(size=root.size, pos=root.pos)

        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_start(self):
        print('Estou a correr...')

    def on_stop(self):
        print('Parando...')


if __name__ == '__main__':
    app = MyApp()
    app.run()