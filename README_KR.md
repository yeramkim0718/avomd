# Avomd GPT Job 백엔드

이 프로젝트는 OpenAI GPT를 활용한 가이드라인 요약 및 체크리스트 생성용 비동기 백엔드 API입니다. 
Django, Celery, Redis, Postgres 기반으로 구현되었습니다.

## 주요 기능
- **POST /jobs**: 텍스트를 큐에 등록, 200ms 이내 event_id 반환
- **GET /jobs/{event_id}**: 작업 상태 및 결과(요약+체크리스트) 조회
- **비동기 처리**: Celery 워커가 GPT 체이닝(요약→체크리스트) 실행
- **API 문서**: `/swagger/`, `/redoc/`, `/schema/`에서 자동 생성 문서 제공
- **테스트 커버리지**: API 및 Celery 로직 단위 테스트, 70% 이상 커버리지

## 사용법 및 개발 프로세스
- 본 프로젝트는 Senior Dev Challenge의 공식 가이드(guide.mdc)와 Cursor TDD/품질 규칙(tdd-rule.mdc)을 철저히 준수하여 개발되었습니다.
- guide.mdc의 요구사항(2시간 내 최소 백엔드, Celery+Redis+Postgres, POST/GET jobs, 200ms 응답, 두 단계 GPT 체이닝, 오픈API 자동 문서, 70%+ 커버리지, docker compose one-command, README 300단어 이하 등)을 체크리스트로 만들어, 모든 기능이 빠짐없이 구현되도록 했습니다.
- tdd-rule.mdc에 따라, 실제 기능 구현 전 반드시 실패하는 테스트를 먼저 작성(Test-First, TDD)하였고, production 코드는 테스트가 존재할 때만 추가했습니다. 테스트 파일명, 커버리지, Celery 통합 테스트, 오픈API 문서 자동화, 커밋 보안 등도 룰에 맞게 관리했습니다.
- 복잡한 설계/비동기 흐름/테스트 시나리오/품질 기준 등은 mcp sequential thinking(체계적 사고 도구)로 단계별 체크리스트를 만들고, 각 단계별로 코드와 테스트가 요구사항을 충족하는지 반복적으로 점검했습니다.
- 커버리지 리포트와 코드 리뷰를 통해 70% 이상 커버리지를 달성했고, Celery 태스크는 직접 호출 방식으로도 검증했습니다.
- 개발 전 과정에서 AI 도구(Cursor, Copilot 등)를 적극 활용하여, 코드 자동 생성, 테스트 자동화, 문서화, 설계 검증 등 생산성과 품질을 극대화했습니다.

## 실행 방법
1. 저장소를 클론합니다.
2. `.env`에 OpenAI API 키를 추가합니다(절대 커밋 금지!).
3. 아래 명령어 실행:
   ```bash
   docker compose up --build
   ```
4. [http://localhost:8000/swagger/](http://localhost:8000/swagger/)에서 API 문서 확인

## 설계/AI 활용
- 모든 비동기 처리는 Celery와 Redis를 활용하여 백엔드에서 안전하게 분리·처리됩니다. 사용자가 /jobs로 요청을 보내면, Job이 생성되고 Celery 태스크로 큐에 등록됩니다. 워커는 FIFO로 큐를 소비하며, 1) GPT로 요약 생성 → 2) 다시 GPT로 체크리스트 생성의 두 단계 체이닝을 수행합니다.
- 각 Job의 상태(status)와 결과(result)는 Postgres에 영구 저장되어, 언제든 event_id로 조회할 수 있습니다. Job 모델은 입력, 상태, 결과, 생성시각을 모두 관리합니다.
- API 문서는 drf-spectacular로 자동 생성되며, Swagger/Redoc UI를 통해 쉽게 확인할 수 있습니다.
- 테스트는 Django REST API, Celery 태스크 단위 테스트를 모두 포함하며, 커버리지 70% 이상을 목표로 작성했습니다. Celery 태스크는 직접 호출 방식으로도 검증합니다.
- AI 도구(Cursor, Copilot 등)를 적극 활용하여 코드 스캐폴딩, 테스트 코드 자동 생성, OpenAPI 연동, 문서 작성 등 개발 생산성을 극대화했습니다.

## 테스트 및 커버리지 확인
- 모든 테스트 실행:
  ```bash
  pytest
  ```
- 커버리지 리포트 확인:
  ```bash
  pytest --cov=job --cov-report=term-missing
  ```

Name                             Stmts   Miss  Cover
----------------------------------------------------
config/__init__.py                   0      0   100%
config/settings.py                  24      0   100%
config/urls.py                       3      0   100%
job/__init__.py                      0      0   100%
job/admin.py                         1      0   100%
job/apps.py                          4      0   100%
job/migrations/0001_initial.py       6      0   100%
job/migrations/__init__.py           0      0   100%
job/models.py                        8      0   100%
job/serializers.py                  12      0   100%
job/tasks.py                        21      3    86%
job/tests.py                        61      0   100%
job/urls.py                          3      0   100%
job/views.py                        26      0   100%
----------------------------------------------------
TOTAL                              169      3    98%