"""
Contains some general purpose functions
"""
import os
import platform

def clear():
    """Cleans terminal window
    """
    # Checks if the application is running on windows or other OS
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def request_confirmation(msg="     Are you sure?"):
    """As the user for confirmation using keyboard
    Returns True / False
    """

    # Iterate until an admissible response is got
    r = ''
    while r not in ['yes', 'no']:
        r = input(msg + ' (yes | no): ')

    return r == 'yes'
