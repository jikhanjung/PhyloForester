# 2025-10-23 R01: Project Status and Next Tasks Analysis

## 분석 목적
현재 프로젝트 상태를 파악하고 다음에 해야 할 작업들을 식별하여 개발 로드맵을 수립하기 위한 분석

## 📊 프로젝트 현황

### 코드 통계
```
총 코드량: 6,325 줄

주요 파일 구성:
  - PfDialog.py:      2,964 줄 (47%) - 대화상자/뷰어 클래스
  - PhyloForester.py: 1,877 줄 (30%) - 메인 애플리케이션
  - PfUtils.py:         733 줄 (12%) - 유틸리티/파서
  - PfModel.py:         410 줄 ( 6%) - 데이터 모델
  - PfLogger.py:         23 줄 (<1%) - 로깅 시스템 (신규)
  - migration.py:        34 줄 (<1%) - DB 마이그레이션
  - fitch_test*.py:     284 줄 ( 4%) - 알고리즘 테스트
```

### 최근 개발 활동 (HEAD~10)

**커밋 히스토리**:
```
0dfefaa - Fix requirements.txt encoding, add DEFAULT_LOG_DIRECTORY, update .gitignore (금일)
78cc5d8 - logger added
cdd97fc - minor fixes
84e67b5 - working on analysis run process
498636d - working on process management
d2b7c98 - working on analysis running process
203a3b8 - minor fixes
b4b0fcc - replaced all QFormLayout with QGridLayout
0d41a9f - minor fixes
0d220be - character mapping (kinda) done
```

**개발 포커스 영역**:
1. 분석 프로세스 관리 (analysis run process)
2. QProcess 기반 외부 프로그램 실행
3. 진행률 모니터링 및 UI 업데이트
4. 로깅 시스템 구축 (진행 중)
5. UI 레이아웃 개선 (GridLayout 통일)

### 최근 변경사항 (HEAD~3..HEAD)

**주요 수정 내용**:
```python
PhyloForester.py (21 줄 변경):
  - 위젯 교체 로직 개선 (빈 위젯 중복 교체 방지)
  - 데이터매트릭스 삭제 시 연관 분석 정리 로직 추가
  - 트리뷰 헤더 숨김 활성화

PfLogger.py (24 줄 신규):
  - 로깅 시스템 기본 구조 생성
  - 날짜별 로그 파일 생성 기능
  - 로그 위치: ~/PaleoBytes/PhyloForester/

PfDialog.py (7 줄 변경):
  - AnalysisViewer에 완료율 필드 추가
  - 분석 상태 QUEUED → READY 변경
```

## 🔍 코드 품질 분석

### 1. 로깅 시스템 현황

**생성된 구조**:
```python
# PfLogger.py (23 줄)
def setup_logger(name, level=logging.INFO):
    logfile_path = os.path.join(pu.DEFAULT_LOG_DIRECTORY,
                                pu.PROGRAM_NAME + '.' + date_str + '.log')
    # ... formatter, handler 설정
    return logger
```

**문제점**:
- ❌ **사용되지 않음**: 어디에서도 import 안됨
- ❌ **초기화 안됨**: setup_logger() 호출 없음
- ❌ **전파 안됨**: 로거 인스턴스가 클래스에 전달되지 않음

**영향**:
- 로깅 시스템이 작동하지 않음
- 디버깅 정보가 파일에 기록되지 않음

### 2. 디버깅 코드 분석

**print() 사용 현황**:
```
총 105개 print() 문 발견
```

**주요 사용 위치**:
```python
# PhyloForester.py
print("command:", command)                    # L508
print("result directory:", result_directory)  # L511
print("process started")                      # L563
print("Failed to start the process")          # L565
print("Error occurred:", error)               # L764
print("Error message:", self.process.errorString())  # L765
print("process finished")                     # L621
print("Process Finished")                     # L624 (주석)

# 진행률 확인 로직
print("progress detected", curr_step, flush=True)  # L660 (주석)

# PfUtils.py
print("interleaved format")                   # L293
print("sequential format")                    # L297
```

