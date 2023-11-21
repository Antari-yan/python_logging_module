#!/usr/bin/env python3

from os import path
from sys import stdin # Only for check if running in terminal
from argparse import ArgumentParser
from yaml import safe_load
import modules.log_setup

file_logging_file = path.join(path.dirname(path.realpath(__file__)), 'logs/logfile.log')
#smtp_credentials_file = path.join(path.dirname(path.realpath(__file__)), 'credentials_sample.yml')
smtp_credentials_file = path.join(path.dirname(path.realpath(__file__)), 'credentials.yml')
syslog_address = ""
syslog_port = 1514


# Create Argument parser
default_log_level = "info"
parser = ArgumentParser(description="")
arg_group_loglevel = parser.add_mutually_exclusive_group()
arg_group_loglevel.add_argument("-debug", "-DEBUG", action="store_true", help="Sets the Loglevel to DEBUG")
arg_group_loglevel.add_argument("-info", "-INFO", action="store_true", help="Sets the Loglevel to INFO")
arg_group_loglevel.add_argument("-warning", "-WARNING", "-warn", "-WARN", action="store_true", help="Sets the Loglevel to WARNING")
arg_group_loglevel.add_argument("-error", "-ERROR", action="store_true", help="Sets the Loglevel to ERROR")
arg_group_loglevel.add_argument("-critical", "-CRITICAL", "-crit", "-CRIT", action="store_true", help="Sets the Loglevel to CRITICAL")
args = parser.parse_args()

if args.debug:
    log_level = "DEBUG"
elif args.info:
    log_level = "INFO"
elif args.warning:
    log_level = "WARNING"
elif args.error:
    log_level = "ERROR"
elif args.critical:
    log_level = "CRITICAL"
else:
    log_level = default_log_level


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
    console_logger_2 = modules.log_setup.create_console_logger(name = 'console_logger_2', loglevel=log_level)

    console_logger_2.debug('debug message')
    console_logger_2.info('info message')
    console_logger_2.warning('warn message')
    console_logger_2.error('error message')
    console_logger_2.critical('critical message')

    print()

    # Console output with specific log level
    console_logger_3 = modules.log_setup.create_console_logger(name = 'console_logger_3', loglevel='DEBUG')

    console_logger_3.debug('debug message')
    console_logger_3.info('info message')
    console_logger_3.warning('warn message')
    console_logger_3.error('error message')
    console_logger_3.critical('critical message')

    return None

def file_test():
    """
    This is a sample if you want to test the file logging functionality.
    """

    file_logger = modules.log_setup.create_file_logger(name = 'file_logger', loglevel=log_level, log_file=file_logging_file)

    print (f"Logging to {file_logging_file}")
    file_logger.debug('debug message')
    file_logger.info('info message')
    file_logger.warning('warn message')
    file_logger.error('error message')
    file_logger.critical('critical message')

    return None

def console_and_file_test():
    """
    This is a sample if you want to test the console and file logging functionality combined.
    """

    console_and_file_logger = modules.log_setup.create_console_logger(name = 'console_logger')
    console_and_file_logger = modules.log_setup.create_file_logger(name = 'console_logger', loglevel=log_level, log_file=file_logging_file)

    console_and_file_logger.debug('debug message')
    console_and_file_logger.info('info message')
    console_and_file_logger.warning('warn message')
    console_and_file_logger.error('error message')
    console_and_file_logger.critical('critical message')

    return None

def smtp_test():
    """
    This is a sample if you want to test the SMTP logging functionality.
    """

    creds_file = path.join(path.dirname(path.realpath(__file__)), smtp_credentials_file)
    with open(creds_file, 'r') as file:
        smtp_logger_data = safe_load(file)

    smtp_logger, smtp_handler = modules.log_setup.create_smtp_logger(mailhost=smtp_logger_data['smtp_mailhost'],
                                                                        port=smtp_logger_data['smtp_port'],
                                                                        username=smtp_logger_data['smtp_username'],
                                                                        password=smtp_logger_data['smtp_password'],
                                                                        fromaddr=smtp_logger_data['smtp_fromaddr'],
                                                                        toaddrs=smtp_logger_data['smtp_toaddrs'],
                                                                        subject='test')

    smtp_logger.info('test message')
    smtp_handler.flush()
    smtp_handler.close()

    return None

def syslog_test():
    """
    This is a sample if you want to test the SysLog logging functionality.
    """

    sys_logger = modules.log_setup.create_syslog_logger(syslog_address=syslog_address, syslog_port=syslog_port)

    sd = {'foo@12345': {'bar': 'baz', 'baz': 'bozz'},'foo@54321': {'rab': 'baz', 'zab': 'bozz'}}
    extra = {'structured_data': sd}

    sys_logger.error('Message', extra=extra)

    return None

file_test()
console_test()
console_and_file_test()
#smtp_test()
#syslog_test()


#if sys.stdin and sys.stdin.isatty():
#    console_test()

#dd if=/dev/zero bs=10M count=1  | tr '\0' '0' > logs/logfile.log
#ls -alh logs/
