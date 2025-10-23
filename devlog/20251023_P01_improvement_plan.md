# 2025-10-23 P01: PhyloForester Improvement Plan

## 계획 개요

**기반 문서**: `20251023_R01_project_status_and_next_tasks_analysis.md`
**목표**: 안정성 향상 및 코드 품질 개선
**기간**: 3주 (Phase 1-2), 필요시 추가
**우선순위**: 안정성 > 품질 보증 > 개발 경험

## 🎯 Phase 1: 안정성 확보 (1주차)

### Sprint 1.1: 에러 처리 기반 구축 (Day 1-2)

#### Task 1.1.1: 에러 처리 유틸리티 작성
**예상 시간**: 2시간
**담당 파일**: `PfUtils.py`

**작업 내용**:
```python
# PfUtils.py에 추가
class PhyloForesterException(Exception):
    """Base exception for PhyloForester"""
    pass

class FileOperationError(PhyloForesterException):
    """File I/O related errors"""
    pass

class ProcessExecutionError(PhyloForesterException):
    """External process execution errors"""
    pass

class DataParsingError(PhyloForesterException):
    """Data parsing errors"""
    pass

def safe_file_read(filepath, mode='r', encoding='utf-8'):
    """Safely read file with error handling"""
    try:
        with open(filepath, mode=mode, encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        raise FileOperationError(f"File not found: {filepath}")
    except PermissionError:
        raise FileOperationError(f"Permission denied: {filepath}")
    except Exception as e:
        raise FileOperationError(f"Error reading file {filepath}: {e}")

def safe_file_write(filepath, content, mode='w', encoding='utf-8'):
    """Safely write file with error handling"""
    try:
        with open(filepath, mode=mode, encoding=encoding) as f:
            f.write(content)
    except PermissionError:
        raise FileOperationError(f"Permission denied: {filepath}")
    except Exception as e:
        raise FileOperationError(f"Error writing file {filepath}: {e}")

def safe_json_loads(json_str, default=None):
    """Safely parse JSON with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        if default is not None:
            return default
        raise DataParsingError(f"Invalid JSON: {e}")
```

**체크리스트**:
- [ ] 예외 클래스 정의
- [ ] safe_file_read 구현
- [ ] safe_file_write 구현
- [ ] safe_json_loads 구현
- [ ] 유닛 테스트 작성 (test_utils.py)

#### Task 1.1.2: 파일 I/O 에러 처리 적용
**예상 시간**: 3시간
**담당 파일**: `PhyloForester.py`, `PfUtils.py`, `PfModel.py`

**작업 내용**:

**Location 1**: `PhyloForester.py:521-524` (startAnalysis)
```python
# Before
data_fd = open(data_file_location, mode='w')
data_fd.write(datamatrix_str)
data_fd.close()

# After
try:
    pu.safe_file_write(data_file_location, datamatrix_str)
    self.logger.info(f"Data file written: {data_file_location}")
except pu.FileOperationError as e:
    self.logger.error(f"Failed to write data file: {e}")
    QMessageBox.critical(self, "File Error",
                        f"Failed to save analysis data:\n{e}")
    self.analysis.analysis_status = ANALYSIS_STATUS_FAILED
    self.analysis.save()
    return
```

**Location 2**: `PfUtils.py:130-132` (PhyloDatafile.loadfile)
```python
# Before
file = open(a_filepath, mode='r')
self.file_text = file.read()
file.close()

# After
try:
    self.file_text = safe_file_read(a_filepath)
except FileOperationError as e:
    # Return False to indicate failure
    print(f"Error loading file: {e}")
    return False
```

**Location 3**: `PfModel.py:166-184` (import_file)
```python
# Before
datafile_obj = pu.PhyloDatafile()
ret = datafile_obj.loadfile(file_path)
if ret:
    # ... 데이터 처리

# After
try:
    datafile_obj = pu.PhyloDatafile()
    ret = datafile_obj.loadfile(file_path)
    if not ret:
        raise pu.DataParsingError(f"Failed to parse file: {file_path}")
    # ... 데이터 처리
except (pu.FileOperationError, pu.DataParsingError) as e:
    self.logger.error(f"Import failed: {e}")
    return False
```