**문제점**:
- ⚠️ 프로덕션 코드에 디버그 출력 혼재
- ⚠️ 로그 레벨 구분 없음 (debug/info/error)
- ⚠️ 구조화된 로깅 불가능
- ⚠️ 로그 파일로 리다이렉트 불가

### 3. 에러 처리 분석

**try/except 사용 현황**:
```
try/except 블록: 0개
raise 문: 0개
```

**위험 영역 식별**:

#### 파일 I/O (에러 처리 없음)
```python
# PhyloForester.py:521-524
data_fd = open(data_file_location, mode='w')  # ❌ IOError 가능
data_fd.write(datamatrix_str)
data_fd.close()

# PfUtils.py:130-132
file = open(a_filepath, mode='r')  # ❌ FileNotFoundError 가능
self.file_text = file.read()
file.close()
```

**위험도**: 🔴 **HIGH** - 파일 접근 실패 시 앱 크래시

#### 외부 프로세스 실행 (부분적 처리)
```python
# PhyloForester.py:562-565
self.process.start(command, run_argument_list)
print("process started")
if self.process.state() == QProcess.NotRunning:
    print("Failed to start the process")  # ❌ 출력만 하고 처리 안함
```

**위험도**: 🟡 **MEDIUM** - 프로세스 실행 실패 시 상태 불일치

#### 데이터베이스 작업 (에러 처리 없음)
```python
# PhyloForester.py:484
analysis_list = PfAnalysis.select().where(...)  # ❌ OperationalError 가능
self.analysis = analysis_list[0]  # ❌ IndexError 가능

# PfModel.py:전체
# Peewee 모델 전체에 에러 처리 없음
```

**위험도**: 🟡 **MEDIUM** - DB 오류 시 예측 불가능한 동작

#### JSON 파싱 (에러 처리 없음)
```python
# PfModel.py:153
formatted_data_list = json.loads(self.datamatrix_json)  # ❌ JSONDecodeError 가능
return formatted_data_list

# PfModel.py:160-161
return json.loads(self.taxa_list_json)  # ❌ JSONDecodeError 가능
```

**위험도**: 🟡 **MEDIUM** - 손상된 데이터 시 복구 불가

### 4. 테스트 현황

**존재하는 테스트**:
```
fitch_test.py   (178 줄) - Fitch 알고리즘 테스트
fitch_test2.py   (72 줄) - Fitch 알고리즘 테스트 2
fitch_test3.py   (34 줄) - Fitch 알고리즘 테스트 3
```

**테스트 없는 주요 기능**:
- ❌ 데이터 모델 (PfModel.py)
- ❌ 파일 파싱 (Nexus, Phylip, TNT)
- ❌ 데이터매트릭스 연산
- ❌ 분석 프로세스 관리
- ❌ UI 컴포넌트
- ❌ 트리 생성/시각화

**테스트 커버리지**: ~5% (알고리즘만)

### 5. 빌드 시스템 분석

**현재 방식**:
```bash
# CLAUDE.md에 문서화된 긴 명령어
pyinstaller --onedir --noconsole \
  --add-data "icons/*.png;icons" \
  --add-data "data/*.*;data" \
  --add-data "translations/*.qm;translations" \
  --add-data "migrations/*;migrations" \
  --icon="icons/PhyloForester.png" \
  --noconfirm PhyloForester.py
```

**문제점**:
- ❌ `.spec` 파일 없음
- ❌ 매번 긴 명령어 입력 필요
- ❌ 빌드 설정 버전 관리 안됨
- ❌ 자동화 어려움

### 6. 국제화 (i18n) 현황

**번역 파일**:
```
translations/PhyloForester_en.ts  (688 bytes)
translations/PhyloForester_en.qm  (297 bytes) - 컴파일됨
translations/PhyloForester_ko.ts  (693 bytes)
translations/PhyloForester_ko.qm  (280 bytes) - 컴파일됨
```

**상태**:
- ✅ 번역 인프라 존재
- ⚠️ 최신 기능 반영 여부 불확실
- ⚠️ 마지막 업데이트: 프로젝트 초기

## 🎯 식별된 작업 항목

