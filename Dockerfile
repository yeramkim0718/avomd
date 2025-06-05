FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /code

# 의존성 파일 복사 및 설치
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . /code/

# 환경변수 설정 (옵션)
ENV PYTHONUNBUFFERED=1

# 기본 커맨드 (개발용 서버 실행)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]