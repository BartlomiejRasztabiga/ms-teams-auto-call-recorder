from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from datetime import datetime
from pynput.keyboard import Key, Controller
import json
import os


class ScreenRecorder(object):
    def __init__(self):
        self.recording = False

    def __sendRecordStopCombination(self):
        keyboard.press(Key.cmd)
        keyboard.press(Key.alt)
        keyboard.press('r')
        keyboard.release(Key.cmd)
        keyboard.release(Key.alt)
        keyboard.release('r')

    def start(self):
        if (not self.recording):
            self.__sendRecordStopCombination()
            self.recording = True

    def stop(self):
        if (self.recording):
            self.__sendRecordStopCombination()
            self.recording = False


sleepDelay = 2      # increase if you have a slow internet connection
timeOutDelay = 30   # increase if you have a slow internet connection

maxParticipants = curParticipants = 0
minParticipants = 10

opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.notifications": 1
})

browser = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
screenRecorder = ScreenRecorder()
keyboard = Controller()


def wait_and_find_ele_by_id(id, timeout=timeOutDelay):
    sleep(sleepDelay)
    for i in range(timeout):
        try:
            ele = browser.find_element_by_id(id)
        except:
            sleep(sleepDelay)
        else:
            return ele


def wait_and_find_ele_by_link_text(text, timeout=timeOutDelay):
    sleep(sleepDelay)
    for i in range(timeout):
        try:
            ele = browser.find_element_by_link_text(text)
        except:
            sleep(sleepDelay)
        else:
            return ele


def wait_and_find_element_by_xpath(xpath, timeout=timeOutDelay):
    sleep(sleepDelay)
    for i in range(timeout):
        try:
            ele = browser.find_element_by_xpath(xpath)
        except:
            sleep(sleepDelay)
        else:
            return ele


def wait_and_find_elements_by_xpath(xpath, timeout=timeOutDelay):
    sleep(sleepDelay)
    for i in range(timeout):
        try:
            ele = browser.find_elements_by_xpath(xpath)
        except:
            sleep(sleepDelay)
        else:
            return ele


def checkAndJoinMeeting():
    global maxParticipants, curParticipants
    joins = wait_and_find_elements_by_xpath('//button[.="Dołącz"]', 3)
    if len(joins) == 0:  # no meeting scheduled
        return
    # join the latest meeting scheduled i.e if join buttons for 9 A.M and 10 A.M available, will join 10 A.M
    joins[-1].click()
    elem = wait_and_find_element_by_xpath(
        '//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button', timeOutDelay)
    if elem.get_attribute('aria-pressed') == 'true':  # turn off camera
        elem.click()
    elem = wait_and_find_element_by_xpath(
        '//*[@id="preJoinAudioButton"]/div/button', timeOutDelay)
    if elem.get_attribute('aria-pressed') == 'true':  # turn off microphone
        elem.click()
    wait_and_find_element_by_xpath(
        '//button[.="Dołącz teraz"]', timeOutDelay).click()  # join meeting
    print('Joined the meeting at {}'.format(datetime.now()))
    screenRecorder.start()
    sleep(60*5)
    actions = ActionChains(browser)
    rosterBtn = wait_and_find_element_by_xpath(
        '//button[@id="roster-button"]', timeOutDelay)
    actions.move_to_element(rosterBtn).click().perform()
    numStr = wait_and_find_elements_by_xpath(
        '//span[@class="toggle-number"][@ng-if="::ctrl.enableRosterParticipantsLimit"]')
    if len(numStr) >= 2:
        if numStr[1].text[1:-1] != '':
            maxParticipants = curParticipants = int(numStr[1].text[1:-1])
    elif len(numStr) == 0:
        actions.move_to_element(rosterBtn).click().perform()


def checkAndEndOrLeaveOrJoinMeeting():
    global maxParticipants, curParticipants
    hangupBtn = wait_and_find_element_by_xpath(
        '//button[@id="hangup-button"]', 2)
    if hangupBtn != None:  # currently in meeting
        numStr = wait_and_find_elements_by_xpath(
            '//span[@class="toggle-number"][@ng-if="::ctrl.enableRosterParticipantsLimit"]')
        if len(numStr) >= 2:
            if numStr[1].text[1:-1] != '':
                curParticipants = int(numStr[1].text[1:-1])
            else:
                actions = ActionChains(browser)
                actions.move_to_element(wait_and_find_element_by_xpath(
                    '//button[@id="roster-button"]', timeOutDelay)).click().perform()
        maxParticipants = max(maxParticipants, curParticipants)
        # leaves the meeting automatically for given condition
        if curParticipants <= minParticipants and curParticipants != 0:
            hangupBtn = wait_and_find_element_by_xpath(
                '//button[@id="hangup-button"]', 3)
            actions = ActionChains(browser)
            actions.move_to_element(hangupBtn).click().perform()
            print('Left meeting at {}'.format(datetime.now()))
            screenRecorder.stop()
            # open calendar tab
            browser.get('https://teams.microsoft.com/_#/calendarv2')
        else:
            return
    else:
        maxParticipants = curParticipants = 0
        browser.get('https://teams.microsoft.com/_#/calendarv2')
        checkAndJoinMeeting()


def init():
    global minParticipants
    # open calendar tab in teams
    browser.get('https://teams.microsoft.com/_#/calendarv2')
    sleep(1)
    with open(os.path.join(os.path.curdir, 'config.json')) as f:
        data = json.load(f)
    minParticipants = data['minimumParticipants']
    wait_and_find_ele_by_id('i0116', timeOutDelay).send_keys(
        data['username'])      # enter username
    wait_and_find_ele_by_id('idSIButton9', timeOutDelay).click(
    )                    # click next
    wait_and_find_ele_by_id('i0118', timeOutDelay).send_keys(
        data['password'])      # enter password
    wait_and_find_ele_by_id('idSIButton9', timeOutDelay).click(
    )                    # click next
    wait_and_find_ele_by_id('idSIButton9', timeOutDelay).click(
    )                    # click yes to stay signed in
    # click use the web app instead link
    wait_and_find_ele_by_link_text(
        'Zamiast tego użyj aplikacji internetowej', timeOutDelay).click()
    # wait for calendar tab to completely load
    while wait_and_find_element_by_xpath('//button[@title="Zmień widok kalendarza"]', timeOutDelay) == None:
        sleep(5)
    # change calender work-week view to week view
    while wait_and_find_element_by_xpath('//button[@title="Zmień widok kalendarza"]', timeOutDelay).get_attribute('name') != "Tydzień roboczy":
        wait_and_find_element_by_xpath(
            '//button[@title="Zmień widok kalendarza"]', timeOutDelay).click()
        wait_and_find_element_by_xpath(
            '//button[@name="Tydzień roboczy"]', timeOutDelay).click()
    print('Initialized Succesfully at {}'.format(datetime.now()))
    checkAndJoinMeeting()


def main():
    global browser
    try:
        init()
    except:
        print('init failed, trying again')
        main()
    else:
        while True:
            try:
                checkAndEndOrLeaveOrJoinMeeting()
            except:
                print('join meeting failed, trying again')
                # open calendar tab in teams
                browser.get('https://teams.microsoft.com/_#/calendarv2')
            else:
                sleep(3)


if __name__ == "__main__":
    main()
