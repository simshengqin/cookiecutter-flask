import pprint
import json
import copy
from datetime import datetime


class LoggingMiddleware(object):
    def __init__(self, app):
        self.app = app
        self.framework_name = ""
        self.output = {}

    def log(self, message):
        with open("pylogging/logs/inbound_logs_" + self.framework_name + ".log", "a+") as f:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(now + " " + message)
            f.write("\n")

    def pretty_request(self, request):
        headers = ''
        for header, value in request.META.items():
            if not header.startswith('HTTP'):
                continue
            header = '-'.join([h.capitalize()
                              for h in header[5:].lower().split('_')])
            headers += '{}: {}\n'.format(header, value)

        return (
            '{method} HTTP/1.1\n'
            'Content-Length: {content_length}\n'
            'Content-Type: {content_type}\n'
            '{headers}\n\n'
            '{body}'
        ).format(
            method=request.method,
            content_length=request.META['CONTENT_LENGTH'],
            content_type=request.META['CONTENT_TYPE'],
            headers=headers,
            body=request.body,
        )

    # Flask will have a 3rd attribute response, unlike Flask
    def __call__(self, request, response=None):

        if response is None:
            self.framework_name = "django"
            response = self.app(request)
            # request.META
            # self.output["Request"] = request.META
            env = request.META
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                self.output["Source"] = request.META['HTTP_X_FORWARDED_FOR']
            else:
                self.output["Source"] = request.META['REMOTE_ADDR']
            self.output["Destination"] = request.META['HTTP_HOST']
            self.output["URL"] = "{0} {1}".format(
                env['REQUEST_METHOD'], env['PATH_INFO'])

            self.output["Response"] = {"content": response.content, "headers": request.headers, "status": str(response.status_code) + " " + response.reason_phrase
                                       # "charset": response.charset,
                                       # "status_code": response.status_code,
                                       # "reason_phrase": response.reason_phrase,
                                       # "closed": response.closed
                                       }
            self.log(pprint.pformat(self.output, sort_dicts=False))
            return response

        else:
            self.framework_name = "flask"
            # errorlog = request['wsgi.errors']
            # pprint.pprint(('REQUEST', request), stream=errorlog)
            # self.log(pprint.pformat(('REQUEST', request)), False)
            # self.log("Request : " + str(request), False)
            self.output["Source"] = "{0}:{1}".format(
                request['REMOTE_ADDR'], request['REMOTE_PORT'])
            self.output["Destination"] = "{0}:{1}".format(
                request['SERVER_NAME'], request['SERVER_PORT'])
            self.output["URL"] = "{0} {1}".format(
                request['REQUEST_METHOD'], request['PATH_INFO'])

            excluded_request_params = set(
                ["REMOTE_ADDR", "REMOTE_PORT", "SERVER_NAME", "SERVER_PORT", "REQUEST_METHOD", "PATH_INFO"])
            self.output["Request"] = {}
            for key, value in request.items():
                if key not in excluded_request_params:
                    self.output["Request"][key] = value

            def log_response(status, headers, *args):
                self.output["Response"] = {
                    "status": status, "headers": headers}
                # pprint(self.output)
                # sort_dicts=False to keep insertion order
                self.log(pprint.pformat(self.output, sort_dicts=False))
                self.output = {}
                # pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
                # self.log(pprint.pformat(
                # ('REQUEST', request, 'RESPONSE', status, headers)), False)

                # self.log("   Response : " + str(status) + " " + str(headers)True)
                return response(status, headers, *args)

            return self.app(request, log_response)