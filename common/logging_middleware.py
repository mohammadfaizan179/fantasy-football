import logging
import os


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        url_name = request.resolver_match.url_name

        # Create a log file for each endpoint
        log_file = os.path.join('logs', f'{url_name}.log')

        # Create a logger for this endpoint
        logger = logging.getLogger(url_name)

        # Set the logger level to DEBUG
        logger.setLevel(logging.DEBUG)

        # Check if a handler already exists to avoid duplicate handlers
        if not logger.handlers:
            # Create a file handler
            handler = logging.FileHandler(log_file)

            # Set the log level
            handler.setLevel(logging.DEBUG)

            # Set the formatter
            formatter = logging.Formatter('{levelname} {asctime} {module} {message}', style='{')
            handler.setFormatter(formatter)

            logger.addHandler(handler)

        # Attach the logger to the request object for use in views
        request.logger = logger
