import threading
from pynput import keyboard
class GlobalHotkeys:
    def __init__(self, on_toggle_listen=None, on_focus=None):
        self.on_toggle_listen = on_toggle_listen
        self.on_focus = on_focus
        self.listener = None
    def _handler(self, key):
        try:
            if key == keyboard.Key.space and self.ctrl and self.alt:
                if self.on_toggle_listen:
                    self.on_toggle_listen()
        except Exception:
            pass
    def _on_press(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl = True
        if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
            self.alt = True
        self._handler(key)
    def _on_release(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl = False
        if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
            self.alt = False
    def start(self):
        self.ctrl = False
        self.alt = False
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        t = threading.Thread(target=self.listener.start)
        t.daemon = True
        t.start()