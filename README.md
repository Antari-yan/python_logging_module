# Python logging module
This python module `modules/log_setup.py` appends the default logging module with additional capabilities.

- Predefined logging format for debug and all other formats
- Colorized logging output for command line
- Buffered SMTP logging
- Rotating File logging with zipping capability (requires gzip)
- [RFC5424](https://datatracker.ietf.org/doc/rfc5424/) Syslog logging


## Usage
To give a proper overview in how the module can be used, `usage_sample.py` contains examples for each logging handlers available.  
``` sh
# Show all script options
python3 usage_sample.py
```
`-h` or `--help` can be used to show all options of the example script.

Creating multiple logger (e.g. file and console) with the same name (same variable and logger name) will result that both logger will be assigned.
This way it is possible to do multiple logging formats at the same time.

To test the `SMTP logger` fill out the variables in `credentials_sample.yml` and uncomment `smtp_test()` at the end.
To test the `Syslog logger` set the variable `syslog_address` and optionally `syslog_port` and uncomment `syslog_test()` at the end.
