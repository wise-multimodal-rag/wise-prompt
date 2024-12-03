# Secret Detection

> Secret detection은 소스 코드나 설정 파일에서 API 키, 비밀번호, 토큰과 같은 민감한 정보를 자동으로 식별하고 노출을 방지하는 보안 기술입니다.
> 

## GitLab Secret Detection
> 현재 시크릿 탐지 기능은 _GitLab CI/CD Pipeline_ 과 _Pre-commit_ 모두 진행할 수 있도록 설정해두었으나 GitLab에서 리파티토리 자체적으로 차단할 수 있는 방법이 있다.    
> 로컬 리파지토리의 푸시를 리모트로 푸시할 때 GitLab에서 차단한다. (=Remote Repo에 커밋되지 않음)    
> 참고: <https://docs.gitlab.com/ee/user/application_security/secret_detection/>

- `Settings > Repository > Pre-defined push rules` 의 `Prevent pushing secret files`에서 설정 가능
- [Prevent pushing secret files](https://docs.gitlab.com/ee/user/project/repository/push_rules.html#prevent-pushing-secrets-to-the-repository) 참고하여 룰 설정

참고: <https://docs.gitlab.com/ee/user/application_security/secret_detection/secret_push_protection/index.html>
