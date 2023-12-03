# Python logging module extension
This python module `modules/log_setup.py` extends the default logging module with additional capabilities.
Besides the module script all other used modules should be available in python3 by default.

- Predefined logging format for debug and all other formats
- Colorized logging output for command line
- Buffered SMTP logging
    - Sends one e-mail that contains all logging massages
- Rotating File logging with zipping capability (requires gzip)
    - Rotates after a set file size (default 10MB) and zips the old log files
- [RFC5424](https://datatracker.ietf.org/doc/rfc5424/) Syslog logging
    - Makes Syslog logging fully compatible with RFC5424 
- Switch between local time and utc

## Setup
To run `usage_sample.py` the `pyyaml` packages is required
``` sh
pip install -r requirements.txt
```

## Usage
To give a proper overview in how the module can be used, `usage_sample.py` contains examples for each logging handlers available.  
``` sh
# Show all script options
python3 usage_sample.py
```
`-h` or `--help` can be used to show all options of the example script.

Creating multiple logger (e.g. file and console) with the same name (same variable and logger name) will result that both logger will be assigned.
This way it is possible to do multiple logging formats at the same time.

To test the `SMTP logger` create a file named `credentials.yml`, fill it out similar to `credentials_sample.yml` and uncomment `smtp_test()` at the end.
To test the `Syslog logger` set the variable `syslog_address` and optionally `syslog_port` and uncomment `syslog_test()` at the end.

## ToDo before first version release
- Proper stating of min python version requirement
- ci/cd
    - automated Linting
    - automated function checks
- Default values shown in Docstring or something similar
