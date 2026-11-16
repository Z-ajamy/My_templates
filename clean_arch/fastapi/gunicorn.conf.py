import multiprocessing
import os

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1

# النوع الإجباري الوحيد المسموح به مع FastAPI
worker_class = "uvicorn.workers.UvicornWorker"


max_requests = 1000
max_requests_jitter = 50

timeout = 120
keepalive = 5
graceful_timeout = 30


accesslog = "-" 
errorlog = "-"
loglevel = "info"


# ==========================================
# 6. بيئة التشغيل والإضافات (Environment & Hooks)
# ==========================================
# إذا كان التطبيق خلف Load Balancer أو Nginx (لضمان الحصول على الـ IP الحقيقي للعميل)
forwarded_allow_ips = "*"
proxy_allow_ips = "*"

# دوال اعتراضية (Hooks) تُنفذ قبل بدء العامل أو بعد انتهائه.
def on_starting(server):
    print("🚀 Gunicorn Master is starting the FastAPI application...")

def worker_exit(server, worker):
    print(f"🛑 Worker {worker.pid} has exited.")



import logging
from pythonjsonlogger import jsonlogger
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "gunicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "gunicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
}

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
