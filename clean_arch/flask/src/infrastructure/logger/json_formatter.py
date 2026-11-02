import datetime
import json
import logging

from flask import has_request_context, request


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.UTC
            ).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "request_id": None,
            "user_id": None,
        }

        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        if has_request_context():
            if hasattr(request, "request_id"):
                log_data["request_id"] = request.request_id

            from flask import g

            if hasattr(g, "user_id"):
                log_data["user_id"] = g.user_id

            log_data["path"] = request.path
            log_data["method"] = request.method

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)