**체크리스트**:
- [ ] PhyloForester.py:521-524 수정
- [ ] PhyloForester.py:535-536 수정 (run file copy)
- [ ] PfUtils.py:130-132 수정
- [ ] PfUtils.py:388-390 수정 (PhyloTreefile)
- [ ] PfModel.py:166-184 수정
- [ ] 에러 발생 시 사용자 알림 추가
- [ ] 통합 테스트 작성

#### Task 1.1.3: QProcess 에러 처리 개선
**예상 시간**: 3시간
**담당 파일**: `PhyloForester.py`

**작업 내용**:

**Location**: `PhyloForester.py:562-570` (startAnalysis)
```python
# Before
self.process.start(command, run_argument_list)
print("process started")
if self.process.state() == QProcess.NotRunning:
    print("Failed to start the process")

# After
try:
    # 실행 파일 존재 확인
    if not os.path.isfile(command):
        raise pu.ProcessExecutionError(
            f"Analysis software not found: {command}\n"
            f"Please configure the path in Preferences.")

    # 실행 권한 확인 (Linux/macOS)
    if platform.system() != 'Windows':
        if not os.access(command, os.X_OK):
            raise pu.ProcessExecutionError(
                f"No execute permission: {command}")

    self.process.start(command, run_argument_list)

    # 프로세스 시작 대기 (최대 5초)
    if not self.process.waitForStarted(5000):
        raise pu.ProcessExecutionError(
            f"Failed to start analysis:\n{self.process.errorString()}")

    self.logger.info(f"Process started: {command} {run_argument_list}")
    self.data_storage['analysis'][self.analysis.id]['widget'].append_output(
        "Analysis started successfully")

except pu.ProcessExecutionError as e:
    self.logger.error(f"Process execution failed: {e}")
    QMessageBox.critical(self, "Execution Error", str(e))

    # 분석 상태를 FAILED로 변경
    self.analysis.analysis_status = ANALYSIS_STATUS_FAILED
    self.analysis.save()
    self.update_analysis_info(self.analysis)

    # 다음 분석 시도
    self.startAnalysis()
```

**handleError 개선**:
```python
# PhyloForester.py:763-765
def handleError(self, error):
    error_messages = {
        QProcess.FailedToStart: "Failed to start (file not found or no permission)",
        QProcess.Crashed: "Process crashed",
        QProcess.Timedout: "Process timed out",
        QProcess.WriteError: "Write error",
        QProcess.ReadError: "Read error",
        QProcess.UnknownError: "Unknown error"
    }

    error_msg = error_messages.get(error, "Unknown error")
    self.logger.error(f"Process error: {error_msg} - {self.process.errorString()}")

    if hasattr(self, 'analysis') and self.analysis:
        self.analysis.analysis_status = ANALYSIS_STATUS_FAILED
        self.analysis.save()
        self.update_analysis_info(self.analysis)

        QMessageBox.critical(self, "Analysis Error",
                            f"Analysis failed: {error_msg}\n\n"
                            f"Details: {self.process.errorString()}")
```

**체크리스트**:
- [ ] 실행 파일 존재 확인 로직 추가
- [ ] 실행 권한 확인 (Linux/macOS)
- [ ] waitForStarted 타임아웃 처리
- [ ] handleError 메서드 개선
- [ ] 실패 시 analysis_status 업데이트
- [ ] 사용자 친화적 에러 메시지
- [ ] 통합 테스트 작성

### Sprint 1.2: 로깅 시스템 통합 (Day 3-4)

#### Task 1.2.1: PfLogger 개선 및 초기화
**예상 시간**: 2시간
**담당 파일**: `PfLogger.py`, `PhyloForester.py`

**작업 내용**:

