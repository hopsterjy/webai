📁 PROJECT_SPEC.md
1. 프로젝트 개요 (Project Overview)
프로젝트명: Personal AI Newsroom (Antigravity Edition)
목표: 국내 IT 뉴스를 RSS로 수집하고, Google Gemini 3.0을 활용해 분석/요약한 뒤, Streamlit 기반의 원페이지 뉴스룸 웹사이트를 구축한다.
핵심 특징:
Serverless Data: 별도의 데이터베이스(DB)를 사용하지 않는다.
GitHub as a Database: 데이터(json)는 GitHub Repository에 직접 Commit하여 영구 저장 및 관리한다.
Dashboard: 관리자 권한으로 뉴스 수집 트리거 및 설정을 제어한다.
2. 기술 스택 (Tech Stack)
Language: Python 3.9+
Frontend/App: Streamlit
AI Engine: Google Gemini API (Model: gemini-3.0 or gemini-1.5-flash)
Data Source: RSS Feeds (feedparser)
Data Storage: GitHub Repository (PyGithub 라이브러리 활용)
Deploy: Streamlit Cloud
3. 파일 구조 (File Structure)
code
Text
/
├── app.py                # 메인 애플리케이션 (UI 및 라우팅)
├── utils.py              # 백엔드 로직 (GitHub CRUD, RSS 파싱, Gemini 호출)
├── requirements.txt      # 의존성 패키지 목록
└── .streamlit/
    └── secrets.toml      # 환경 변수 (로컬 테스트용, 실제 배포시 Cloud 설정 이용)
4. 데이터 스키마 (JSON Data Schema)
모든 데이터는 GitHub Repo의 루트 경로에 .json 파일로 저장된다.
4.1. feeds.json (뉴스 소스 관리)
code
JSON
[
  {
    "name": "구글 뉴스 (IT)",
    "url": "https://news.google.com/rss/..."
  },
  {
    "name": "GeekNews",
    "url": "http://feeds.feedburner.com/geeknews"
  }
]
4.2. news_data.json (분석된 뉴스 아카이브)
Key: 날짜 (YYYY-MM-DD)
Value: Gemini가 생성한 Markdown 포맷의 리포트
code
JSON
{
  "2025-12-03": "## 🚀 오늘의 IT 브리핑\n\n- **주요 이슈**: ...",
  "2025-12-02": "..."
}
4.3. stats.json (접속 통계)
code
JSON
{
  "total_visits": 1250,
  "last_visit": "2025-12-03 14:00:00"
}
5. 기능 명세 (Functional Requirements)
5.1. 백엔드 유틸리티 (utils.py)
GitHub Storage Handler (GitHubStorage Class)
load_json(filename): 리포지토리에서 파일 내용을 읽어와 Python 객체로 반환. 파일이 없으면 기본값 반환.
save_json(filename, content): Python 객체를 JSON으로 변환하여 리포지토리에 Commit (Update/Create).
라이브러리: PyGithub 사용.
RSS Fetcher & AI Analyzer (fetch_and_analyze Function)
입력된 RSS URL 리스트를 순회하며 최신 기사(Top 3)의 제목, 링크, 요약문을 수집.
수집된 텍스트를 하나의 프롬프트로 구성하여 Gemini API에 전송.
Prompt Persona: "IT 전문 뉴스 앵커"
Output Format: Markdown (헤드라인, 3대 뉴스, 해시태그 포함).
5.2. 프론트엔드 UI (app.py)
A. 사용자 모드 (메인 화면)
탭 1: 오늘의 브리핑
news_data.json에서 오늘 날짜(YYYY-MM-DD) 데이터를 조회하여 표시.
데이터가 없을 경우 "아직 발행되지 않음" 메시지 표시.
과거 날짜를 선택할 수 있는 Selectbox 제공 (아카이브 기능).
B. 관리자 모드 (사이드바 또는 별도 탭)
인증: secrets.toml에 설정된 ADMIN_PW와 일치해야 접근 가능.
기능 1: RSS 피드 관리
현재 등록된 RSS 목록 조회 (Table).
새로운 RSS 추가 (이름, URL 입력) 및 삭제 기능.
변경 사항은 즉시 feeds.json에 반영(Commit).
기능 2: 수동 발행 트리거
"뉴스 분석 및 발행" 버튼 클릭 시 utils.fetch_and_analyze 실행.
결과를 화면에 미리보기로 보여주고, 성공 시 news_data.json에 저장.
기능 3: 통계 보기
stats.json을 읽어 총 방문자 수 표시.
6. 환경 변수 및 보안 (Secrets)
Streamlit Cloud의 Secrets 메뉴에 다음 변수들이 반드시 설정되어야 한다.
code
Toml
[secrets]
GITHUB_TOKEN = "repo 권한이 있는 GitHub Personal Access Token"
REPO_NAME = "username/repository-name"
GEMINI_API_KEY = "Google AI Studio API Key"
ADMIN_PW = "관리자 접속 비밀번호"
7. 구현 단계 (Implementation Steps for Antigravity)
환경 설정: requirements.txt 생성 및 패키지 설치.
GitHub 연동 구현: utils.py에서 GitHubStorage 클래스 구현 및 테스트.
AI 로직 구현: RSS 파싱 로직과 Gemini 3.0 프롬프트 엔지니어링 구현.
UI 개발: Streamlit을 사용하여 메인 뷰와 관리자 대시보드 레이아웃 구성.
통합 테스트: 관리자 패널에서 "발행" 버튼을 눌러 실제 GitHub에 파일이 생성되는지 확인. 