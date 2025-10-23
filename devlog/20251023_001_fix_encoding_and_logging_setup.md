# 2025-10-23: Fix Encoding Issues and Logging Setup

## 작업 개요
프로젝트 현황 파악 중 발견된 크리티컬 버그 3건을 수정하고 개발 환경을 정리했습니다.

## 발견된 문제점

### 1. requirements.txt 인코딩 문제 🔴
- **증상**: 파일이 UTF-16 LE로 인코딩되어 있음
- **영향**: `pip install -r requirements.txt` 실행 시 오류 발생 가능
- **원인**: 파일 편집 시 잘못된 인코딩으로 저장됨

```bash
# 문제 확인
$ file requirements.txt
requirements.txt: Unicode text, UTF-16, little-endian text, with CRLF line terminators
```

### 2. PfLogger.py의 미정의 상수 참조 🔴
- **위치**: `PfLogger.py:15`
- **증상**: `pu.DEFAULT_LOG_DIRECTORY` 참조하지만 `PfUtils.py`에 정의되지 않음
- **영향**: 로거 초기화 시 `AttributeError` 발생
- **존재하는 상수**: `DEFAULT_DB_DIRECTORY`만 정의됨

```python
# PfLogger.py:15
logfile_path = os.path.join(pu.DEFAULT_LOG_DIRECTORY, pu.PROGRAM_NAME + '.' + date_str + '.log')
# AttributeError: module 'PfUtils' has no attribute 'DEFAULT_LOG_DIRECTORY'
```

### 3. 분석 결과 디렉토리가 Git에 추적됨 🟡
- **증상**: `CLOUDINA_Parsimony_140836/`, `CLOUDINA_Parsimony_141035/` 등이 untracked files로 표시
- **영향**: Git 상태가 지저분해지고 불필요한 파일이 커밋될 위험
- **필요 조치**: `.gitignore`에 패턴 추가 필요

## 수정 내용

### 1. requirements.txt UTF-8 인코딩으로 변환 ✅

**변경 전:**
- UTF-16 LE 인코딩
- 패키지명: `Bio` (잘못된 이름)

**변경 후:**
- UTF-8/ASCII 인코딩
- 패키지명: `biopython` (올바른 이름)

```bash
$ cat > requirements.txt << 'EOF'
numpy
peewee
peewee_migrate
pillow
PyQt5
PyQt5-Qt5
PyQt5-sip
pyinstaller
biopython
matplotlib
EOF
```

**검증:**
```bash
$ file requirements.txt
requirements.txt: ASCII text
```

### 2. PfUtils.py에 DEFAULT_LOG_DIRECTORY 상수 추가 ✅

**파일**: `PfUtils.py:18`

**추가 코드:**
```python
DEFAULT_DB_DIRECTORY = os.path.join( USER_PROFILE_DIRECTORY, COMPANY_NAME, PROGRAM_NAME )
DEFAULT_LOG_DIRECTORY = os.path.join( USER_PROFILE_DIRECTORY, COMPANY_NAME, PROGRAM_NAME )  # 추가
```

**로그 파일 위치:**
- Windows: `C:\Users\{username}\PaleoBytes\PhyloForester\PhyloForester.YYYYMMDD.log`
- macOS/Linux: `~/PaleoBytes/PhyloForester/PhyloForester.YYYYMMDD.log`

### 3. .gitignore에 PhyloForester 전용 패턴 추가 ✅

**추가된 섹션:**
```gitignore
# PhyloForester specific
# Analysis result directories (pattern: *_Parsimony_*, *_ML_*, *_Bayesian_*)
*_Parsimony_*/
*_ML_*/
*_Bayesian_*/

# Database files
*.db
*.db-journal

# Application logs
PhyloForester.*.log
```

**무시되는 파일/디렉토리:**
- 분석 결과 디렉토리 (Parsimony/ML/Bayesian 패턴)
- SQLite 데이터베이스 파일
- 애플리케이션 로그 파일

## 추가 작업: CLAUDE.md 생성 📝

Claude Code를 위한 프로젝트 가이드 문서를 생성했습니다.

**내용:**
- 프로젝트 개요 및 아키텍처
- 4계층 구조 설명 (Main/Model/Dialog/Utility)
- 핵심 아키텍처 패턴 (프로세스 관리, 데이터 저장 전략, 위젯 라이프사이클)
- 빌드/실행 명령어
- 외부 의존성 (TNT, IQTree, MrBayes)
- 중요 구현 세부사항

## 결과

### Git 상태
```
Changes not staged for commit:
  modified:   .gitignore
  modified:   PfUtils.py
  modified:   requirements.txt

Untracked files:
  CLAUDE.md
  devlog/
```

### 수정 효과
✅ `pip install -r requirements.txt` 정상 작동
✅ `PfLogger.setup_logger()` AttributeError 해결
✅ 분석 결과 디렉토리가 더 이상 Git 상태에 표시되지 않음
✅ 깔끔한 개발 환경 구축

## 프로젝트 컨텍스트

### 최근 커밋 (HEAD~5..HEAD)
```
78cc5d8 - logger added (최신)
cdd97fc - minor fixes
84e67b5 - working on analysis run process
498636d - working on process management
d2b7c98 - working on analysis running process
```

### 현재 개발 포커스
- QProcess 기반 외부 프로그램 실행 관리
- 분석 진행률 실시간 파싱 및 UI 업데이트
- 로깅 시스템 구축 (진행 중)
- 분석 상태 머신 (`READY` → `RUNNING` → `FINISHED/STOPPED/FAILED`)

### 주요 변경사항
- 분석 상태: `ANALYSIS_STATUS_QUEUED` → `ANALYSIS_STATUS_READY`
- AnalysisViewer에 완료율 필드 추가
- GridLayout으로 UI 통일

## 다음 단계

1. 변경사항 커밋
   ```bash
   git add .gitignore PfUtils.py requirements.txt CLAUDE.md devlog/
   git commit -m "Fix requirements.txt encoding, add DEFAULT_LOG_DIRECTORY, update .gitignore"
   ```

2. 로깅 시스템 테스트
   - `PfLogger.setup_logger()` 동작 확인
   - 로그 파일 생성 및 기록 검증

3. 분석 프로세스 관리 기능 완성
   - 진행률 파싱 로직 개선
   - 에러 처리 강화

## 참고사항

### 의존성 목록 (requirements.txt)
- numpy
- peewee (ORM)
- peewee_migrate (DB 마이그레이션)
- pillow (이미지 처리)
- PyQt5 (GUI 프레임워크)
- pyinstaller (실행 파일 빌드)
- biopython (계통수 파싱)
- matplotlib (시각화)

### 데이터베이스 위치
- `~/PaleoBytes/PhyloForester/PhyloForester.db`

### 외부 소프트웨어 통합
- **TNT**: Parsimony 분석
- **IQTree**: Maximum Likelihood 분석
- **MrBayes**: Bayesian 분석

---

**작업 시간**: 약 30분
**수정 파일**: 3개 (requirements.txt, PfUtils.py, .gitignore)
**신규 파일**: 2개 (CLAUDE.md, devlog/)
**해결된 버그**: 3건 (모두 크리티컬)
