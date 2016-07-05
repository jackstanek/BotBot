"""Send emails to offending users"""

import smtplib
from email.mime.text import MIMEText

from botbot.report import ReporterBase
from botbot.config import CONFIG
from botbot.problems import every_problem

from jinja2 import Environment

class EmailReporter(ReporterBase):
    """Sends emails to people if they have bad files"""
    def __init__(self, chkr, smtpprovider=smtplib.SMTP):
        super().__init__(chkr)
        self.email = CONFIG.get('email', 'email') # TODO: Add this to the config
        self.passwd = CONFIG.get('email', 'password')
        self.smtpprovider = smtpprovider # Object that sends emails (can be test dummy)

    def _get_user_email_address(self, username):
        """Construct an email address from an MSI username"""
        domain = CONFIG.get('email', 'domain')
        email = '{}@{}'.format(username, domain)
        return email

    def _prettify_problems(self, fis):
        """
        Get a list of tuples of the problem description, solution, and
        list of paths
        """
        # Get a list of problems that are present in the file list
        pp = set.union(*[p['problems'] for p in fis]) # present problems

        # Alias for the problem description dictionary
        ep = every_problem

        # Ugly list comprehension coming up
        return [(ep[prob].message, ep[prob].fix,
                 [p['path'] for p in fis if prob in p['problems']])
                for prob in pp]
        # Wonderful, innit

    def write_report(self, fmt, shared, attr='owner'):
        """Send an email to every"""
        send = self.smtpprovider(CONFIG.get('email', 'smtp_server'),
                                 CONFIG.get('email', 'smtp_port'))

        send.starttls()
        send.login(self.email, self.passwd)
        allfiles = self.chkr.db.get_files_by_attribute(attr)

        for user in allfiles:
            filelist = allfiles[user]
            prettylist = self._prettify_problems(filelist)

            env = self._get_template()
            msgcontent = env.
