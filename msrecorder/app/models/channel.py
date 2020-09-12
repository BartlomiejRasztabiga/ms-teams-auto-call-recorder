class Channel:
    def __init__(self, name, meetings, blacklisted=False):
        self.name = name
        self.meetings = meetings
        self.blacklisted = blacklisted

    def __str__(self):
        return self.name + " [BLACKLISTED]" if self.blacklisted else self.name

    def get_channel_elem(self, parent):
        try:
            channel_elem = parent.find_element_by_css_selector(
                f"ul>ng-include>li[data-tid*='channel-{self.name}-li']")
        except exceptions.NoSuchElementException:
            return None

        return channel_elem