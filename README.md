# 심부름 요청 API

**2024 벤처스타트업아카데미 해커톤 \[서퍼톤\]**

'강'팀의 took 서비스의 백엔드 API 레포지토리입니다.

FastAPI와 MySQL로 만든 심부름 요청·수락·완료·정산 API입니다.

## 실행 환경

```text
Python 3.12.0
```

## 미리보기

서버 실행 후 API 문서는 아래에서 확인합니다.

```text
http://127.0.0.1:3001/docs
```

## 빠른 시작

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 3001
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --port 3001
```

## 가상 환경

가상 환경 폴더는 `.venv`를 사용합니다.

```bash
# macOS
source .venv/bin/activate
deactivate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
deactivate
```

## 환경 변수

`.env.sample`을 복사해 `.env` 파일을 만들고 DB 정보를 입력합니다.

```bash
# macOS
cp .env.sample .env
```

```powershell
# Windows PowerShell
Copy-Item .env.sample .env
```

`.env`에 MySQL 연결 정보를 입력합니다.

```text
DB_USERNAME=root
DB_PASSWORD=비밀번호
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=errand_db
```

`.env`에는 비밀번호 등 민감한 정보를 넣으므로 Git에 올리지 마세요.
