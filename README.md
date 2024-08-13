# Wise Prompt

[![PythonVersion](https://img.shields.io/badge/python-3.9.13-blue)](https://www.python.org/downloads/release/python-3913/)
[![FastAPIVersion](https://img.shields.io/badge/fastapi-0.111.0-yellowgreen)](https://fastapi.tiangolo.com/release-notes/#01110)
[![loguru](https://img.shields.io/badge/loguru-0.7.2-orange)](https://loguru.readthedocs.io/en/stable/project/changelog.html)

## Prompt Engineering
> 참고: [[Notion] 와이즈넛 성장기술연구소 기술연구-RAG Prompt Engineering](https://www.notion.so/wisenut/Prompt-Engineering-e6368f6b3aac44ef9cd70d6f5d2afbe6?pvs=4)
### Prompt Engineering Method
- Default
- CoT (Chain-of-Thought)
  - _Zero-shot CoT_
  - _Auto-CoT (Automatic Chain-of-Thought)_
- _Self-Consistency_
- _ReAct_
- ...
### Prompt Generation Method
- _APE (Automatic Prompt Engineering)_

### TODO
- Auto-CoT: dataset 도메인별 적용 방안
- Self-Consistency: 함수가 아닌 langchain 라이브러리를 이용해서 두 단계를 하나의 파이프라인으로 연결
- Self-Consistency, APE: API Call Batch
- ReAct: 직접 구현