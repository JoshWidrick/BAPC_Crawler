import configparser


class Config:

    # filename for config file
    CONFIG_FILE_NAME = 'config.ini'
    # config object
    config = None
    # all necessary reddit user inputs
    reddit_options = ['user_agent', 'client_id', 'client_secret', 'username', 'password']
    # all necessary mail server api user inputs
    api_options = ['api_url', 'api_key', 'mailgun_domain', 'email_address', 'emails_subject']

    def __init__(self):
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.read(self.CONFIG_FILE_NAME)
        # Run checks to see if info is available, prompt if not
        self.config_check_reddit()

    def config_check_reddit(self):
        if 'reddit' not in self.config:
            self.config.add_section('reddit')
        self.run_input_options('reddit', self.reddit_options)

    def config_check_api(self):
        if 'api' not in self.config:
            self.config.add_section('api')
        self.run_input_options('api', self.api_options)

    def run_input_options(self, name, options):
        for o in options:
            if not self.config.has_option(name, o):
                scratch = input(f"Enter {o.replace('_', ' ').title()}: ")
                self.config.set(name, o, scratch)
                self.write_file()

    def write_file(self):
        cfgfile = open(self.CONFIG_FILE_NAME, 'w')
        self.config.write(cfgfile)
        cfgfile.close()

    def get_option(self, section, option):
        return self.config.get(section, option)
