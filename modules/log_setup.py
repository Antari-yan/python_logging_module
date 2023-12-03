"""
This Module can be used to easily use logging in a program.
To make the logging of internal programs more consistent,
the output format like Date and Time can, but shouldn't, be changed only in the module.

In the worst case the module will always default to console output.
The only exception is when a new logger can't be created,
which makes the module exit because something broke

For usage:
-Import the Module
-Call one of the create_* functions and set it to a variable

For the future:
With more handler types, switching to file handler before switching to console output may be better.
Handler Docs: https://docs.python.org/3/library/logging.handlers.html

Pylint ignores:
# Ignoring C0301: Line too long
# Ignoring W0718: Catching too general exception
# Ignoring W0719: Raising too general exception
# Ignoring C103: PascalCase/snake_case
# Ignoring R0902: Too many instance attributes
# Ignoring R0913: Too many arguments
# Ignoring R0914: Too many local variables
"""

__version__ = '0.3.1'

from os import path as os_path, remove as os_remove, rename as os_rename
from sys import exit as sys_exit
from gzip import open as open_gzip
import logging.handlers
from smtplib import SMTP
from datetime import datetime
from time import timezone, strftime, gmtime
from re import compile as re_compile
from socket import gethostname

DEFAULT_NAME ='root'
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# To give more in-depth information, the debug loglevel returns more information
DEBUG_FORMAT = '%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - <PID %(process)d:%(processName)s> - %(module)s:%(funcName)s:%(lineno)d - %(message)s'  # pylint: disable=C0301
# Dateformat is set, so that it will always be the same
DEFAULT_DATEFMT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TIME_ZONE_STYLE = 'local'
DEFAULT_LOGLEVEL = 'INFO'

# Default Settings for File logging
DEFAULT_LOG_FILE = ''
DEFAULT_FILE_ENCODING = 'utf-8'
DEFAULT_MAX_FILE_SIZE = 10485760  # 10MB
# When a log file is >10MB a new one will be created,
# but there will never be more than 10 Log files total
DEFAULT_FILE_BACKUP_COUNT = 5

# Default Settings for SMTP logging
DEFAULT_MAIL_SERVER = ''
DEFAULT_SMTP_PORT = 587
DEFAULT_SMTP_USER = ''
DEFAULT_SMTP_PASSWORD = ''
DEFAULT_SMTP_SENDER = ''
DEFAULT_SMTP_RECIPIENT = ''
DEFAULT_SMTP_SUBJECT = ''
DEFAULT_SMTP_CAPACITY = 100

# Default Settings for SysLog logging
DEFAULT_SYSLOG_ADDRESS = ''
DEFAULT_SYSLOG_PORT = 1514

# Default coloring
DEFAULT_DEBUG_COLOR = '\x1b[34;20m'     # Blue
DEFAULT_INFO_COLOR = '\x1b[38;20m'      # Grey
DEFAULT_WARNING_COLOR = '\x1b[33;20m'   # Yellow
DEFAULT_ERROR_COLOR = '\x1b[31;20m'     # Red
DEFAULT_CRITICAL_COLOR = '\x1b[31;1m'   # Bold Red
DEFAULT_DEFAULT_COLOR = '\x1b[0m'               # White

class __rotating_file_handler_with_zipping(logging.handlers.RotatingFileHandler):   # pylint: disable=C0103
    """
    Essentially this is a RotatingFileHandler with a modified doRollover.
    Instead of doing a normal Rollover this creates zip files of old logs.
    Through this, the required space for old log files is highly reduced.
    """

    def __init__(self, filename, **kws):
        """
        Initializes a RotatingFileHandler to append it later with zipping capabilities
        """

        backupCount = kws.get('backupCount', 0) # pylint: disable=C0103
        self.backup_count = backupCount
        encoding = kws.get('encoding', DEFAULT_FILE_ENCODING)
        self.encoding = encoding
        logging.handlers.RotatingFileHandler.__init__(self, filename, **kws)

    def doArchive(self, old_log):   # pylint: disable=C0103
        """
        Write the old log file into a zip file and delete the log file
        """

        with open(old_log, encoding=self.encoding) as log:
            with open_gzip(old_log + '.gz', 'wt', encoding=self.encoding) as compressed_log:
                compressed_log.writelines(log)
        os_remove(old_log)

    def doRollover(self):
        """
        Makes Rollover for the zip compressed logs, deletes old logs and starts the zipping process
        """

        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = f"{self.baseFilename}.{i}.gz"
                dfn = f"{self.baseFilename}.{i + 1}.gz"
                if os_path.exists(sfn):
                    if os_path.exists(dfn):
                        os_remove(dfn)
                    os_rename(sfn, dfn)
        dfn = self.baseFilename + ".1"
        if os_path.exists(dfn):
            os_remove(dfn)
        if os_path.exists(self.baseFilename):
            os_rename(self.baseFilename, dfn)
            self.doArchive(dfn)
        if not self.delay:
            self.stream = self._open()

