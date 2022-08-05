import logging
from logging import handlers
import sys    
import requests
import textwrap
# Request with session----------------------------------------------
# for calling using request.Session().get()



# def setup_logging_session(response, *args, **kwargs):
#     extra = {'req': response.request, 'res': response}
#     root.debug('HTTP roundtrip', extra=extra)
    

# class HttpFormatter(logging.Formatter):

#     def _formatHeaders(self, d):
#         return '\n'.join(f'{k}: {v}' for k, v in d.items())

#     def formatMessage(self, record):
#         result = super().formatMessage(record)
#         if record.name == 'httplogger':
#             result += textwrap.dedent('''
#                 ---------------- request ----------------
#                 {req.method} {req.url}
#                 {reqhdrs}

#                 {req.body}
#                 ---------------- response ----------------
#                 {res.status_code} {res.reason} {res.url}
#                 {reshdrs}

#                 {res.text}
#             ''').format(
#                 req=record.req,
#                 res=record.res,
#                 reqhdrs=self._formatHeaders(record.req.headers),
#                 reshdrs=self._formatHeaders(record.res.headers),
#             )

#         return result


# root = logging.getLogger('httplogger')
# formatter = HttpFormatter('{asctime} {levelname} {name} {message}', style='{')
# handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(formatter)
# root.addHandler(handler)
# root.setLevel(logging.DEBUG)

# Request without session----------------------------------------------
# for calling using request.get()
import http.client
# import logging
import os.path
# import sys
from logging.handlers import TimedRotatingFileHandler

def print_to_log(*args):
    # monkey-patch a `print` global into the http.client module; all calls to
    # print() in that module will then use our print_to_log implementation
    http_client_logger = logging.getLogger("http.client")
    http_client_logger.debug(" ".join(args)) 


def setup_outbound_logging(framework_name = "", loglevel = logging.DEBUG):
    http.client.print = print_to_log
    if framework_name != "":
        framework_name = "_"+ framework_name
    # the file handler receives all messages from level DEBUG on up, regardless
    fileHandler = TimedRotatingFileHandler(
        "pylogging/logs/outbound_logs" + framework_name + ".log",
        when="midnight"
    )
    fileHandler.setLevel(logging.DEBUG)
    handlers = [fileHandler]
    # if loglevel is not None:
        # if a log level is configured, use that for logging to the console
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setLevel(logging.DEBUG)
    # handlers.append(stream_handler)

    # if loglevel == logging.DEBUG:
        # when logging at debug level, make http.client extra chatty too
        # http.client *uses `print()` calls*, not logging.
    http.client.HTTPConnection.debuglevel = 1

    # finally, configure the root logger with our choice of handlers
    # the logging level of the root set to DEBUG (defaults to WARNING otherwise).
    logformat = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    fileHandler.setFormatter(logging.Formatter(logformat))
    # stream_handler.setFormatter(logging.Formatter(logformat))
    root = logging.getLogger('http.client')
    root.addHandler(fileHandler)
    # root.addHandler(stream_handler)
    root.setLevel(logging.DEBUG)

    logging.basicConfig(
        format=logformat, datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers, level=logging.DEBUG
    )

