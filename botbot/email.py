"""Send emails to offending users"""

import smtplib
from email.mime.text import MIMEText

from botbot.report import ReporterBase
from botbot.config import CONFIG
from botbot.problems import every_problem

class EmailReporter(ReporterBase):
    """Sends emails to people if they have bad files"""
    def __init__(self, chkr):
        super().__init__(chkr)
        self.email = CONFIG.get('email', 'email') # TODO: Add this to the config
        self.passwd = CONFIG.get('email', 'password')

    def _get_user_email_address(self, username):
        domain = CONFIG.get('email', 'domain')
        email = '{}@{}'.format(username, domain)
        return email

    def _prettify_problems(self, fi):
        return tuple()

    def write_report(self, fmt, shared, attr='owner'):
        send = SMTP(CONFIG.get('email', 'smtp_server'),
                    CONFIG.get('email', 'smtp_port'))

        send.starttls()
        send.login(self.email, self.passwd)

        for user, filelist in self.chkr.db.get_files_by_attribute(attr):
            pass