class __buffering_SMTP_handler(logging.handlers.BufferingHandler):  # pylint: disable=C0103 disable=R0902
    """
    Essentially this is a BufferingHandler extended with SMTP capabilities
    All Logs will be buffered und when flush() is used the Mail will be send
    """
    def __init__(self, mailhost, port, username, password,  # pylint: disable=R0913
                 fromaddr, toaddrs, subject, capacity, log_format):
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.mailhost = mailhost
        self.mailport = port
        self.username = username
        self.password = password
        self.fromaddr = fromaddr
        if isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.setFormatter(log_format)

    def flush(self):
        if len(self.buffer) > 0:
            try:
                smtp = SMTP(self.mailhost, self.mailport)
                smtp.starttls()
                smtp.login(self.username, self.password)
                msg = f"From: {self.fromaddr}\r\nTo: {','.join(self.toaddrs)}\r\nSubject: {self.subject}\r\n\r\n"   # pylint: disable=C0301
                for record in self.buffer:
                    s = self.format(record)
                    msg = msg + s + "\r\n"
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
                smtp.quit()
            except Exception:   # pylint: disable=W0718
                if logging.raiseExceptions:
                    raise
            self.buffer = []

class __SysLog_handler_rfc5424(logging.handlers.SysLogHandler): # pylint: disable=C0103
    """
    Essentially this is a SysLogHandler,
    but instead of the RFC3164 the RFC5424 is used.

    RFC5424 is required because, even though Graylog supports RFC3164,
    the logs aren't displayed for some reason.
    """
    tz_offset = re_compile(r'([+-]\d{2})(\d{2})$')
    escaped = re_compile(r'([\]"\\])')

    def __init__(self, *args, **kwargs):
        self.msgid = kwargs.pop('msgid', None)
        self.appname = kwargs.pop('appname', None)
        super().__init__(*args, **kwargs)

    def format(self, record):   # pylint: disable=R0914
        version = 1
        asctime = datetime.fromtimestamp(record.created).isoformat()
        m = self.tz_offset.match(strftime('%z'))
        has_offset = False
        if m and timezone:
            hrs, mins = m.groups()
            if int(hrs) or int(mins):
                has_offset = True
        if not has_offset:
            asctime += 'Z'
        else:
            asctime += f'{hrs}:{mins}'
        try:
            hostname = gethostname()
        except Exception:   # pylint: disable=W0718
            hostname = '-'
        appname = self.appname or '-'
        procid = record.process
        msgid = '-'
        msg = super().format(record)
        sdata = '-'
        if hasattr(record, 'structured_data'):
            sd = record.structured_data
            # This should be a dict where the keys are SD-ID and the value is a
            # dict mapping PARAM-NAME to PARAM-VALUE (refer to the RFC for what these
            # mean)
            # There's no error checking here - it's purely for illustration, and you
            # can adapt this code for use in production environments
            parts = []

            def replacer(m):
                g = m.groups()
                return '\\' + g[0]

            for sdid, dv in sd.items():
                part = f'[{sdid}'
                for k, v in dv.items():
                    s = str(v)
                    s = self.escaped.sub(replacer, s)
                    part += f' {k}="{s}"'
                part += ']'
                parts.append(part)
            sdata = ''.join(parts)

        return f'{version} {asctime} {hostname} {appname} {procid} {msgid} {sdata} {msg}'

class __Custom_formatter(logging.Formatter):    # pylint: disable=C0103
    """
    Colored logging formatter
    """

    def __init__(self, fmt, datefmt, time_zone, debug_color,    # pylint: disable=R0913
                 info_color, warning_color, error_color, critical_color, default_color):
        super().__init__()
        self.fmt = fmt
        self.datefmt = datefmt
        self.time_zone = time_zone
        self.FORMATS = {    # pylint: disable=C0103
            logging.DEBUG: debug_color + self.fmt + default_color,
            logging.INFO: info_color + self.fmt + default_color,
            logging.WARNING: warning_color + self.fmt + default_color,
            logging.ERROR: error_color + self.fmt + default_color,
            logging.CRITICAL: critical_color + self.fmt + default_color
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=self.datefmt)
        if self.time_zone == 'utc':
            formatter.converter = gmtime
        return formatter.format(record)

