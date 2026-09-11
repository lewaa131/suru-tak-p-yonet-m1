"""Small retained bridge between the Android UI thread and Kivy's event loop."""
from kivy.clock import Clock
from jnius import autoclass, PythonJavaClass, java_method


class BackAction(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    __javacontext__ = 'app'

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.host = autoclass('org.kivy.android.PythonActivity').mActivity

    @java_method('()V')
    def run(self):
        Clock.schedule_once(self.dispatch)

    def dispatch(self, *_):
        if not self.app.go_back():
            autoclass('org.surutakip.mobile.BackNavigation').background(self.host)


def install(app):
    bridge = BackAction(app)
    autoclass('org.surutakip.mobile.SafeArea').install(bridge.host)
    autoclass('org.surutakip.mobile.BackNavigation').install(bridge.host, bridge)
    return bridge
