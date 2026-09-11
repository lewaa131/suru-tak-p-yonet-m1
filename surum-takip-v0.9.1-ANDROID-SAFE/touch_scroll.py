"""Buttons remain scroll candidates even when a finger pauses before dragging."""
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior


class TouchScrollView(ScrollView):
    def _change_touch_mode(self, *args):
        touch = self._touch
        if touch is not None and self._viewport is not None:
            for widget in self._viewport.walk():
                if isinstance(widget, ButtonBehavior) and widget.collide_point(*widget.to_widget(*touch.pos)):
                    # Keep ownership until movement or release. The normal
                    # ScrollView release path still delivers an ordinary tap.
                    # Text fields retain Kivy's long-press/selection handling.
                    return
        return super()._change_touch_mode(*args)