**PfLogger.py 개선**:
```python
import PfUtils as pu
import logging
import os
from datetime import datetime

# 로그 디렉토리 생성
if not os.path.exists(pu.DEFAULT_LOG_DIRECTORY):
    os.makedirs(pu.DEFAULT_LOG_DIRECTORY)

def setup_logger(name, level=logging.INFO):
    """Setup application logger

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")

    logfile_path = os.path.join(pu.DEFAULT_LOG_DIRECTORY,
                                f'{pu.PROGRAM_NAME}.{date_str}.log')

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(logfile_path, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Only warnings+ to console

    # Logger configuration
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent duplicate logs
    logger.propagate = False

    return logger

def get_logger(name):
    """Get existing logger or create new one"""
    return logging.getLogger(name)
```

**PhyloForester.py 초기화**:
```python
# PhyloForester.py 상단 (import 섹션)
import PfLogger

class PhyloForesterMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Logger 초기화 (첫 번째로)
        self.logger = PfLogger.setup_logger(__name__, logging.INFO)
        self.logger.info("=" * 60)
        self.logger.info(f"PhyloForester v{pu.PROGRAM_VERSION} starting")
        self.logger.info(f"Platform: {platform.system()} {platform.release()}")
        self.logger.info("=" * 60)

        # ... 기존 초기화 코드
```

**체크리스트**:
- [ ] PfLogger.py 개선 (console handler 추가)
- [ ] 로그 디렉토리 자동 생성
- [ ] PhyloForester.py에서 logger 초기화
- [ ] 앱 시작/종료 로그 추가
- [ ] 로그 파일 생성 확인

#### Task 1.2.2: Dialog 클래스에 로거 전달
**예상 시간**: 2시간
**담당 파일**: `PfDialog.py`, `PhyloForester.py`

**작업 내용**:

**AnalysisViewer**:
```python
# PfDialog.py
class AnalysisViewer(QWidget):
    def __init__(self, logger=None):
        super(AnalysisViewer, self).__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        # ... 기존 초기화

    def set_analysis(self, analysis):
        self.logger.debug(f"Setting analysis: {analysis.analysis_name}")
        # ... 기존 로직
```

**주요 Dialog 클래스들**:
- AnalysisDialog
- DatamatrixDialog
- ProjectDialog
- PreferencesDialog

**PhyloForester.py에서 로거 전달**:
```python
# 예: AnalysisDialog 생성 시
self.analysis_dialog = AnalysisDialog(self, logger=self.logger)
```

**체크리스트**:
- [ ] AnalysisViewer에 logger 파라미터 추가
- [ ] AnalysisDialog에 logger 파라미터 추가
- [ ] DatamatrixDialog에 logger 파라미터 추가
- [ ] ProjectDialog에 logger 파라미터 추가
- [ ] PreferencesDialog에 logger 파라미터 추가
- [ ] Dialog 생성 시 logger 전달

#### Task 1.2.3: 핵심 로직 print() → logging 교체 (Phase 1)
**예상 시간**: 4시간
**담당 파일**: `PhyloForester.py`

**작업 내용**:

**startAnalysis 메서드** (30개 print 중 약 10개):
```python
# L508: print("command:", command)
self.logger.info(f"Starting analysis with command: {command}")

# L511: print("result directory:", result_directory)
self.logger.info(f"Result directory: {result_directory}")

# L563: print("process started")
self.logger.info(f"Process started successfully")

# L565: print("Failed to start the process")
self.logger.error("Failed to start the process")
```

**progress_check 메서드** (주석 포함):
```python
# L660: print("progress detected", curr_step, flush=True) (주석)
self.logger.debug(f"Progress detected: {curr_step}/{total_step}")
```

**handleError 메서드**:
```python
# L764-765
self.logger.error(f"Error occurred: {error}")
self.logger.error(f"Error message: {self.process.errorString()}")
```

**onProcessFinished 메서드**:
```python
# L621, 624
self.logger.info("Analysis process finished")
self.logger.info(f"Exit code: {exitCode}")
```

**체크리스트**:
- [ ] startAnalysis 메서드 (10개)
- [ ] progress_check 메서드 (5개)
- [ ] handleError 메서드 (2개)
- [ ] onProcessFinished 메서드 (3개)
- [ ] onReadyReadStandardOutput 메서드
- [ ] onReadyReadStandardError 메서드
- [ ] 주석 처리된 print 제거
- [ ] 로그 레벨 적절히 설정

