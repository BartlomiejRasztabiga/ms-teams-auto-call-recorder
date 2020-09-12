import json
import random
import re
import time
from datetime import datetime
from threading import Timer

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from pynput.keyboard import Key, Controller

from msrecorder.app.screenrecorder.screen_recorder_factory import ScreenRecorderFactory
from msrecorder.app.models.meeting import Meeting
from msrecorder.app.config.config import Config
from msrecorder.app.models.team import Team
from msrecorder.app.models.browser import get_browser
from msrecorder.app.utils.utils import wait_until_found

# Globals
browser = get_browser()
config = Config()
print(config)
hangup_thread: Timer = None
screenRecorder = ScreenRecorderFactory().create_screen_recorder()
keyboard: Controller = Controller()


def update_current_meeting():
    meeting_id = active_meeting.meeting_id

    actionsMenu = browser.find_element_by_class_name(
        'calling-unified-bar-section')
    hover_over_element(actionsMenu)

    rosterBtn = browser.find_element_by_xpath('//button[@id="roster-button"]')
    try_click_element(rosterBtn)
    numStr = browser.find_elements_by_xpath(
        '//span[@class="toggle-number"][@ng-if="::ctrl.enableRosterParticipantsLimit"]')
    if len(numStr) >= 1:
        if numStr[1].text[1:-1] != '':
            participants = int(numStr[1].text[1:-1])
        else:
            participants = 99999
    hover_over_element(actionsMenu)
    try_click_element(rosterBtn)

    if meeting_id == active_meeting.meeting_id:
        if 'leave_if_less_than_participants' in config.config and config.config['leave_if_less_than_participants'] and participants < int(
                config.config['leave_if_less_than_participants']):
            hangup()
        elif participants == 1 and 'leave_if_last' in config.config and config.config['leave_if_last']:
            hangup()


def hover_over_element(el):
    hover = ActionChains(browser).move_to_element(el)
    hover.perform()


def try_click_element(el, delay=5):
    try:
        el.click()
    except exceptions.ElementClickInterceptedException:
        print('retrying click')
        time.sleep(delay)
        try_click_element(el)


def get_teams():
    # find all team names
    team_elems = browser.find_elements_by_css_selector(
        "ul>li[role='treeitem']>div[sv-element]")
    team_names = [team_elem.get_attribute(
        "data-tid") for team_elem in team_elems]
    team_names = [team_name[team_name.find(
        'team-') + 5:team_name.rfind("-li")] for team_name in team_names]

    team_list = [Team(browser, team_names[i], team_elems[i], i, None)
                 for i in range(len(team_elems))]
    return team_list


def join_newest_meeting(teams):
    global active_meeting, hangup_thread

    meeting_to_join = Meeting(-1,
                              None) if active_meeting is None else active_meeting
    meeting_team = None
    meeting_channel = None

    for team in teams:
        for channel in team.channels:
            if channel.blacklisted:
                continue

            for meeting in channel.meetings:
                if meeting.started_at > meeting_to_join.started_at:
                    meeting_to_join = meeting
                    meeting_team = team
                    meeting_channel = channel

    if meeting_team is None:
        return False

    print('meeting to join')

    hangup()

    channels_elem = meeting_team.expand_channels()

    meeting_channel.get_channel_elem(channels_elem).click()

    time.sleep(0.5)
    join_btn = wait_until_found(browser,
                                f"button[track-data*='{meeting_to_join.meeting_id}']", 30)
    if join_btn is None:
        return

    join_btn.click()

    join_now_btn = wait_until_found(browser,
                                    "button[data-tid='prejoin-join-button']", 30)
    if join_now_btn is None:
        return

    # turn camera off
    video_btn = browser.find_element_by_css_selector(
        "toggle-button[data-tid='toggle-video']>div>button")
    video_is_on = video_btn.get_attribute("aria-pressed")
    if video_is_on == "true":
        video_btn.click()

    # turn mic off
    audio_btn = browser.find_element_by_css_selector(
        "toggle-button[data-tid='toggle-mute']>div>button")
    audio_is_on = audio_btn.get_attribute("aria-pressed")
    if audio_is_on == "true":
        audio_btn.click()

    if 'random_delay' in config.config and config.config['random_delay']:
        delay = random.randrange(10, 31, 1)
        print(f"Wating for {delay}s")
        time.sleep(delay)

    join_now_btn.click()

    print(f"Joined meeting: {meeting_team.name} > {meeting_channel.name}")

    browser.find_element_by_class_name("app-bar-selected").click()

    # Update elements to keep DOM updated
    for team in teams:
        team.update_elem()

    browser.find_element_by_class_name("call-status").click()

    active_meeting = meeting_to_join

    if 'auto_leave_after_min' in config.config and config.config['auto_leave_after_min'] > 0:
        hangup_thread = Timer(
            config.config['auto_leave_after_min'] * 60, hangup)
        hangup_thread.start()

    screenRecorder.start()

    return True


