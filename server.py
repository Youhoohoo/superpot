#!/usr/bin/env python
# encoding: utf-8

from icspot import *
import gevent.monkey
import gevent

gevent.monkey.patch_all()

logger = logging.getLogger()
logfile = '/var/log/superpot.log'

def setup_logging(log_file, verbose):
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    log_format = logging.Formatter('%(asctime)-15s %(message)s')
    console_log = logging.StreamHandler()
    console_log.setLevel(log_level)
    console_log.setFormatter(log_format)

    logger.setLevel(log_level)
    file_log = logging.FileHandler(log_file)
    file_log.setFormatter(log_format)
    file_log.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_log)
    root_logger.addHandler(file_log)

port_list = [102]


if __name__ == '__main__':
	setup_logging(logfile, False)
	event = []
	for port in port_list:
		event.append(gevent.spawn(init_server, port))

	gevent.joinall(event)

'''

	gevent.joinall([
        gevent.spawn(init_server, 102),
        gevent.spawn(init_server, 502),
        gevent.spawn(init_server, 2404),
	])


'''

