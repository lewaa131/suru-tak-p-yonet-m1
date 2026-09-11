"""All dialogs share the same theme and Android back behavior."""
from kivy.app import App
from kivy.uix.popup import Popup


class AppPopup(Popup):
    def open(self, *args, **kwargs):
        kwargs.setdefault('animation', False)
        return super().open(*args, **kwargs)

    def dismiss(self, *args, **kwargs):
        kwargs.setdefault('animation', False)
        return super().dismiss(*args, **kwargs)

    def __init__(self, **kwargs):
        kwargs.setdefault('background', '')
        kwargs.setdefault('background_color', (.94, .98, .95, 1))
        kwargs.setdefault('title_color', (.05, .28, .19, 1))
        kwargs.setdefault('separator_color', (.10, .48, .32, 1))
        kwargs.setdefault('auto_dismiss', False)
        super().__init__(**kwargs)

    def on_open(self):
        app = App.get_running_app()
        if app:
            app.popup_stack.append(self)

    def on_dismiss(self):
        app = App.get_running_app()
        if app and self in app.popup_stack:
            app.popup_stack.remove(self)
        for widget in self.walk():
            if hasattr(widget, 'focus'): widget.focus = False

    def _handle_keyboard(self, window, key, *args):
        if key in (27, 1001):
            App.get_running_app().go_back()
            return True
        return super()._handle_keyboard(window, key, *args)
