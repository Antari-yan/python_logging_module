#!/usr/bin/env python3

"""
This is a collection of examples on how the logging module can be used.
"""

from os import path
from sys import stdin # Only for check if running in terminal
from argparse import ArgumentParser
from yaml import safe_load
import modules.log_setup

FILE_LOGGING_FILE = path.join(path.dirname(path.realpath(__file__)), 'logs/logfile.log')
SMTP_CREDENTIALS_FILE = path.join(path.dirname(path.realpath(__file__)), 'credentials.yml')
SYSLOG_ADDRESS = ""
SYSLOG_PORT = 1514


# Create Argument parser
DEFAULT_LOG_LEVEL = "info"
parser = ArgumentParser(description="")
arg_group_loglevel = parser.add_mutually_exclusive_group()
arg_group_loglevel.add_argument("-debug", "-DEBUG",action="store_true", help="Sets the Loglevel to DEBUG")
arg_group_loglevel.add_argument("-info", "-INFO", action="store_true", help="Sets the Loglevel to INFO")
arg_group_loglevel.add_argument("-warning", "-WARNING", "-warn", "-WARN", action="store_true", help="Sets the Loglevel to WARNING")
arg_group_loglevel.add_argument("-error", "-ERROR", action="store_true", help="Sets the Loglevel to ERROR")
arg_group_loglevel.add_argument("-critical", "-CRITICAL", "-crit", "-CRIT", action="store_true", help="Sets the Loglevel to CRITICAL")
arg_group_loglevel.add_argument("-utc", "-UTC", action="store_true", help="Sets the used Timezone to UTC")
args = parser.parse_args()

if args.debug:
    LOG_LEVEL = "DEBUG"
elif args.info:
    LOG_LEVEL = "INFO"
elif args.warning:
    LOG_LEVEL = "WARNING"
elif args.error:
    LOG_LEVEL = "ERROR"
elif args.critical:
    LOG_LEVEL = "CRITICAL"
else:
    LOG_LEVEL = DEFAULT_LOG_LEVEL

if args.utc:
    TIME_ZONE_STYLE = "utc"
else:
    TIME_ZONE_STYLE = "local"

def console_test():
    """
    These are some samples if you want to test the console logging functionality.
    """

    console_logger_1 = modules.log_setup.create_console_logger(name = 'console_logger_1')

    console_logger_1.debug('debug message')
    console_logger_1.info('info message')
    console_logger_1.warning('warn message')
    console_logger_1.error('error message')
    console_logger_1.critical('critical message')

    print()

    # Console output with specific log level
    console_logger_2 = modules.log_setup.create_console_logger(name = 'console_logger_2',
                                                               loglevel=LOG_LEVEL,
                                                               time_zone_style=TIME_ZONE_STYLE)

    console_logger_2.debug('debug message')
    console_logger_2.info('info message')
    console_logger_2.warning('warn message')
    console_logger_2.error('error message')
    console_logger_2.critical('critical message')

    print()

    # Console output with specific log level
    console_logger_3 = modules.log_setup.create_console_logger(name = 'console_logger_3',
                                                               loglevel='DEBUG',
                                                               time_zone_style=TIME_ZONE_STYLE)

    console_logger_3.debug('debug message')
    console_logger_3.info('info message')
    console_logger_3.warning('warn message')
    console_logger_3.error('error message')
    console_logger_3.critical('critical message')

def file_test():
    """
    This is a sample if you want to test the file logging functionality.
    """

    file_logger = modules.log_setup.create_file_logger(name = 'file_logger',
                                                       loglevel=LOG_LEVEL,
                                                       log_file=FILE_LOGGING_FILE,
                                                       time_zone_style=TIME_ZONE_STYLE)

    print (f"Logging to {FILE_LOGGING_FILE}")
    file_logger.debug('debug message')
    file_logger.info('info message')
    file_logger.warning('warn message')
    file_logger.error('error message')
    file_logger.critical('critical message')

def console_and_file_test():
    """
    This is a sample if you want to test the console and file logging functionality combined.
    """

    console_and_file_logger = modules.log_setup.create_console_logger(name = 'console_logger')
    console_and_file_logger = modules.log_setup.create_file_logger(name = 'console_logger',
                                                                   loglevel=LOG_LEVEL,
                                                                   log_file=FILE_LOGGING_FILE,
                                                                   time_zone_style=TIME_ZONE_STYLE)

    console_and_file_logger.debug('debug message')
    console_and_file_logger.info('info message')
    console_and_file_logger.warning('warn message')
    console_and_file_logger.error('error message')
    console_and_file_logger.critical('critical message')

def smtp_test():
    """
    This is a sample if you want to test the SMTP logging functionality.
    """

    creds_file = path.join(path.dirname(path.realpath(__file__)), SMTP_CREDENTIALS_FILE)
    with open(creds_file, 'r', encoding='utf-8') as file:
        smtp_logger_data = safe_load(file)

    smtp_logger, smtp_handler = modules.log_setup.create_smtp_logger(mailhost=smtp_logger_data['smtp_mailhost'],
                                                                     port=smtp_logger_data['smtp_port'],
                                                                     username=smtp_logger_data['smtp_username'],
                                                                     password=smtp_logger_data['smtp_password'],
                                                                     fromaddr=smtp_logger_data['smtp_fromaddr'],
                                                                     toaddrs=smtp_logger_data['smtp_toaddrs'],
                                                                     subject='test',
                                                                     time_zone_style=TIME_ZONE_STYLE)

    smtp_logger.info('test message')
    smtp_handler.flush()
    smtp_handler.close()

def syslog_test():
    """
    This is a sample if you want to test the SysLog logging functionality.
    """

    sys_logger = modules.log_setup.create_syslog_logger(syslog_address=SYSLOG_ADDRESS,
                                                        syslog_port=SYSLOG_PORT,
                                                        time_zone_style=TIME_ZONE_STYLE)

    sd = {'user1@host1': {'key1': 'value1', 'key2': 'value2'},
          'some@thing': {'key3': 'value3', 'key4': 'value4'}}
    extra = {'structured_data': sd}

    sys_logger.error('Message', extra=extra)

file_test()
if stdin and stdin.isatty():
    console_test()
#console_and_file_test()
#smtp_test()
#syslog_test()

# Create a 10MB file
#dd if=/dev/zero bs=10M count=1  | tr '\0' '0' > logs/logfile.log
#ls -alh logs/