**로그 레벨 가이드**:
- `DEBUG`: 상세한 디버그 정보 (progress, state changes)
- `INFO`: 일반 정보 (process started, file created)
- `WARNING`: 경고 (unusual but handled situations)
- `ERROR`: 에러 (recoverable errors)
- `CRITICAL`: 치명적 에러 (unrecoverable errors)

### Sprint 1.3: 데이터베이스 에러 처리 (Day 5)

#### Task 1.3.1: Peewee 에러 처리
**예상 시간**: 3시간
**담당 파일**: `PhyloForester.py`, `PfModel.py`

**작업 내용**:

**데이터베이스 쿼리 에러 처리**:
```python
# PhyloForester.py:484
# Before
analysis_list = PfAnalysis.select().where(
    PfAnalysis.analysis_status == ANALYSIS_STATUS_READY
).order_by(PfAnalysis.created_at)
if len(analysis_list) == 0:
    return
self.analysis = analysis_list[0]

# After
try:
    analysis_list = PfAnalysis.select().where(
        PfAnalysis.analysis_status == ANALYSIS_STATUS_READY
    ).order_by(PfAnalysis.created_at)

    if len(analysis_list) == 0:
        self.logger.info("No ready analyses to start")
        return

    self.analysis = analysis_list[0]
    self.logger.info(f"Starting analysis: {self.analysis.analysis_name}")

except OperationalError as e:
    self.logger.error(f"Database error: {e}")
    QMessageBox.critical(self, "Database Error",
                        f"Failed to access database:\n{e}")
    return
except IndexError as e:
    self.logger.error(f"No analysis found: {e}")
    return
```

**PfModel save() 에러 처리**:
```python
# PfModel.py에 추가
class PfDatamatrix(Model):
    # ... 기존 코드

    def safe_save(self):
        """Save with error handling"""
        try:
            self.save()
            return True
        except IntegrityError as e:
            print(f"Integrity error: {e}")
            return False
        except OperationalError as e:
            print(f"Database error: {e}")
            return False
```

**체크리스트**:
- [ ] 주요 SELECT 쿼리 에러 처리
- [ ] save() 호출 에러 처리
- [ ] delete_instance() 에러 처리
- [ ] 외래 키 제약 위반 처리
- [ ] 데이터베이스 연결 에러 처리

#### Task 1.3.2: JSON 파싱 에러 처리
**예상 시간**: 2시간
**담당 파일**: `PfModel.py`

**작업 내용**:

**datamatrix_as_list**:
```python
# PfModel.py:151-156
def datamatrix_as_list(self):
    if self.datamatrix_json:
        try:
            formatted_data_list = json.loads(self.datamatrix_json)
            return formatted_data_list
        except json.JSONDecodeError as e:
            print(f"Error parsing datamatrix JSON: {e}")
            return []
    else:
        return []
```

**get_taxa_list**:
```python
# PfModel.py:158-163
def get_taxa_list(self):
    if self.taxa_list_json:
        try:
            return json.loads(self.taxa_list_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing taxa list JSON: {e}")
            return []
    else:
        return []
```

**get_character_list**:
```python
# PfModel.py:141-149
def get_character_list(self):
    self.character_list = []
    if self.character_list_json:
        try:
            self.character_list = json.loads(self.character_list_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing character list JSON: {e}")
            self.character_list = []
    # ... 나머지 로직
```

**체크리스트**:
- [ ] datamatrix_as_list 에러 처리
- [ ] get_taxa_list 에러 처리
- [ ] get_character_list 에러 처리
- [ ] get_taxa_timetable 에러 처리
- [ ] get_tree_options 에러 처리 (PfTree)

## 🧪 Phase 2: 품질 보증 (2주차)

### Sprint 2.1: 테스트 인프라 구축 (Day 6-7)

#### Task 2.1.1: 테스트 환경 설정
**예상 시간**: 2시간