### Category 1: 안정성 (Stability) 🔴

#### S1. 에러 처리 추가
**우선순위**: 🔴 CRITICAL
**예상 시간**: 8-12 시간

**세부 작업**:
1. 파일 I/O 에러 처리
   - `PhyloForester.py`: 데이터 파일 쓰기 (L521-524)
   - `PfUtils.py`: 파일 읽기 (L130-132)
   - `PfModel.py`: import_file 메서드

2. 프로세스 실행 에러 처리
   - `PhyloForester.py`: startAnalysis (L562-570)
   - QProcess 시작 실패 처리
   - 외부 프로그램 경로 검증

3. 데이터베이스 에러 처리
   - 쿼리 실행 에러
   - 데이터 무결성 에러
   - 연결 에러

4. JSON 파싱 에러 처리
   - `PfModel.py`: datamatrix_as_list, get_taxa_list
   - 손상된 데이터 복구 전략

**영향도**: 앱 크래시 방지, 사용자 경험 개선

#### S2. PfLogger 통합
**우선순위**: 🔴 HIGH
**예상 시간**: 2-4 시간

**세부 작업**:
1. 로거 초기화
   - `PhyloForester.py`: 앱 시작 시 setup_logger 호출
   - 메인 윈도우에 로거 인스턴스 저장

2. 로거 전파
   - 주요 클래스에 logger 파라미터 추가
   - Dialog 클래스들에 로거 전달

3. 로그 레벨 설정
   - 개발 모드: DEBUG
   - 프로덕션: INFO

**영향도**: 디버깅 효율성 향상

#### S3. print() → logging 교체
**우선순위**: 🟡 MEDIUM
**예상 시간**: 4-6 시간

**세부 작업**:
1. Phase 1: 핵심 로직 (105개 중 ~30개)
   - startAnalysis
   - progress_check
   - handleError
   - onProcessFinished

2. Phase 2: 유틸리티 (105개 중 ~20개)
   - PfUtils.py 파일 파싱 로직

3. Phase 3: 나머지 (105개 중 ~55개)
   - 주석 처리된 print 제거
   - 기타 디버그 출력

**영향도**: 코드 품질 향상, 로그 관리 용이

### Category 2: 품질 보증 (Quality Assurance) 🟡

#### Q1. 테스트 작성
**우선순위**: 🟡 MEDIUM
**예상 시간**: 12-16 시간

**세부 작업**:
1. 단위 테스트 (Unit Tests)
   - `test_model.py`: 데이터 모델 테스트
   - `test_parsers.py`: Nexus/Phylip/TNT 파서 테스트
   - `test_datamatrix.py`: 데이터매트릭스 연산 테스트

2. 통합 테스트 (Integration Tests)
   - `test_analysis_process.py`: 분석 프로세스 테스트
   - `test_database.py`: DB 연산 테스트

3. UI 테스트 (UI Tests)
   - `test_dialogs.py`: 대화상자 테스트 (pytest-qt)
   - `test_main_window.py`: 메인 윈도우 테스트

**테스트 프레임워크**:
```python
# requirements.txt에 추가 필요
pytest
pytest-qt
pytest-cov  # 커버리지 측정
```

**목표 커버리지**: 60% (핵심 로직)

### Category 3: 개발 경험 (Developer Experience) 🟢

#### D1. PyInstaller Spec 파일
**우선순위**: 🟢 LOW
**예상 시간**: 1-2 시간

**세부 작업**:
1. spec 파일 생성
   ```bash
   pyi-makespec --onedir --noconsole \
     --icon="icons/PhyloForester.png" \
     PhyloForester.py
   ```

2. spec 파일 커스터마이징
   - 데이터 파일 자동 포함
   - 버전 정보 추가
   - 빌드 옵션 설정

3. 빌드 스크립트 작성
   ```bash
   # build.sh (Linux/macOS)
   # build.bat (Windows)
   ```

**영향도**: 빌드 프로세스 자동화

#### D2. 번역 업데이트
**우선순위**: 🟢 LOW
**예상 시간**: 2-3 시간

