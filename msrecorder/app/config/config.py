class Config:
    def __init__(self, config_dict):
        self.config = config_dict

        self.email = self.get_property('email')
        self.password = self.get_property('password')
        self.leave_if_less_than_participants = self.get_property(
            'leave_if_less_than_participants')
        self.leave_if_last = self.get_property('leave_if_last')
        self.random_delay = self.get_property('random_delay')
        self.auto_leave_after_min = self.get_property('auto_leave_after_min')
        self.organisation_num = self.get_property('organisation_num')
        self.start_automatically = self.get_property('start_automatically')
        self.check_interval = self.get_property('check_interval')
        self.run_at_time = self.get_property('run_at_time')
        self.mute_audio = self.get_property('mute_audio')
        self.chrome_type = self.get_property('chrome_type')
        print(self.config['blacklist'])
        print('blacklist' in self.config)
        print('test')
        #TODO why get property returns None
        print(self.get_property('blacklist'))
        print('test2')
        self.blacklist = self.get_property('blacklist')

    def get_property(self, key):
        return self.config[key] if key in self.config and self.config[key] else None