**작업 내용**:

**requirements.txt 업데이트**:
```
# Testing dependencies
pytest>=7.0.0
pytest-qt>=4.2.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
```

**테스트 디렉토리 구조**:
```
PhyloForester/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures
│   ├── test_utils.py        # PfUtils 테스트
│   ├── test_model.py        # PfModel 테스트
│   ├── test_parsers.py      # 파서 테스트
│   ├── test_datamatrix.py   # 데이터매트릭스 테스트
│   ├── test_dialogs.py      # Dialog 테스트
│   └── fixtures/            # 테스트 데이터
│       ├── test_nexus.nex
│       ├── test_phylip.phy
│       └── test_tnt.tnt
```

**conftest.py**:
```python
import pytest
import os
from peewee import SqliteDatabase
from PfModel import *

# Test database
test_db = SqliteDatabase(':memory:')

@pytest.fixture(scope='function')
def db():
    """Create test database"""
    test_db.bind([PfProject, PfDatamatrix, PfAnalysis, PfTree, PfPackage])
    test_db.connect()
    test_db.create_tables([PfProject, PfDatamatrix, PfAnalysis, PfTree, PfPackage])

    yield test_db

    test_db.drop_tables([PfProject, PfDatamatrix, PfAnalysis, PfTree, PfPackage])
    test_db.close()

@pytest.fixture
def sample_project(db):
    """Create sample project"""
    project = PfProject.create(
        project_name="Test Project",
        project_desc="Test Description"
    )
    return project

@pytest.fixture
def sample_nexus_file():
    """Return path to sample Nexus file"""
    return os.path.join('tests', 'fixtures', 'test_nexus.nex')
```

**체크리스트**:
- [ ] pytest, pytest-qt, pytest-cov 설치
- [ ] tests/ 디렉토리 생성
- [ ] conftest.py 작성
- [ ] fixtures/ 디렉토리 및 테스트 데이터 생성
- [ ] pytest 실행 확인

#### Task 2.1.2: 유틸리티 테스트 작성
**예상 시간**: 4시간
**파일**: `tests/test_utils.py`

**작업 내용**:
```python
import pytest
import json
from PfUtils import *

class TestSafeFileOperations:
    def test_safe_file_read_success(self, tmp_path):
        """Test successful file read"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        content = safe_file_read(str(test_file))
        assert content == "Hello World"

    def test_safe_file_read_not_found(self):
        """Test file not found error"""
        with pytest.raises(FileOperationError):
            safe_file_read("nonexistent.txt")

    def test_safe_file_write_success(self, tmp_path):
        """Test successful file write"""
        test_file = tmp_path / "output.txt"
        safe_file_write(str(test_file), "Test Content")

        assert test_file.read_text() == "Test Content"

    def test_safe_json_loads_valid(self):
        """Test valid JSON parsing"""
        data = safe_json_loads('{"key": "value"}')
        assert data == {"key": "value"}

    def test_safe_json_loads_invalid_with_default(self):
        """Test invalid JSON with default"""
        data = safe_json_loads('invalid json', default={})
        assert data == {}

    def test_safe_json_loads_invalid_no_default(self):
        """Test invalid JSON without default"""
        with pytest.raises(DataParsingError):
            safe_json_loads('invalid json')

class TestPhyloDatafile:
    def test_loadfile_nexus(self, sample_nexus_file):
        """Test Nexus file loading"""
        df = PhyloDatafile()
        result = df.loadfile(sample_nexus_file)

        assert result is True
        assert df.file_type == 'Nexus'
        assert len(df.taxa_list) > 0

    def test_loadfile_nonexistent(self):
        """Test loading nonexistent file"""
        df = PhyloDatafile()
        result = df.loadfile("nonexistent.nex")

        assert result is False

# ... 추가 테스트
```

**체크리스트**:
- [ ] safe_file_read 테스트
- [ ] safe_file_write 테스트
- [ ] safe_json_loads 테스트
- [ ] PhyloDatafile 테스트
- [ ] PhyloTreefile 테스트
- [ ] 커버리지 80% 이상