def _configure_logger(name, handler, loglevel):
    """
    Creates a logger with the given name
    Adds the given handler to the logger
    Sets the given loglevel for the logger
    """

    if name in (None, '', 'root'):
        try:
            logger = logging.getLogger()
        except Exception as e:  # pylint: disable=W0718
            print(e)
            sys_exit("Error while creating new root logger")
    else:
        try:
            logger = logging.getLogger(name)
        except Exception as e:  # pylint: disable=W0718
            print(e)
            sys_exit(f"Error while creating {name} Logger")

    logger.addHandler(handler)
    logger.setLevel(loglevel)

    return logger

def _set_timezone_style(time_zone_style):
    """
    Sets the timezone style for the logger
    """

    try:
        if str(time_zone_style).lower() == 'utc':
            set_timezone = 'utc'
        else:
            set_timezone = 'local'
    except Exception as e:  # pylint: disable=W0718
        print(e)
        print(f"Couldn't parse inputted timezone style, using default {DEFAULT_TIME_ZONE_STYLE}")
        set_timezone = DEFAULT_TIME_ZONE_STYLE

    return set_timezone

def _set_format(loglevel):
    """
    Sets the format for the logger depending on the loglevel.
    """

    if loglevel == 'DEBUG':
        log_format = DEBUG_FORMAT
    else:
        log_format = DEFAULT_FORMAT

    return log_format

def _check_loglevel(loglevel):
    """
    Checks if the inputted loglevel can be used or switches to default loglevel.
    """

    try:
        loglevel = str(loglevel).upper()
        if 'DEBUG' in loglevel:
            loglevel = 'DEBUG'
        elif 'INFO' in loglevel:
            loglevel = 'INFO'
        elif 'WARNING' in loglevel:
            loglevel = 'WARNING'
        elif 'ERROR' in loglevel:
            loglevel = 'ERROR'
        elif 'CRITICAL' in loglevel:
            loglevel = 'CRITICAL'
        else:
            raise Exception # pylint: disable=W0719
    except Exception as e:  # pylint: disable=W0718
        print(e)
        print(f"Couldn't parse inputted loglevel, using default {DEFAULT_LOGLEVEL}")
        loglevel = DEFAULT_LOGLEVEL

    return loglevel

def create_console_logger(name=DEFAULT_NAME,    # pylint: disable=R0913
                          loglevel=DEFAULT_LOGLEVEL,time_zone_style=DEFAULT_TIME_ZONE_STYLE,
                          debug_output_color=DEFAULT_DEBUG_COLOR,
                          info_output_color=DEFAULT_INFO_COLOR,
                          warning_output_color=DEFAULT_WARNING_COLOR,
                          error_output_color=DEFAULT_ERROR_COLOR,
                          critical_output_color=DEFAULT_CRITICAL_COLOR,
                          default_output_color=DEFAULT_DEFAULT_COLOR):
    """
    Creates a new logger with console output with the given name and loglevel.
    """

    loglevel = _check_loglevel(loglevel)
    log_format = _set_format(loglevel)
    time_zone_style = _set_timezone_style(time_zone_style)

    handler = logging.StreamHandler()

    handler.setFormatter(__Custom_formatter(fmt=log_format,
                                            datefmt=DEFAULT_DATEFMT,
                                            time_zone=time_zone_style,
                                            debug_color=debug_output_color,
                                            info_color=info_output_color,
                                            warning_color=warning_output_color,
                                            error_color=error_output_color,
                                            critical_color=critical_output_color,
                                            default_color=default_output_color))

    logger = _configure_logger(name, handler, loglevel)

    return logger

def create_file_logger(name="File", # pylint: disable=R0913
                        log_file=DEFAULT_LOG_FILE,
                        loglevel=DEFAULT_LOGLEVEL,
                        time_zone_style=DEFAULT_TIME_ZONE_STYLE,
                        maxBytes=DEFAULT_MAX_FILE_SIZE,         # pylint: disable=C0103
                        backupCount=DEFAULT_FILE_BACKUP_COUNT,  # pylint: disable=C0103
                        encoding=DEFAULT_FILE_ENCODING):
    """
    Creates a new Rotating File Logger extended with the capability to zip old logs,
    at the given log file location with the given name and loglevel.
    If no path is giving or it is not usable it will default to console output.
    The max log file size (maxBytes) defaults to 10485760(10MB).
    The max amount of log files (backupCount) defaults to 10.
    """

    loglevel = _check_loglevel(loglevel)
    log_format = _set_format(loglevel)
    time_zone_style = _set_timezone_style(time_zone_style)

    try:
        if log_file != '':
            if not os_path.exists(log_file):
                print("Logfile doesn't exist and will be created")
                with open(log_file, 'w', encoding=encoding):
                    pass
            handler = __rotating_file_handler_with_zipping(filename=log_file,
                                                            encoding=DEFAULT_FILE_ENCODING,
                                                            maxBytes=maxBytes,
                                                            backupCount=backupCount)
        else:
            raise Exception # pylint: disable=W0719
    except Exception as e:  # pylint: disable=W0718
        print(e)
        print("Logfile couldn't be created or given path is empty, changing to StreamHandler")
        handler = logging.StreamHandler()


    formatter = logging.Formatter(fmt=log_format, datefmt=DEFAULT_DATEFMT)
    if time_zone_style == 'utc':
        formatter.converter = gmtime
    handler.setFormatter(formatter)

    logger = _configure_logger(name, handler, loglevel)

    return logger

