# Sample Gunicorn configuration file.
# source: https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

import json
import multiprocessing

# 해당값 수정하여 Gunicorn 설정 적용
host = "0.0.0.0"
port = "8000"
bind = f"{host}:{port}"
loglevel = "info"
errorlog = "-"
accesslog = "-"
worker_tmp_dir = "/tmp/shm"  # 해당값 수정시 gunicorn.Dockerfile도 수정해야함
graceful_timeout = 60
timeout = 60
keepalive = 5
worker_class = "uvicorn.workers.UvicornWorker"
workers_per_core_str = 1
max_workers_str = 10
web_concurrency = 4

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
# web_concurrency(workers)를 프로세스 수만큼 사용할 경우, 아래 주석 해제하여 사용
# default_web_concurrency = workers_per_core * cores
# web_concurrency = max(int(default_web_concurrency), 2)
use_max_workers = int(max_workers_str)
workers = web_concurrency

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "use_max_workers": use_max_workers,
    "host": host,
    "port": port,
}

print(json.dumps(log_data))
