"""Send emails to offending users"""

import smtplib
from email.mime.text import MIMEText

from botbot import report
from botbot.config import CONFIG
from botbot.problems import every_problem

from jinja2 import Environment, FileSystemLoader

_EMAIL_TEMPLATE_NAME = 'email.txt'
_EMAIL_SUBJECT_LINE = 'Issues in MSI shared folder'

def _get_user_email_address(username):
    """Construct an email address from an MSI username"""
    domain = CONFIG.get('email', 'domain')
    email = '{}@{}'.format(str(username), str(domain))
    return email

class EmailReporter(report.ReporterBase):
    """Sends emails to people if they have bad files"""
    def __init__(self, chkr, smtpprovider=smtplib.SMTP):
        super().__init__(chkr)
        self.email = CONFIG.get('email', 'email') # TODO: Add this to the config
        self.passwd = CONFIG.get('email', 'password')
        self.smtpprovider = smtpprovider # Object that sends emails (can be test dummy)

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
        return [
            {
                'message': ep[prob].message,
                'fix': ep[prob].fix,
                'paths': [p['path'] for p in fis if prob in p['problems']]
            }
            for prob in pp
        ]
        # Wonderful, innit

    def write_report(self, fmt, shared, attr='username'):
        """Send an email to everyone."""
        send = self.smtpprovider(CONFIG.get('email', 'smtp_server'),
                                 CONFIG.get('email', 'smtp_port'))

        send.starttls()
        send.login(self.email, self.passwd)
        allfiles = self.chkr.db.get_files_by_attribute(self.chkr.path, attr)

        env = self._get_env(_EMAIL_TEMPLATE_NAME)

        for user in allfiles:
            prettylist = self._prettify_problems(allfiles[user])

            if prettylist:
                msgcontent = env.get_template(_EMAIL_TEMPLATE_NAME).render(filelist=prettylist)

                msg = MIMEText(msgcontent)
                msg['To'] = _get_user_email_address(user)
                msg['From'] = self.email
                msg['Subject'] = _EMAIL_SUBJECT_LINE
                send.send_message(msg)

        send.quit()

class DummySMTP:
    """
    A dummy email client that's used for testing. It only prints email
    content to the stdout. That's it.
    """
    def __init__(self, server, port):
        pass

    def starttls(self):
        """For compatibility. Does nothing."""
        pass

    def login(self, email, passwd):
        """For compatibility. Does nothing."""
        pass

    def send_message(self, msg):
        """"""
        print(msg)

    def quit(self):
        """For compatibility. Does nothing."""
        pass
