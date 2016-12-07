""" Defines the jira_login function which will prompt the user at the command-
    line for credentials, log in to JIRA using the JIRA Python module, and
    returns a jira.client.JIRA instance. """

# Import common modules
from os.path import basename, dirname, join, splitext
from json import load
from getpass import getpass

# Import jira module
try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError:
    print '[ ERROR ] Unable to import jira module'
    print '    https://pypi.python.org/pypi/jira'
    print '        > pip install jira'
    print '        > easy_install jira'
    exit()

# Import requests module
try:
    from requests import packages
    packages.urllib3.disable_warnings()
except ImportError:
    print '[ ERROR ] Unable to import requests module'
    print '    https://pypi.python.org/pypi/requests'
    print '        > pip install requests'
    exit()


# Configuration file to define JIRA server information
CONFIG_FILE = join(dirname(__file__), str(splitext(basename(__file__))[0] + '.json'))


def get_user_password(user_arg, pass_arg, json_config):
    """ Prompts the user at the command-line for credentials (if none specified
        as arguments or in the JSON configuration file) """
    if user_arg is None:
        if 'user' in json_config:
            username = json_config['user']
        else:
            # Get Jira username from command-line
            print 'Enter Jira username, or leave blank for anonymous access'
            username = raw_input('Username: ').strip()
            if username.strip() == '':
                username = 'anonymous'
    else:
        username = user_arg.strip()

    if pass_arg is None:
        # Get password (for non-anonymous access)
        if username == 'anonymous':
            password = ''
        else:
            if 'password' in json_config:
                password = json_config['password']
                print '[ WARNING ] Received password from JSON file. This is a very bad idea.'
            else:
                password = getpass().strip()
    else:
        password = pass_arg.strip()

    return (username, password)


def get_jira_config(json_config):
    """ Parses the JSON configuration file data for server and verify keys
        Returns a dict of those two key/value pairs """

    if 'server' not in json_config:
        raise ValueError('Missing "server" key in JSON configuration file')
    if 'verify' not in json_config:
        raise ValueError('Missing "verify" key in JSON configuration file')

    return {'server' : json_config['server'], 'verify' : json_config['verify']}


def jira_login(user_arg=None, pass_arg=None):
    """ Logs in to the JIRA server
        returns an instance of jira.client.JIRA """

    with open(CONFIG_FILE, 'r') as handle:
        json_config = load(handle)

    jira_config = get_jira_config(json_config)
    username, password = get_user_password(user_arg, pass_arg, json_config)

    # Log in to Jira using the specified credentials
    try:
        if username == 'anonymous':
            jira_server = JIRA(jira_config)
        else:
            jira_server = JIRA(jira_config, basic_auth=(username, password))
    except JIRAError as error:
        print '[ ERROR ] Error logging in to Jira, %s' % str(error.status_code)
        print error.response
        exit()
    if username == 'anonymous':
        print 'Anonymous login successful'
    else:
        print 'Login successful as %s' % username
    print ''

    return jira_server