### Sprint 2.2: 모델 테스트 작성 (Day 8-9)

#### Task 2.2.1: 데이터 모델 테스트
**예상 시간**: 6시간
**파일**: `tests/test_model.py`

**작업 내용**:
```python
import pytest
from PfModel import *

class TestPfProject:
    def test_create_project(self, db):
        """Test project creation"""
        project = PfProject.create(
            project_name="Test Project",
            project_desc="Description"
        )

        assert project.id is not None
        assert project.project_name == "Test Project"

    def test_project_datamatrix_relationship(self, db, sample_project):
        """Test project-datamatrix relationship"""
        dm = PfDatamatrix.create(
            project=sample_project,
            datamatrix_name="Test Matrix",
            n_taxa=10,
            n_chars=20
        )

        assert dm.project.id == sample_project.id
        assert sample_project.datamatrices.count() == 1

class TestPfDatamatrix:
    def test_datamatrix_creation(self, db, sample_project):
        """Test datamatrix creation"""
        dm = PfDatamatrix.create(
            project=sample_project,
            datamatrix_name="Matrix 1",
            n_taxa=5,
            n_chars=10,
            datatype=DATATYPE_MORPHOLOGY
        )

        assert dm.id is not None
        assert dm.n_taxa == 5

    def test_datamatrix_as_list_empty(self, db, sample_project):
        """Test datamatrix_as_list with no data"""
        dm = PfDatamatrix.create(
            project=sample_project,
            datamatrix_name="Empty Matrix",
            n_taxa=0,
            n_chars=0
        )

        result = dm.datamatrix_as_list()
        assert result == []

    def test_datamatrix_as_list_valid(self, db, sample_project):
        """Test datamatrix_as_list with valid JSON"""
        test_data = [["0", "1"], ["1", "0"]]
        dm = PfDatamatrix.create(
            project=sample_project,
            datamatrix_name="Valid Matrix",
            n_taxa=2,
            n_chars=2,
            datamatrix_json=json.dumps(test_data)
        )

        result = dm.datamatrix_as_list()
        assert result == test_data

    def test_copy_datamatrix(self, db, sample_project):
        """Test datamatrix copy"""
        original = PfDatamatrix.create(
            project=sample_project,
            datamatrix_name="Original",
            n_taxa=5,
            n_chars=10
        )

        copy = original.copy()

        assert copy.id != original.id
        assert copy.datamatrix_name == original.datamatrix_name
        assert copy.n_taxa == original.n_taxa

# ... 추가 테스트
```

**체크리스트**:
- [ ] PfProject 테스트
- [ ] PfDatamatrix 테스트
- [ ] PfAnalysis 테스트
- [ ] PfTree 테스트
- [ ] CASCADE 삭제 테스트
- [ ] 커버리지 70% 이상

### Sprint 2.3: UI 테스트 작성 (Day 10)

#### Task 2.3.1: Dialog 테스트
**예상 시간**: 4시간
**파일**: `tests/test_dialogs.py`

**작업 내용**:
```python
import pytest
from pytestqt.qt_compat import qt_api
from PfDialog import *

class TestAnalysisViewer:
    def test_creation(self, qtbot):
        """Test AnalysisViewer creation"""
        viewer = AnalysisViewer()
        qtbot.addWidget(viewer)

        assert viewer.tabview is not None
        assert viewer.tabview.count() == 3  # Info, Log, Trees

    def test_set_analysis(self, qtbot, db, sample_project):
        """Test setting analysis"""
        dm = PfDatamatrix.create(
            project=sample_project,
            datamatrix_name="Test DM",
            n_taxa=5,
            n_chars=10
        )

        analysis = PfAnalysis.create(
            datamatrix=dm,
            analysis_name="Test Analysis",
            analysis_type=ANALYSIS_TYPE_PARSIMONY
        )

        viewer = AnalysisViewer()
        qtbot.addWidget(viewer)
        viewer.set_analysis(analysis)

        assert viewer.edtAnalysisName.text() == "Test Analysis"
        assert viewer.edtAnalysisType.text() == ANALYSIS_TYPE_PARSIMONY

# ... 추가 테스트
```

