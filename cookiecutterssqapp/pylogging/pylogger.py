from pylogging.inbound_logger import LoggingMiddleware
from pylogging.outbound_logger import setup_outbound_logging  # , setup_logging_session
from pylogging.file_logger import setup_file_logging, close_file_logging 
import os

def create_logs_dir():
    '''
    Create logs directory if it doesn't exist
    '''
    path = os.path.join(os.getcwd(), "pylogging/logs")
    if not os.path.exists(path):
        os.makedirs(path)

def setup_logging_and_run_flask(path, app, *args, **kwargs):
    '''
    Setup inbound, outbound and file logging, then run app Inputs: 
    - path (path to look for file changes recursively)
    - app (flask app)
    - any other arguments that flask's app.run() normally accepts
    '''
    create_logs_dir()
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    setup_outbound_logging("flask")
    setup_file_logging()
    try:
        app.run(*args, **kwargs)
    finally:
        close_file_logging()

def setup_logging_and_run_django(path, main):
    '''
    Setup inbound, outbound and file logging, then run app
    Inputs: 
    - path (path to look for file changes recursively)
    - main (django main function)
    '''
    create_logs_dir()
    setup_outbound_logging("django")
    watcher_thread = setup_file_logging(path, "django")
    main()
    watcher_thread.join()   