**세부 작업**:
1. 번역 문자열 추출
   ```bash
   pylupdate5 PhyloForester.py PfDialog.py -ts translations/PhyloForester_en.ts
   pylupdate5 PhyloForester.py PfDialog.py -ts translations/PhyloForester_ko.ts
   ```

2. Qt Linguist로 번역 작업
   - 새로 추가된 문자열 번역
   - 기존 번역 검토

3. 번역 컴파일
   ```bash
   lrelease translations/*.ts
   ```

**영향도**: 사용자 경험 (다국어 지원)

## 🚨 위험 요소 및 기술 부채

### Critical Issues
1. **에러 처리 부재** (Risk: HIGH)
   - 파일 I/O 실패 시 크래시
   - 외부 프로그램 실행 실패 시 상태 불일치
   - 복구 불가능한 상태 발생 가능

2. **로깅 시스템 미사용** (Risk: MEDIUM)
   - 프로덕션 환경에서 디버깅 어려움
   - 사용자 문제 재현 불가
   - 성능 이슈 파악 어려움

### Technical Debt
1. **테스트 부재** (Debt: HIGH)
   - 리팩토링 위험도 증가
   - 회귀 버그 발생 가능성
   - 코드 품질 검증 불가

2. **print() 문 산재** (Debt: MEDIUM)
   - 로그 관리 어려움
   - 프로덕션 빌드에 디버그 출력 포함
   - 코드 가독성 저하

3. **빌드 프로세스 수동화** (Debt: LOW)
   - 빌드 재현성 낮음
   - 설정 버전 관리 안됨
   - 자동화 어려움

## 📈 코드 메트릭스

```
코드 복잡도:
  - 최대 함수 크기: ~200 줄 (AnalysisDialog.__init__)
  - 평균 함수 크기: ~30 줄
  - 최대 파일 크기: 2,964 줄 (PfDialog.py)

유지보수성:
  - 에러 처리: ⚠️ 없음
  - 로깅: ⚠️ 구축 중 (미사용)
  - 테스트: ⚠️ 5% 커버리지
  - 문서화: ✅ CLAUDE.md 존재

의존성:
  - PyQt5: GUI 프레임워크
  - Peewee: ORM
  - Biopython: 계통수 파싱
  - Matplotlib: 시각화
  - 외부 도구: TNT, IQTree, MrBayes
```

## 🎓 학습 포인트

### 잘된 점
1. ✅ **명확한 아키텍처**: 4계층 구조 잘 분리됨
2. ✅ **데이터베이스 마이그레이션**: peewee-migrate 사용
3. ✅ **국제화 준비**: 번역 인프라 존재
4. ✅ **문서화**: CLAUDE.md로 프로젝트 가이드 제공

### 개선 필요
1. ⚠️ **에러 처리**: 전체적으로 부재
2. ⚠️ **로깅**: 시스템은 있으나 미사용
3. ⚠️ **테스트**: 알고리즘만 테스트됨
4. ⚠️ **코드 품질**: print() 문 과다 사용

## 📝 권장 사항

### 즉시 시작 (1-2주 내)
1. **에러 처리 추가** - 안정성 확보
2. **PfLogger 통합** - 디버깅 인프라 구축
3. **핵심 로직 로깅 교체** - 코드 품질 개선

### 단기 목표 (1개월 내)
4. **기본 테스트 작성** - 품질 보증
5. **PyInstaller spec 파일** - 빌드 자동화

### 장기 목표 (필요시)
6. **번역 업데이트** - 사용자 경험
7. **전체 print() 교체** - 기술 부채 해소
8. **포괄적 테스트** - 60% 커버리지 달성

## 🔗 관련 문서

- `CLAUDE.md`: 프로젝트 아키텍처 및 가이드
- `devlog/20251023_001_fix_encoding_and_logging_setup.md`: 최근 수정 내역
- Recent commits: `84e67b5` ~ `0dfefaa` (분석 프로세스 개선 작업)

---

**분석 일시**: 2025-10-23
**분석자**: Claude Code
**다음 문서**: `20251023_P01_improvement_plan.md` (작업 계획)
