# KHU Mobile/Web Service Project - Midterm Evaluation 02

경희대학교 **2026-2 모바일/웹서비스 프로젝트 중간평가 과제 2** 수행 결과를 정리한 저장소입니다.

YOLOv5를 이용해 객체를 실시간으로 검출하고, 검출 결과와 이미지를 Django REST Framework 서버에 전송하여 웹과 Android 애플리케이션에서 확인할 수 있도록 구현했습니다.

---

## 프로젝트 구성

```text
Midterm_Evaluation_02/
├─ PhotoBlogServer/   # Django REST Framework Server
├─ PhotoViewer/       # Android Client
├─ YOLOv5/            # YOLOv5 Edge Client
└─ 모바일웹서비스 프로젝트_공통평가 02_수행 결과 보고서.docx
```

---

## 주요 구현 사항

### 1. YOLOv5 객체 검출

- YOLOv5를 이용한 실시간 객체 검출
- Webcam 입력 기반 객체 탐지
- 검출 객체의 Class 및 Confidence 확인

- 참고 이미지 자료 
<img width="1916" height="1007" alt="image" src="https://github.com/user-attachments/assets/0ffa74a1-da8f-48b2-abd9-18ec3166ed91" />


### 2. Django 서버 연동

- YOLOv5에서 검출한 객체 정보를 Django REST API로 전송
- 검출 이미지와 객체 정보를 Multipart POST 방식으로 등록
- Token 기반 인증 사용
- Localhost 및 PythonAnywhere 환경 지원

### 3. Android Client

- Django 서버의 게시물 목록 조회
- YOLO에서 검출된 이미지 확인
- 게시물 제목, 날짜, 이미지 표시
- Local / Cloud 서버 환경 지원

### 4. PythonAnywhere 배포

- Django 서버를 PythonAnywhere에 배포
- YOLOv5 Local Client에서 Cloud Server로 검출 결과 전송
- PythonAnywhere 웹 페이지 및 REST API에서 등록 결과 확인

- 참고 이미지 자료
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/027d7219-bfc0-41f2-a955-da755cb92da6" />

---

## 추가 편의 기능

### Confidence 임계값 기반 서버 전송 필터링

YOLO 자체 검출 결과와 별도로 서버 전송용 Confidence 임계값을 적용했습니다.

기본값은 `0.50`이며, 임계값 이상의 객체만 Django 서버에 전송합니다.

```powershell
$env:POST_CONF_THRESHOLD="0.50"
```

이를 통해 낮은 신뢰도의 객체가 불필요하게 서버에 등록되는 것을 줄일 수 있습니다.

### Cooldown 기반 중복 전송 방지

동일 객체가 짧은 시간 내 반복적으로 검출되는 경우 서버에 중복 게시물이 생성되는 것을 방지하기 위해 Cooldown 기능을 적용했습니다.

기본 Cooldown 시간은 `30초`입니다.

```powershell
$env:POST_COOLDOWN_SECONDS="30"
```

Cooldown 시간이 지나기 전에 동일 객체가 다시 등장하면 서버 전송을 생략하고, 시간이 지난 후 재등장하면 새로운 이벤트로 등록합니다.

---

## 실행 방법

### 1. Django Server 실행

```bash
cd PhotoBlogServer

python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\activate
```

필요 패키지 설치:

```bash
pip install -r requirements.txt
```

DB Migration:

```bash
python manage.py migrate
```

서버 실행:

```bash
python manage.py runserver
```

---

### 2. YOLOv5 실행

```bash
cd YOLOv5
```

가상환경 생성 및 활성화:

```powershell
py -3.9 -m venv venv
.\venv\Scripts\Activate.ps1
```

필요 패키지 설치:

```bash
pip install -r requirements.txt
```

Django 접속 정보 설정:

```powershell
$env:DJANGO_HOST="http://127.0.0.1:8000"
$env:DJANGO_USERNAME="admin"
$env:DJANGO_PASSWORD="Django 관리자 비밀번호"

$env:POST_CONF_THRESHOLD="0.50"
$env:POST_COOLDOWN_SECONDS="30"
```

YOLO 실행:

```bash
python detect.py --source 0
```

PythonAnywhere 서버를 사용하는 경우 `DJANGO_HOST`를 Cloud URL로 변경합니다.

```powershell
$env:DJANGO_HOST="https://kimjinse.pythonanywhere.com"
```

---

## 동작 흐름

```text
Webcam
  ↓
YOLOv5 객체 검출
  ↓
Confidence 임계값 확인
  ↓
Cooldown 확인
  ↓
Django REST API POST
  ↓
Django Web / Android Client에서 확인
```

---

## 주요 기술

- Python
- YOLOv5
- OpenCV
- Django
- Django REST Framework
- Android Java
- Retrofit
- PythonAnywhere
