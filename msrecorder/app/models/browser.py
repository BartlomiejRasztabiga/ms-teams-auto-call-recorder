from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from msrecorder.app.config.config_service import ConfigService


def get_browser():
    browser: webdriver.Chrome = None

    config = ConfigService.get_instance().config

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-edrrors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])

    if 'mute_audio' in config and config['mute_audio']:
        chrome_options.add_argument("--mute-audio")

    chrome_type = ChromeType.GOOGLE
    if 'chrome_type' in config:
        if config['chrome_type'] == "chromium":
            chrome_type = ChromeType.CHROMIUM
        elif config['chrome_type'] == "msedge":
            chrome_type = ChromeType.MSEDGE

    browser = webdriver.Chrome(ChromeDriverManager(
        chrome_type=chrome_type).install(), options=chrome_options)

    return browser