def hangup():
    try:
        hangup_btn = browser.find_element_by_css_selector(
            "button[data-tid='call-hangup']")
        hangup_btn.click()

        screenRecorder.stop()
        print("Left Meeting")

        if hangup_thread:
            hangup_thread.cancel()

        return True
    except exceptions.NoSuchElementException:
        return False


def main():
    global browser, config
    print(browser)
    window_size = browser.get_window_size()
    if window_size['width'] < 950:
        print("Resized window")
        browser.set_window_size(950, window_size['height'])

    browser.get("https://teams.microsoft.com")

    if config.config['email'] != "" and config.config['password'] != "":
        login_email = wait_until_found(browser, "input[type='email']", 30)
        if login_email is not None:
            login_email.send_keys(config.config['email'])
            time.sleep(1)

        # find the element again to avoid StaleElementReferenceException
        login_email = wait_until_found(browser, "input[type='email']", 5)
        if login_email is not None:
            login_email.send_keys(Keys.ENTER)

        login_pwd = wait_until_found(browser, "input[type='password']", 5)
        if login_pwd is not None:
            login_pwd.send_keys(config.config['password'])
            time.sleep(1)

        # find the element again to avoid StaleElementReferenceException
        login_pwd = wait_until_found(browser, "input[type='password']", 5)
        if login_pwd is not None:
            login_pwd.send_keys(Keys.ENTER)

        time.sleep(1)
        keep_logged_in = wait_until_found(browser, "input[id='idBtn_Back']", 5)
        if keep_logged_in is not None:
            keep_logged_in.click()

        time.sleep(1)
        use_web_instead = wait_until_found(browser, ".use-app-lnk", 5)
        if use_web_instead is not None:
            use_web_instead.click()

        time.sleep(1)
        teams_button = wait_until_found(browser,
                                        "button.app-bar-link > ng-include > svg.icons-teams", 5)
        if teams_button is not None:
            teams_button.click()

    # if additional organisations are setup in the config file
    if 'organisation_num' in config.config and config.config['organisation_num'] > 1:
        additional_org_num = config.config['organisation_num']
        select_change_org = wait_until_found(
            browser, "button.tenant-switcher", 20)
        if select_change_org is not None:
            select_change_org.click()

            change_org = wait_until_found(browser,
                                          f"li.tenant-option[aria-posinset='{additional_org_num}']", 20)
            if change_org is not None:
                change_org.click()
                time.sleep(5)

                use_web_instead = wait_until_found(browser, ".use-app-lnk", 5)
                if use_web_instead is not None:
                    use_web_instead.click()

                time.sleep(1)
                teams_button = wait_until_found(browser,
                                                "button.app-bar-link > ng-include > svg.icons-teams", 5)
                if teams_button is not None:
                    teams_button.click()

    print("Waiting for correct page...")
    if wait_until_found(browser, "div[data-tid='team-channel-list']", 60 * 5) is None:
        exit(1)

    teams = get_teams()
    if len(teams) == 0:
        print("Nothing found, is Teams in list mode?")
        exit(1)

    for team in teams:
        team.init_channels()
        team.check_blacklist()

    print("\nFound Teams and Channels: ")
    for team in teams:
        print(team)

    if 'start_automatically' not in config.config or not config.config['start_automatically']:
        sel_str = "\nStart [s], Reload teams [r], Quit [q]\n"

        selection = input(sel_str).lower()
        while selection != 's':
            if selection == 'q':
                browser.close()
                exit(0)
            if selection == 'r':
                config = Config()
                teams = get_teams()
                for team in teams:
                    team.init_channels()
                    team.check_blacklist()

                for team in teams:
                    print(team)

            selection = input(sel_str).lower()

    check_interval = 5
    if "check_interval" in config.config and config.config['check_interval'] > 1:
        check_interval = config.config['check_interval']

    while True:
        timestamp = datetime.now()
        print(f"\n[{timestamp:%H:%M:%S}] Updating channels")

        if active_meeting.isActive():
            update_current_meeting()
        else:
            for team in teams:
                team.update_meetings(active_meeting)

        if join_newest_meeting(teams) and not active_meeting.isActive():
            for team in teams:
                team.update_elem()

        time.sleep(check_interval)


def run():
    global active_meeting
    active_meeting = Meeting(-1, -1)

    config = Config()

    if 'run_at_time' in config.config and config.config['run_at_time'] != "":
        now = datetime.now()
        run_at = datetime.strptime(config.config['run_at_time'], "%H:%M").replace(
            year=now.year, month=now.month, day=now.day)

        if run_at.time() < now.time():
            run_at = datetime.strptime(config.config['run_at_time'], "%H:%M").replace(year=now.year, month=now.month,
                                                                                      day=now.day + 1)

        delay = (run_at - now).total_seconds()

        print(f"Waiting until {run_at} ({int(delay)}s)")
        time.sleep(delay)

    try:
        main()
    finally:
        if hangup_thread is not None:
            hangup_thread.cancel()
