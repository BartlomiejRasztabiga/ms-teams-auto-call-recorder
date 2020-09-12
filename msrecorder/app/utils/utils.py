from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions
from selenium.webdriver.common.by import By

from msrecorder.app.models.browser import get_browser


def wait_until_found(sel, timeout):
    browser = get_browser()

    try:
        element_present = EC.visibility_of_element_located(
            (By.CSS_SELECTOR, sel))
        WebDriverWait(browser, timeout).until(element_present)

        return browser.find_element_by_css_selector(sel)
    except exceptions.TimeoutException:
        print(f"Timeout waiting for element: {sel}")
        return None
