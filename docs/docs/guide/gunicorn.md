# Multi Process: Gunicorn

### What is Gunicorn?

>
> Gunicorn의 프로세스는 프로세스 기반의 처리 방식을 채택하고 있으며, 이는 내부적으로 크게 master process와 worker process로 나뉘어 집니다.    
> Gunicorn이 실행되면, 그 프로세스 자체가 master process이며, fork를 사용하여 설정에 부여된 worker 수대로 worker process가 생성 됩니다.    
> master process는 worker process를 관리하는 역할을 하고, worker process는 웹어플리케이션을 임포트하며, 요청을 받아 웹어플리케이션 코드로 전달하여 처리하도록 하는 역할을 합니다.

- Gunicorn 적용
    - Before: FastAPI 단독 실행 (Uvicorn 서버로 실행) = 1 process 로 TA 모듈 서버 구동
    - After: Gunicorn으로 FastAPI 다중 실행 (n*worker) = n+1 process (= 1*master + n*worker) 로 TA 모듈 서버 구동

### How to use Gunicorn

```bash
# 의존성 설치
(venv) pip install --extra-index-url https://download.pytorch.org/whl/cpu .[gunicorn]
# 실행
gunicorn --bind 0:8000 --max-requests 20 -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

- Gunicorn 기본 옵션 설명
    - `-w ${num_of_worker}`: request 를 처리할 app 을 지정된 워커 수 만큼 생성 미지정시 1
    - `--bind 0:8000`: `host:port` 형태로 바인딩할 소켓을 지정. 미지정시 `['127.0.0.1:8000']`
    - `-k uvicorn.workers.UvicornWorker`: fastapi 구동을 위한 설정이므로 워커 클래스는 `uvicorn`으로 고정해서 사용
    - `--max-requests 1000`: 각 워커에 해당 설정값 이상으로 요청이 몰릴 경우 다시 시작하여 메모리 누수 방지
    - 자세한 설정 옵션은 [Gunicorn 공식 문서 Settings](https://docs.gunicorn.org/en/stable/settings.html) 참고
- 커맨드로 옵션을 설정할 수 있지만 편리성을 위해 Gunicorn 설정파일인 `gunicorn.conf.py`에서 진행한다.
    - Configuration File은 `./gunicorn.conf.py`가 디폴트로 설정되어있고, 다른 경로를 설정하고 싶은 경우, `-c CONFIG` or `--config CONFIG`로 설정한다.
    - 자세한 사용법은 하단 링크 참고
        - <https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py>
        - <https://zetawiki.com/wiki/Gunicorn.conf.py>
- 주의사항
    - 요청이 올 수 있는 수준으로 최적값으로 설정하여 필요 이상으로 설정할 경우 OOM 발생
    - 공식문서를 참고하여 사용 환경에 맞는 설정 필요
