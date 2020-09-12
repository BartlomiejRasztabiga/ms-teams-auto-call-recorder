import time
import re

from selenium.common import exceptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from msrecorder.app.models.channel import Channel
from msrecorder.app.config.config import Config
from msrecorder.app.models.browser import get_browser
from msrecorder.app.utils.utils import wait_until_found


config = Config()
browser: webdriver.Chrome = get_browser()
uuid_regex = r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b"


class Team:
    def __init__(self, name, elem, index, channels=None):
        if channels is None:
            channels = []
        self.name = name
        self.elem = elem
        self.index = index
        self.channels = channels

    def __str__(self):
        channel_string = '\n\t'.join([str(channel)
                                      for channel in self.channels])

        return f"{self.name}\n\t{channel_string}"

    def expand_channels(self):
        channels_div_css_selector = "div.channels"

        try:
            elem = self.elem.find_element_by_css_selector(
                channels_div_css_selector)
        except exceptions.NoSuchElementException:
            try:
                self.elem.click()
                elem = self.elem.find_element_by_css_selector(
                    channels_div_css_selector)
            except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException):
                return None
        return elem

    def init_channels(self):
        channels_elem = self.expand_channels()

        channel_elems = channels_elem.find_elements_by_css_selector(
            "ul>ng-include>li")

        channel_names = [channel_elem.get_attribute(
            "data-tid") for channel_elem in channel_elems]
        channel_names = [channel_name[channel_name.find('-channel-') + 9:channel_name.rfind("-li")] for channel_name
                         in
                         channel_names if channel_name is not None]

        self.channels = [Channel(channel_name, [])
                         for channel_name in channel_names]

    def check_blacklist(self):
        blacklist = config.config['blacklist']
        blacklist_item = next(
            (team for team in blacklist if team['team_name'] == self.name), None)
        if blacklist_item is None:
            return

        if len(blacklist_item['channel_names']) == 0:
            for channel in self.channels:
                channel.blacklisted = True
        else:
            blacklist_channels = [
                x for x in self.channels if x.name in blacklist_item['channel_names']]
            for blacklist_channel in blacklist_channels:
                blacklist_channel.blacklisted = True

    def update_meetings(self):
        channels = self.expand_channels()

        for channel in self.channels:
            if channel.blacklisted:
                continue

            channel_elem = channel.get_channel_elem(channels)
            try:
                active_meeting_elem = channel_elem.find_element_by_css_selector(
                    "a>active-calls-counter[is-meeting='true']")
            except exceptions.NoSuchElementException:
                continue

            active_meeting_elem.click()

            if wait_until_found(
                    "button[ng-click='ctrl.joinCall()']", 60) is None:
                continue

            join_meeting_elems = browser.find_elements_by_css_selector(
                "button[ng-click='ctrl.joinCall()']")

            meeting_ids = []
            for join_meeting_elem in join_meeting_elems:
                try:
                    uuid = re.search(
                        uuid_regex, join_meeting_elem.get_attribute('track-data'))
                    if uuid is None:
                        continue

                    meeting_ids.append(uuid.group(0))
                except exceptions.StaleElementReferenceException:
                    continue

            # remove duplicates
            meeting_ids = list(dict.fromkeys(meeting_ids))

            time.sleep(1)
            all_call_elems = browser.find_elements_by_css_selector(
                ".ts-calling-thread-header")

            for meeting_id in meeting_ids:
                # if the meeting is active or new, do some more things
                if meeting_id not in [meeting.meeting_id for meeting in
                                      channel.meetings] or meeting_id == active_meeting.meeting_id:
                    time_started = time.time()

                    # search the corresponding header elem and extract the time
                    for call_elem in all_call_elems:
                        try:
                            call_elem.find_element_by_css_selector(
                                f"calling-join-button > button[track-data*='{meeting_id}'] ")
                        except exceptions.NoSuchElementException:
                            continue
                        else:
                            header_id = call_elem.get_attribute("id")
                            if header_id is not None:
                                time_started = int(
                                    header_id.replace("m", "")[:-3])
                                break

                    if meeting_id != active_meeting.meeting_id:
                        channel.meetings.append(
                            Meeting(time_started, meeting_id))

    def update_elem(self):
        team_elems = browser.find_elements_by_css_selector(
            "ul>li[role='treeitem']>div[sv-element]")
        self.elem = team_elems[self.index]
