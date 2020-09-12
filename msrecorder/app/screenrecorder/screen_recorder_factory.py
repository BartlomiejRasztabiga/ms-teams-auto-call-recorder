from .windows_built_in_screen_recorder import WindowsBuiltInScreenRecorder

class ScreenRecorderFactory:
    def create_screen_recorder(self):
        return WindowsBuiltInScreenRecorder()
