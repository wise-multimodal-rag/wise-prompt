# Sample Gunicorn configuration file.
# source: https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

# from multiprocessing import cpu_count

bind = '0.0.0.0:8000'
workers = 4  # cpu_count() * 2 + 1 # 프로세서 수 *2 +1 만큼 생성하려는 경우
worker_class = 'uvicorn.workers.UvicornWorker'
threads = 1
