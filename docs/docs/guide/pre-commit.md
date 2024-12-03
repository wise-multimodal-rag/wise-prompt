# Pre-commit

> 커밋 전 코드체크 자동화를 도와주는 프레임워크
>
> 코드 저장소에 commit을 수행하기 전에 포맷팅이나 린팅이 잘 되어 있는지 확인하는 도구
>

참고: <https://pre-commit.com/>

## Purpose

- 모든 커밋 전에 실행하여 문법 오류나 스타일, 정렬, 타입 오류와 같은 코드의 문제를 **자동으로** 지적해준다.
- 코드를 검토하기 전에 문제를 지적함으로써 코드 검토자는 사소한 스타일을 신경쓰는데 **시간을 낭비하지 않고** 아키텍처에 집중할 수 있다.
- 협업자들끼리 **공통된 규약**을 따를 수 있다.

## Description

- pre-commit은 기본적으로 `.pre-commit-config.yaml` 파일의 설정을 참고한다.
- pre-commit을 진행하기 위한 테스트들(ex. ruff, pyright)은 `pyproject.toml` 파일의 설정을 참고한다.
- 현재는 GitLab CI/CD의 secret-detection, lint stage인 _secret-detection_, _ruff_, _pyright_ 총 3가지 job을 수행한다.

## Requirements

```shell
# pip 방식으로 설치
pip install pre-commit
# poetry 방식으로 설치
poetry add --group lint pre-commit

# version check
pre-commit --v
```

## Getting started

실제로 실행하기 위해서는 아래와 같은 명령어를 수행하면 된다.

```shell
# 아래 명령어로 pre-commit 훅을 활성화합니다.
# 커밋이 될 때마다 위에서 설정한 파일이 pre-commit 단계에서 실행되도록 명령어를 입력한다.
# 필수 단계로 해당 작업을 진행하지 않을 경우, pre-commit 실행이 되지 않는다.
pre-commit install

# 이제 pre-commit이 적용되어 커밋을 할때마다 자동으로 pre-commit을 실행한다.
# 만약 pre-commit을 직접 실행하고 싶으면 아래와 같은 명령어를 수행한다.
pre-commit run
# 커밋 기록에 따른게 아닌 모든 파일을 점검하고 싶으면 --all-files 옵션을 추가한다.
pre-commit run --all-files
```

해당 설정을 마무리하면 PyCharm에서 commit을 진행할 때 pre-commit 테스트를 통과하지 않으면 아래 캡쳐화면과 같이 에러가 뜨는 것을 확인할 수 있다.

- pre-commit 실패    
  ![pre commit failed](../images/pre-commit-failed.png "pre commit failed")
- pre-commit 실패 로그 확인    
  ![pre commit failed console log](../images/pre-commit-failed-console-log.png "pre commit failed console log")

### Extras

`.pre-commit-config.yaml` 파일이 수정되면 아래 명령어를 수행해야 한다.

```shell
git add .pre-commit-config.yaml
```

yaml 파일의 rev 버전을 최신으로 업데이트하기 위해서는 아래 명령어를 사용하면 된다.

```shell
pre-commit autoupdate
```

pre-commit을 비활성화하고 싶을 경우, 3가지 방법이 있다.

1. **`.git/hooks/pre-commit` 파일 삭제하기**    
   pre-commit이 설치되면 `.git/hooks/pre-commit`에 스크립트가 생성됩니다.    
   이 파일을 삭제하거나 이름을 변경하면 pre-commit이 실행되지 않게 됩니다.
    ```shell
    rm .git/hooks/pre-commit
    ```
2. **`pre-commit-config.yaml` 파일 수정**    
   프로젝트의 루트 디렉토리에 있는 `.pre-commit-config.yaml` 파일에서 특정 hook을 비활성화할 수 있습니다.    
   필요하지 않은 hook을 주석 처리하거나 삭제해보세요.
3. **pre-commit 비활성화 명령어 사용**    
   pre-commit 자체를 일시적으로 비활성화하려면 다음 명령어를 사용할 수 있습니다.
    ```shell
    pre-commit uninstall
    ```

## FAQ

**Q1. 그럼 GitLab CI에서 수행하면 되지 왜 로컬에서 한 번 더 확인하나요? 이중 작업 아닌가요?**

첫 번째는 시간을 아끼기 위해서입니다.    
생각보다 GitLab CI 파이프라인은 확인하기까지 시간이 소요됩니다.
pre-commit을 사용하면 커밋하기 전에 로컬에서 빠르게 문제점을 확인해서 고칠 수 있습니다.

두 번째는 secret detection 때문입니다.    
보호해야할 시크릿들이 푸시해서 올라가게 되면 GitLab CI 파이프라인을 돌아도 커밋이나 MR 기록에 남기 때문에 무의미해집니다.
따라서 코드 저장소에 올리기 전에 로컬에서 먼저 체크하게 됩니다.