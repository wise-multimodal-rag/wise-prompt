# Docker

## Docker Buildkit

Docker 이미지를 빌드하기 위한 도구로, 기존 Docker 빌드 프로세스보다 더 빠르고 효율적이며 유연합니다. (Docker Desktop 및 Docker Engine 버전 23.0부터 기본 빌더)

1. 병렬 빌드
    - 기존 Docker 빌드는 단계적으로 실행되어 각 단계가 끝날 때까지 기다려야 했습니다.
    - BuildKit은 여러 단계(레이어)를 동시에 실행할 수 있어 빌드 속도가 크게 향상됩니다.
2. 캐시 최적화
    - BuildKit은 빌드 과정에서 발생하는 중복 작업을 최소화하여 효율적으로 캐시를 사용합니다.
    - 이를 통해 변경되지 않은 부분은 다시 빌드하지 않아 시간을 절약할 수 있습니다.
3. 시크릿과 SSH 키 관리
    - Dockerfile에서 민감한 정보(예: API 키, SSH 키)를 안전하게 전달할 수 있습니다.
    - 기존 방식에서는 이를 안전하게 처리하기 어려웠습니다.
4. 더 나은 에러 메시지와 디버깅 지원
    - 빌드 오류 발생 시 더 직관적이고 상세한 에러 메시지를 제공하여 문제를 쉽게 해결할 수 있습니다.
5. 멀티 플랫폼 빌드 지원
    - 단일 명령으로 여러 플랫폼(예: Linux, Windows)의 이미지를 동시에 빌드할 수 있습니다.
    - 예: docker buildx 명령어를 통해 ARM 및 x86 이미지를 동시에 생성 가능.

> 위 설명은 ChatGPT로부터 생성한 답변을 기반으로 작성되었습니다.

- 참고
    - <https://docs.docker.com/build/buildkit/>
    - <https://github.com/moby/buildkit>

### 설치 방법

```shell
$ apt-get update && apt-get install -y docker-buildx-plugin
$ docker buildx version
github.com/docker/buildx v0.17.1 257815a
```

### 사용법

```shell
docker buildx build ... 
or 
DOCKER_BUILDKIT=1 docker build ... 
```

## FAQ

**Q1. Docker Buildkit을 굳이 써야하나요? 기본 도커만으로도 충분히 사용할 수 있는걸요!**

이미 위에서 성능, 스토리지 관리, 확장성 측면에서 장점을 충분히 설명했습니다.    
또한 `docker build`를 실행하면 아래와 같은 주의사항이 뜹니다.

```bash
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/
```

Docker에서도 Buildkit을 기본으로 가져가려는 움직임이 보입니다. 시간이 지나면 선택이 아닌 필수가 될 것입니다.