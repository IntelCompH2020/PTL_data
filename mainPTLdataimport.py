# -*- coding: utf-8 -*-
"""
Main program for importing databases for use with projects from the PTL

Created on Jul 4, 2018

@author:    Jerónimo Arenas García
            (based on code from jcid)

"""


from __future__ import print_function    # For python 2 compatibility
import os
import platform
import time


def clear():

    """Cleans terminal window
    """
    # Checks if the application is running on windows or other OS
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def query_options(options, msg=None, zero_option='exit'):
    """
    Prints a heading and the options, and returns the one selected by the user

    Args:
        options        : Complete list of options
        msg            : Heading message to be printed before the list of
                         available options
        zero_option    : If 'exit', an exit option is shown
                         If 'up', an option to go back to the previous menu
    """

    # Print the heading messsage
    if msg is None:
        print('\n')
        print('*********************')
        print('***** MAIN MENU *****')
        print('*********************')
        print('\nAvailable options:')
    else:
        print(msg)

    count = 1
    for n in range(len(options)):
        #Print active options without numbering lags
        print(' {}. '.format(count) + options[n])
        count += 1

    if zero_option == 'exit':
        print(' 0. Exit the application\n')
    elif zero_option == 'up':
        print(' 0. Back to the previous menu\n')

    range_opt = range(len(options)+1)

    opcion = None
    while opcion not in range_opt:
        opcion = input('What would you like to do? [{0}-{1}]: '.format(
            str(range_opt[0]), range_opt[-1]))
        try:
            opcion = int(opcion)
        except:
            print('Write a number')
            opcion = None

    if opcion==0:
        return opcion
    else:
        return options[opcion-1]


def request_confirmation(msg="     Are you sure?"):

    # Iterate until an admissible response is got
    r = ''
    while r not in ['yes', 'no']:
        r = input(msg + ' (yes | no): ')

    return r == 'yes'


# ################################
# Main body of application

clear()
print('***********************')
print('*** PTL data import ***')
print('***********************')

var_exit = False
time_delay = 3

# ########################
# Prepare user interaction
# ########################

# This is the complete list of level-0 options.
# The options that are shown to the user will depend on the project state
options_L0 = ['Regenerate db_Pr_FECYT',
                'Regenerate db_Pr_CORDIS',
                'Regenerate db_Pr_NSF',
                'Regenerate db_Pa_PATSTAT']


# ################
# Interaction loop
# ################

while not var_exit:

    option1 = query_options(options_L0)

    if option1 == 0:

        # Activate flag to exit the application
        var_exit = True

    elif option1 == 'Regenerate db_Pr_FECYT':

        # print("\n*** Regenerating database for FECYT projects")
        # if request_confirmation('This action will delete the existing database and regenerate if from scratch. Are you sure?'):
        #     cmd = 'python runFECYTscripts.py --resetDB'
        #     os.system(cmd)

        print('Update from the utility deactivated. This database has been generated and is stable')


    elif option1 == 'Regenerate db_Pr_CORDIS':

        # print("\n*** Regenerating database for CORDIS projects")
        # if request_confirmation('This action will delete the existing database and regenerate if from scratch. Are you sure?'):
        #     cmd = 'python runCORDISscripts.py --resetDB'
        #     os.system(cmd)

        print('Update from the utility deactivated. This database has been generated and is stable')

    elif option1 == 'Regenerate db_Pr_NSF':

        print("\n*** Regenerating database for NSF projects")
        print("*** This option is NOT IMPLEMENTED YET")

    elif option1 == 'Regenerate db_Pa_PATSTAT':

        # print("\n*** Regenerating PATENTS database")
        # if request_confirmation('This action will delete the existing database and regenerate if from scratch. Are you sure?'):
        #     cmd = 'python runPATSTATSscripts.py --resetDB'
        #     os.system(cmd)
        print('Update from the utility deactivated. This database has been generated and is stable')


    if option1 != 0:
        time.sleep(time_delay)
        #clear()