def create_smtp_logger(name='SMTP', # pylint: disable=R0913
                        loglevel=DEFAULT_LOGLEVEL,
                        time_zone_style=DEFAULT_TIME_ZONE_STYLE,
                        mailhost=DEFAULT_MAIL_SERVER,
                        port=DEFAULT_SMTP_PORT,
                        username=DEFAULT_SMTP_USER,
                        password=DEFAULT_SMTP_PASSWORD,
                        fromaddr=DEFAULT_SMTP_SENDER,
                        toaddrs=DEFAULT_SMTP_RECIPIENT,
                        subject=DEFAULT_SMTP_SUBJECT,
                        capacity=DEFAULT_SMTP_CAPACITY):
    """
    Creates a new logger that sends the complete log via SMTP
    important: returns Logger AND Handler
    usage:
    smtp_logger, smtp_handler = create_smtp_logger(<mail_information>)
    smtp_logger.info('info message')
    smtp_handler.flush()
    smtp_handler.close()

    hint: capacity stands for the amount of single log entries per mail
    e.g.: capacity of 10 and 80 single log messages generate 8 Mails
    the mail will only be send, when the handler is flushed

    https://docs.python.org/3/howto/logging-cookbook.html#sending-logging-messages-to-email-with-buffering
    """

    if name in (None, '', 'root'):
        print("The Name can't be empty or root for this type of logger, defaulting to name SMTP")
        name = 'SMTP'
    if not isinstance(port, int):
        try:
            port = int(port)
        except Exception as e:  # pylint: disable=W0718
            print(e)
            print("The Port has to be int, defaulting to Port 587")
            port = 587
    if not isinstance(capacity, int):
        try:
            capacity = int(capacity)
        except Exception as e:  # pylint: disable=W0718
            print(e)
            print("The Capacity has to be int, defaulting to Capacity 100")
            capacity = 100

    loglevel = _check_loglevel(loglevel)
    log_format = _set_format(loglevel)
    time_zone_style = _set_timezone_style(time_zone_style)

    log_format = logging.Formatter(fmt=log_format, datefmt=DEFAULT_DATEFMT)
    if time_zone_style == 'utc':
        log_format.converter = gmtime

    try:
        handler = __buffering_SMTP_handler(mailhost, port, username, password, fromaddr,
                                           toaddrs, subject, capacity, log_format)
    except Exception as e:  # pylint: disable=W0718
        print(e)
        print("SMTP Logger couldn't be created, changing to StreamHandler")
        handler = logging.StreamHandler()

    logger = _configure_logger(name, handler, loglevel)

    return logger, handler

def create_syslog_logger(name="SysLog",
                        loglevel=DEFAULT_LOGLEVEL,
                        time_zone_style=DEFAULT_TIME_ZONE_STYLE,
                        syslog_address=DEFAULT_SYSLOG_ADDRESS,
                        syslog_port=DEFAULT_SYSLOG_PORT):
    """
    Creates a new RFC5424 Syslog Logger for centralized logging
    Requires the target IP and Port to send the logs to.
    """

    loglevel = _check_loglevel(loglevel)
    log_format = _set_format(loglevel)
    time_zone_style = _set_timezone_style(time_zone_style)

    try:
        handler = __SysLog_handler_rfc5424(address=(syslog_address, syslog_port))
    except Exception as e:  # pylint: disable=W0718
        print(e)
        print("SysLog Address or Port are wrong or unavailable, changing to StreamHandler")
        handler = logging.StreamHandler()

    formatter = logging.Formatter(fmt=log_format, datefmt=DEFAULT_DATEFMT)
    if time_zone_style == 'utc':
        formatter.converter = gmtime
    handler.setFormatter(formatter)

    logger = _configure_logger(name, handler, loglevel)

    return logger
