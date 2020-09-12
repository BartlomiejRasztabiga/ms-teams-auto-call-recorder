from pynput.keyboard import Key, Controller

class WindowsBuiltInScreenRecorder:
    def __init__(self):
        self.recording = False
        self.keyboard: Controller = Controller()

    def __sendRecordStopCombination(self):
        self.keyboard.press(Key.cmd)
        self.keyboard.press(Key.alt)
        self.keyboard.press('r')
        self.keyboard.release(Key.cmd)
        self.keyboard.release(Key.alt)
        self.keyboard.release('r')

    def start(self):
        if (not self.recording):
            print('starting recording')
            self.__sendRecordStopCombination()
            self.recording = True

    def stop(self):
        if (self.recording):
            print('stopping recording')
            self.__sendRecordStopCombination()
            self.recording = False