**체크리스트**:
- [ ] AnalysisViewer 테스트
- [ ] TreeViewer 기본 테스트
- [ ] Dialog 생성 테스트
- [ ] UI 요소 존재 확인

## 🛠️ Phase 3: 개발 경험 개선 (3주차)

### Sprint 3.1: 빌드 자동화 (Day 11-12)

#### Task 3.1.1: PyInstaller spec 파일 생성
**예상 시간**: 2시간

**작업 내용**:

**spec 파일 초안 생성**:
```bash
pyi-makespec --onedir --noconsole \
  --icon="icons/PhyloForester.png" \
  PhyloForester.py
```

**PhyloForester.spec 커스터마이징**:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['PhyloForester.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons/*.png', 'icons'),
        ('data/*.*', 'data'),
        ('translations/*.qm', 'translations'),
        ('migrations/*', 'migrations'),
    ],
    hiddenimports=['peewee_migrate'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PhyloForester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/PhyloForester.png',
    version='version.txt',  # 추가할 버전 정보 파일
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PhyloForester',
)
```

**버전 정보 파일** (`version.txt`):
```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 0, 1, 0),
    prodvers=(0, 0, 1, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'PaleoBytes'),
         StringStruct(u'FileDescription', u'Phylogenetic Analysis Tool'),
         StringStruct(u'FileVersion', u'0.0.1'),
         StringStruct(u'InternalName', u'PhyloForester'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
         StringStruct(u'OriginalFilename', u'PhyloForester.exe'),
         StringStruct(u'ProductName', u'PhyloForester'),
         StringStruct(u'ProductVersion', u'0.0.1')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

**빌드 스크립트**:

**build.sh** (Linux/macOS):
```bash
#!/bin/bash
set -e

echo "Building PhyloForester..."
pyinstaller --clean PhyloForester.spec

echo "Build complete!"
echo "Output: dist/PhyloForester/"
```

**build.bat** (Windows):
```batch
@echo off
echo Building PhyloForester...
pyinstaller --clean PhyloForester.spec

echo Build complete!
echo Output: dist\PhyloForester\
pause
```

**체크리스트**:
- [ ] spec 파일 생성 및 커스터마이징
- [ ] version.txt 작성
- [ ] build.sh 작성 (실행 권한 부여)
- [ ] build.bat 작성
- [ ] 빌드 테스트 (Windows/Linux/macOS)
- [ ] 빌드 결과 검증

#### Task 3.1.2: .gitignore 업데이트
**예상 시간**: 10분

**작업 내용**:
```gitignore
# PyInstaller
build/
dist/
*.spec.bak
version.txt.bak
```

### Sprint 3.2: 나머지 print() 교체 (Day 13-14)

#### Task 3.2.1: PfUtils.py 로깅 교체
**예상 시간**: 3시간
**파일**: `PfUtils.py`

**작업 내용**:
```python
# PfUtils.py 상단에 추가
import logging
logger = logging.getLogger(__name__)

# 예시 (L293, 297)
# Before:
print("interleaved format")
print("sequential format")

# After:
logger.debug("Detected interleaved format")
logger.debug("Detected sequential format")
```

**체크리스트**:
- [ ] PhyloDatafile 클래스 (~10개)
- [ ] PhyloTreefile 클래스 (~5개)
- [ ] 주석 처리된 print 제거

#### Task 3.2.2: 나머지 파일 로깅 교체
**예상 시간**: 3시간
**파일**: `PhyloForester.py`, `PfDialog.py`, `PfModel.py`

**체크리스트**:
- [ ] PhyloForester.py 나머지 (~50개)
- [ ] PfDialog.py (~10개)
- [ ] PfModel.py (~5개)
- [ ] 모든 주석 처리된 print 제거
- [ ] 전체 검색으로 누락 확인

### Sprint 3.3: 번역 업데이트 (Day 15, 선택적)

#### Task 3.3.1: 번역 문자열 추출 및 업데이트
**예상 시간**: 2-3시간

**작업 내용**:
```bash
# 번역 문자열 추출
pylupdate5 PhyloForester.py PfDialog.py \
  -ts translations/PhyloForester_en.ts \
  -ts translations/PhyloForester_ko.ts

# Qt Linguist로 번역 작업
linguist translations/PhyloForester_ko.ts

# 번역 컴파일
lrelease translations/*.ts
```

**체크리스트**:
- [ ] pylupdate5 실행
- [ ] 새 문자열 번역 (한국어)
- [ ] 기존 번역 검토
- [ ] lrelease 컴파일
- [ ] 앱에서 번역 확인

## 📋 전체 체크리스트

### Phase 1: 안정성 확보 (✅/❌)
- [ ] S1.1: 에러 처리 유틸리티
- [ ] S1.2: 파일 I/O 에러 처리
- [ ] S1.3: QProcess 에러 처리
- [ ] S2.1: PfLogger 개선
- [ ] S2.2: Dialog 로거 전달
- [ ] S2.3: 핵심 로직 로깅 교체
- [ ] S3.1: Peewee 에러 처리
- [ ] S3.2: JSON 파싱 에러 처리

### Phase 2: 품질 보증 (✅/❌)
- [ ] Q1.1: 테스트 환경 설정
- [ ] Q1.2: 유틸리티 테스트
- [ ] Q2.1: 모델 테스트
- [ ] Q3.1: Dialog 테스트

### Phase 3: 개발 경험 (✅/❌)
- [ ] D1.1: PyInstaller spec
- [ ] D1.2: 빌드 스크립트
- [ ] D2.1: PfUtils 로깅 교체
- [ ] D2.2: 나머지 로깅 교체
- [ ] D3.1: 번역 업데이트 (선택)

## 🎯 성공 기준

### Phase 1 완료 기준
- [ ] 모든 파일 I/O에 에러 처리 적용
- [ ] QProcess 실행 실패 시 적절한 처리
- [ ] 로깅 시스템 완전 통합
- [ ] 핵심 로직에서 print() 제거 (30개 이상)
- [ ] 크래시 없이 안정적 실행

### Phase 2 완료 기준
- [ ] pytest 실행 성공
- [ ] 유틸리티 테스트 커버리지 80% 이상
- [ ] 모델 테스트 커버리지 70% 이상
- [ ] 최소 20개 이상 테스트 케이스

### Phase 3 완료 기준
- [ ] PyInstaller spec 파일로 빌드 성공
- [ ] 모든 print() 제거 (105개)
- [ ] 로그 파일 정상 생성 확인

## 📊 진행 상황 추적

### Week 1 (안정성)
- Day 1: [ ] S1.1
- Day 2: [ ] S1.2
- Day 3: [ ] S1.3, S2.1
- Day 4: [ ] S2.2, S2.3
- Day 5: [ ] S3.1, S3.2

### Week 2 (품질)
- Day 6: [ ] Q1.1
- Day 7: [ ] Q1.2
- Day 8: [ ] Q2.1
- Day 9: [ ] Q2.1 (계속)
- Day 10: [ ] Q3.1

### Week 3 (경험)
- Day 11: [ ] D1.1
- Day 12: [ ] D1.2
- Day 13: [ ] D2.1
- Day 14: [ ] D2.2
- Day 15: [ ] D3.1 (선택)

## 🔄 리뷰 포인트

각 Sprint 완료 후:
1. 코드 리뷰
2. 테스트 실행
3. 로그 파일 확인
4. 사용자 시나리오 테스트

## 📝 다음 devlog 문서

- `20251023_W01_stability_improvements.md` - 1주차 작업 기록
- `20251023_W02_quality_assurance.md` - 2주차 작업 기록
- `20251023_W03_developer_experience.md` - 3주차 작업 기록

---

**계획 수립일**: 2025-10-23
**예상 기간**: 3주 (15 작업일)
**총 예상 시간**: 60-80 시간
**기반 문서**: `20251023_R01_project_status_and_next_tasks_analysis.md`
