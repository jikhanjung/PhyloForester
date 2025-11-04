# 2025-11-04 P03: PhyloForester Quality Improvement Plan

## 계획 개요

**목표**: PhyloForester 애플리케이션의 전체 품질을 프로덕션 수준으로 향상
**기간**: 3개월 (12주)
**현재 버전**: v0.1.0
**목표 버전**: v0.2.0 (품질 개선 버전)

---

## 📊 현황 분석

### 강점 (Strengths)

✅ **CI/CD 인프라**
- GitHub Actions 워크플로우 완비 (test, build, release, docs)
- 자동화된 테스트 실행 (Python 3.11, 3.12 매트릭스)
- 자동화된 빌드 (Windows, macOS, Linux)
- 자동화된 릴리스 프로세스

✅ **테스트 인프라**
- 82개 테스트 케이스
- pytest 기반 테스트 프레임워크
- pytest-qt, pytest-cov, pytest-mock 통합
- 40% 전체 커버리지

✅ **문서화 시스템**
- Sphinx 기반 문서 (RST 형식)
- 사용자 가이드, 개발자 가이드, 설치 가이드
- 문제 해결 가이드 (troubleshooting)
- GitHub Pages 자동 배포

✅ **버전 관리 체계**
- Semantic versioning (semver)
- 자동 버전 관리 (manage_version.py)
- devlog 문서화 시스템
- Changelog 관리

### 약점 (Weaknesses)

❌ **코드 품질 도구 부재**
- Ruff 설정 파일 없음 (CI에서는 실행하지만 continue-on-error: true)
- Type hints 없음 (0%)
- Linting 규칙 미정의
- Pre-commit hooks 없음

❌ **낮은 테스트 커버리지**
- PhyloForester.py: 0% (1564 lines, 메인 GUI)
- PfDialog.py: 48% (2160 lines, 다이얼로그)
- PfUtils.py: 61% (571 lines, 유틸리티)
- PfModel.py: 83% (335 lines, 데이터베이스) ✓ 양호
- PfLogger.py: 96% (26 lines, 로깅) ✓ 우수

❌ **에러 핸들링 부족**
- 전역 exception handler 없음
- 일부 함수에서 예외 처리 누락
- 사용자 친화적 에러 메시지 부족

❌ **문서화 불완전**
- Docstring 일부 누락
- API 문서 자동 생성 안 됨
- Type hints 없어서 IDE 지원 제한적

❌ **성능 최적화 미흡**
- 프로파일링 미실시
- 대용량 데이터 처리 최적화 없음
- UI 반응성 개선 여지 (일부 무거운 작업이 메인 스레드)

### 기회 (Opportunities)

🎯 **개발 환경 개선**
- VS Code/PyCharm 설정 제공으로 개발자 경험 향상
- Docker 개발 환경으로 의존성 관리 간소화
- Task runner로 일상적인 작업 자동화

🎯 **보안 강화**
- Bandit, Safety로 보안 취약점 사전 감지
- 코드 서명으로 신뢰성 향상

🎯 **사용자 경험 개선**
- 더 나은 도움말 시스템
- 접근성 개선
- 국제화 완성도 향상

### 위험 요소 (Threats)

⚠️ **기술 부채 증가**
- 테스트 없이 기능 추가 시 버그 증가 위험
- Type hints 없어서 리팩토링 어려움

⚠️ **유지보수성 저하**
- 코드 복잡도 관리 필요
- 문서화 부족으로 신규 개발자 온보딩 어려움

---

## 🎯 목표 및 성공 지표

### 3개월 후 목표

| 항목 | 현재 | 목표 | 측정 방법 |
|------|------|------|----------|
| **테스트 커버리지** | 40% | 60%+ | pytest --cov |
| **Type Hint 커버리지** | 0% | 80%+ | mypy --strict |
| **Linting 통과율** | ~70% (추정) | 100% | ruff check |
| **문서화** | 60% | 90%+ | 수동 검토 |
| **보안 취약점** | 미확인 | 0개 | bandit, safety |
| **코드 복잡도** | 미측정 | <10 (평균) | radon cc |
| **빌드 성공률** | 95% | 100% | GitHub Actions |
| **릴리스 주기** | 수동 | 자동화 | CI/CD |

### KPI (핵심 성과 지표)

1. **품질 지표**
   - 전체 테스트 통과율: 100%
   - Critical 버그 수: 0개
   - 코드 리뷰 적용률: 100%

2. **개발 생산성 지표**
   - PR 평균 처리 시간: < 2일
   - CI/CD 파이프라인 성공률: > 95%
   - 문서화된 API 비율: > 90%

3. **사용자 만족도 지표**
   - 크래시 없는 실행: 99%+
   - 응답 시간: < 2초 (일반적인 작업)
   - 에러 메시지 이해도: 설문 조사

---

## 📅 Phase 1: 코드 품질 기반 구축 (Week 1-2)

### 목표
코드 품질 도구를 설정하고 기존 코드에 적용하여 일관성 있는 코드베이스 구축

### Sprint 1.1: Ruff 설정 및 코드 스타일 통일 (Week 1, Day 1-3)

#### Task 1.1.1: pyproject.toml 생성 및 Ruff 규칙 설정
**예상 시간**: 2시간
**담당**: Developer
**우선순위**: Critical

**작업 내용**:
1. `pyproject.toml` 파일 생성
2. Ruff 규칙 설정
3. 프로젝트별 예외 규칙 정의

**설정 예시**:
```toml
[tool.ruff]
target-version = "py38"
line-length = 100

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "RET",  # flake8-return
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # unused imports
"tests/**/*.py" = ["S101"]  # use of assert

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**검증 방법**:
```bash
ruff check .
ruff format --check .
```

**완료 기준**:
- [ ] pyproject.toml 파일 생성
- [ ] Ruff 규칙 정의 완료
- [ ] 로컬에서 ruff check 실행 가능

---

#### Task 1.1.2: 기존 코드 Ruff 규칙 적용
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Critical

**작업 내용**:
1. 자동 수정 가능한 항목 일괄 적용
2. 수동 수정 필요한 항목 리스트업
3. 모듈별로 순차적으로 수정

**실행 순서**:
```bash
# 1. 자동 수정 (안전한 항목만)
ruff check --fix .

# 2. 포맷팅 적용
ruff format .

# 3. 남은 이슈 확인
ruff check .
```

**수동 수정 우선순위**:
1. PfLogger.py (26 lines, 작음)
2. version.py (4 lines, 작음)
3. PfModel.py (335 lines, 중요)
4. PfUtils.py (571 lines)
5. PfDialog.py (2160 lines, 대형)
6. PhyloForester.py (1564 lines, 대형)

**완료 기준**:
- [ ] 모든 모듈에서 ruff check 통과
- [ ] 모든 모듈에서 ruff format 통과
- [ ] 코드 동작 검증 (기존 테스트 통과)

---

#### Task 1.1.3: Pre-commit hooks 설정
**예상 시간**: 1시간
**담당**: Developer
**우선순위**: High

**작업 내용**:
1. `.pre-commit-config.yaml` 파일 생성
2. pre-commit 설치 및 활성화
3. 개발자 가이드 업데이트

**설정 파일**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-case-conflict

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ['-x', '--tb=short']
        stages: [commit]
```

**설치 가이드** (developer_guide.rst 추가):
```bash
# Pre-commit 설치
pip install pre-commit

# Hook 활성화
pre-commit install

# 모든 파일에 대해 실행 (최초 1회)
pre-commit run --all-files
```

**완료 기준**:
- [ ] .pre-commit-config.yaml 생성
- [ ] 로컬에서 pre-commit 동작 확인
- [ ] 개발자 가이드 업데이트

---

#### Task 1.1.4: CI에서 Ruff 강제 적용
**예상 시간**: 30분
**담당**: Developer
**우선순위**: High

**작업 내용**:
`.github/workflows/test.yml` 수정:

```yaml
# Before:
- name: Lint with Ruff
  run: |
    ruff check . --output-format=github
  continue-on-error: true

# After:
- name: Lint with Ruff
  run: |
    ruff check . --output-format=github
  # Ruff 실패 시 빌드 실패 (continue-on-error 제거)

- name: Check formatting with Ruff
  run: |
    ruff format --check .
```

**완료 기준**:
- [ ] CI에서 Ruff 실패 시 빌드 실패
- [ ] 포맷팅 체크 추가
- [ ] main 브랜치 보호 규칙 업데이트

**예상 효과**:
- 모든 PR에서 코드 스타일 자동 검증
- 코드 리뷰 시간 단축
- 코드 일관성 향상

---

### Sprint 1.2: Type Hints 추가 (Week 1-2, Day 4-7)

#### Task 1.2.1: 개발 도구 설정
**예상 시간**: 1시간
**담당**: Developer
**우선순위**: High

**작업 내용**:
1. mypy 설치 및 설정
2. pyproject.toml에 mypy 설정 추가
3. CI에 mypy 통합

**mypy 설정** (pyproject.toml):
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # 초기에는 false, 점진적으로 true로
ignore_missing_imports = true  # 외부 라이브러리 import 에러 무시

# 모듈별 엄격도 설정
[[tool.mypy.overrides]]
module = "PfLogger"
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "PfModel"
disallow_untyped_defs = true
```

**CI 통합** (.github/workflows/test.yml):
```yaml
- name: Type check with mypy
  run: |
    mypy PfLogger.py PfModel.py --strict
  continue-on-error: true  # 초기에는 경고만
```

**완료 기준**:
- [ ] mypy 설치 및 설정 완료
- [ ] 로컬에서 mypy 실행 가능
- [ ] CI에 mypy 단계 추가

---

#### Task 1.2.2: PfLogger.py Type Hints 추가
**예상 시간**: 1시간
**담당**: Developer
**우선순위**: High
**난이도**: Easy (26 lines, 96% coverage)

**작업 내용**:
```python
# Before:
def setup_logger(name, log_file=None, level=logging.INFO):
    logger = logging.getLogger(name)
    # ...
    return logger

# After:
from typing import Optional
import logging

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """Set up logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    # ...
    return logger
```

**완료 기준**:
- [ ] 모든 함수에 type hints 추가
- [ ] mypy --strict 통과
- [ ] Docstring 업데이트

---

#### Task 1.2.3: PfModel.py Type Hints 추가
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: High
**난이도**: Medium (335 lines, 83% coverage)

**작업 내용**:
Peewee 모델 클래스에 type hints 추가

```python
from typing import Optional, List, Dict, Any
from peewee import Model, CharField, IntegerField, DateTimeField
from datetime import datetime

class PfProject(Model):
    """Project model for phylogenetic analysis projects."""

    project_name: CharField = CharField(max_length=255)
    project_desc: CharField = CharField(max_length=1000, null=True)
    created_at: DateTimeField = DateTimeField(default=datetime.now)
    modified_at: DateTimeField = DateTimeField(default=datetime.now)

    def get_datamatrices(self) -> List['PfDatamatrix']:
        """Get all datamatrices associated with this project.

        Returns:
            List of PfDatamatrix instances
        """
        return list(self.datamatrices)  # type: ignore
```

**Peewee 관련 주의사항**:
- Peewee 필드는 descriptor이므로 타입 지정이 까다로움
- `# type: ignore` 주석 필요한 경우 있음
- 가능한 한 메서드 반환 타입에 집중

**완료 기준**:
- [ ] 모든 모델 클래스 필드 타입 정의
- [ ] 모든 메서드 시그니처 타입 추가
- [ ] mypy 통과 (일부 ignore 허용)
- [ ] 테스트 통과 (test_model.py)

---

#### Task 1.2.4: PfUtils.py 주요 함수 Type Hints 추가
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Medium
**난이도**: Medium (571 lines, 61% coverage)

**작업 내용**:
주요 유틸리티 함수부터 시작 (우선순위순):

1. **경로 관리 함수**:
```python
def get_default_result_directory_path() -> str:
    """Get default result directory path without creating it.

    Returns:
        Path string to default result directory
    """
    # ...

def create_result_directory(path: str) -> bool:
    """Create result directory with permission testing.

    Args:
        path: Directory path to create

    Returns:
        True if successful, False otherwise
    """
    # ...
```

2. **파일 파서 클래스**:
```python
from typing import List, Dict, Tuple, Optional

class PhyloDatafile:
    """Parser for phylogenetic data files (Nexus, Phylip, TNT)."""

    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.taxa_list: List[str] = []
        self.datamatrix: List[List[str]] = []
        # ...

    def parse_nexus(self) -> Tuple[List[str], List[List[str]]]:
        """Parse Nexus format file.

        Returns:
            Tuple of (taxa_list, datamatrix)
        """
        # ...
```

3. **Fitch 알고리즘**:
```python
def fitch_algorithm(
    tree: Any,  # Newick tree object
    character_states: Dict[str, str]
) -> Dict[str, str]:
    """Run Fitch algorithm for ancestral state reconstruction.

    Args:
        tree: Phylogenetic tree object
        character_states: Character states for leaf nodes

    Returns:
        Dictionary mapping node names to reconstructed states
    """
    # ...
```

**점진적 적용 전략**:
- 새로운 함수: 100% type hints
- 기존 함수: 공개 API부터 우선 적용
- 복잡한 내부 함수: 나중에 적용

**완료 기준**:
- [ ] 모든 공개 함수 type hints 추가
- [ ] 주요 클래스 type hints 추가
- [ ] mypy 에러 50% 감소
- [ ] 기존 테스트 통과

---

#### Task 1.2.5: PfDialog.py 주요 클래스 Type Hints 추가
**예상 시간**: 2일
**담당**: Developer
**우선순위**: Medium
**난이도**: Hard (2160 lines, 대형 파일)

**작업 내용**:
크기가 크므로 클래스별로 분할 작업

**우선순위 1: Dialog 클래스**
```python
from typing import Optional
from PyQt5.QtWidgets import QDialog, QWidget

class ProjectDialog(QDialog):
    """Dialog for creating/editing projects."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        super().__init__(parent)
        self.parent: Optional[QWidget] = parent
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        # ...

    def get_project_data(self) -> Dict[str, Any]:
        """Get project data from dialog fields.

        Returns:
            Dictionary with project_name, project_desc, etc.
        """
        # ...
```

**우선순위 2: Viewer 클래스**
```python
class AnalysisViewer(QWidget):
    """Viewer widget for analysis results."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        # ...

    def load_analysis(self, analysis: 'PfAnalysis') -> None:
        """Load analysis data into viewer.

        Args:
            analysis: PfAnalysis model instance
        """
        # ...
```

**점진적 적용**:
- Week 1: Dialog 생성자 및 주요 메서드
- Week 2: Viewer 클래스
- Week 3: Helper 메서드

**완료 기준**:
- [ ] 모든 Dialog 클래스 생성자 타입 추가
- [ ] 모든 Viewer 클래스 생성자 타입 추가
- [ ] 주요 공개 메서드 타입 추가 (50%+)
- [ ] mypy 에러 30% 감소

---

### Sprint 1.3: Docstring 표준화 (Week 2, Day 3-5)

#### Task 1.3.1: Docstring 스타일 선택 및 설정
**예상 시간**: 1시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:
1. Google Style vs NumPy Style 선택
2. Sphinx 확장 설정
3. 예시 템플릿 작성

**권장**: Google Style (간결하고 읽기 쉬움)

**Sphinx 설정** (docs/conf.py):
```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Google/NumPy style docstring 지원
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
```

**Google Style 템플릿**:
```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Short description in one line.

    Longer description can span multiple lines. Explain what
    the function does, any important details about its behavior,
    and usage examples if helpful.

    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 0.

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        IOError: When file cannot be read

    Example:
        >>> example_function("test", 42)
        True
    """
    # ...
```

**완료 기준**:
- [ ] Docstring 스타일 결정
- [ ] Sphinx 설정 업데이트
- [ ] 템플릿 문서 작성

---

#### Task 1.3.2: PfModel.py Docstring 추가
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: High

**작업 내용**:
모든 모델 클래스와 메서드에 docstring 추가

```python
class PfProject(Model):
    """Phylogenetic analysis project.

    Represents a top-level project that contains multiple datamatrices.
    Each project tracks creation and modification times.

    Attributes:
        project_name: Unique name for the project
        project_desc: Optional description
        created_at: Creation timestamp
        modified_at: Last modification timestamp

    Relationships:
        datamatrices: One-to-many relationship with PfDatamatrix
    """

    project_name = CharField(max_length=255, unique=True)
    project_desc = CharField(max_length=1000, null=True)
    created_at = DateTimeField(default=datetime.now)
    modified_at = DateTimeField(default=datetime.now)

    def get_datamatrices(self) -> List['PfDatamatrix']:
        """Get all datamatrices in this project.

        Returns:
            List of PfDatamatrix instances ordered by index

        Example:
            >>> project = PfProject.get(project_name="My Project")
            >>> matrices = project.get_datamatrices()
            >>> len(matrices)
            3
        """
        return list(
            PfDatamatrix.select()
            .where(PfDatamatrix.project == self)
            .order_by(PfDatamatrix.datamatrix_index)
        )
```

**완료 기준**:
- [ ] 모든 모델 클래스 docstring 추가
- [ ] 모든 메서드 docstring 추가
- [ ] Sphinx로 문서 생성 확인

---

#### Task 1.3.3: PfUtils.py Docstring 추가
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Medium

**작업 내용**:
주요 유틸리티 함수와 클래스에 docstring 추가

**우선순위**:
1. 공개 API 함수 (100%)
2. 클래스 및 클래스 메서드 (100%)
3. 내부 helper 함수 (50%+)

**완료 기준**:
- [ ] 모든 공개 함수 docstring 추가
- [ ] 모든 클래스 docstring 추가
- [ ] 복잡한 알고리즘 상세 설명 추가

---

#### Task 1.3.4: API 문서 자동 생성
**예상 시간**: 2시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:
1. API 문서 RST 파일 생성
2. Sphinx autodoc 활용
3. GitHub Pages 업데이트

**API 문서 구조** (docs/api.rst):
```rst
API Reference
=============

.. toctree::
   :maxdepth: 2

   api/model
   api/dialog
   api/utils
   api/logger

Models (PfModel)
----------------

.. automodule:: PfModel
   :members:
   :undoc-members:
   :show-inheritance:

Dialogs (PfDialog)
------------------

.. automodule:: PfDialog
   :members:
   :undoc-members:
   :show-inheritance:

Utilities (PfUtils)
-------------------

.. automodule:: PfUtils
   :members:
   :undoc-members:
   :show-inheritance:

Logger (PfLogger)
-----------------

.. automodule:: PfLogger
   :members:
   :undoc-members:
   :show-inheritance:
```

**완료 기준**:
- [ ] API 문서 자동 생성 설정
- [ ] 로컬에서 문서 빌드 확인
- [ ] GitHub Pages에 배포
- [ ] 인덱스 페이지에서 링크 추가

---

### Phase 1 완료 기준 및 검증

**완료 기준**:
- [x] Ruff 설정 완료 및 CI 통합
- [x] Pre-commit hooks 설정
- [x] PfLogger, PfModel type hints 100%
- [x] PfUtils type hints 80%+
- [x] PfDialog type hints 50%+
- [x] 모든 공개 API docstring 추가
- [x] API 문서 자동 생성

**검증 방법**:
```bash
# 1. Linting
ruff check .
ruff format --check .

# 2. Type checking
mypy PfLogger.py PfModel.py --strict
mypy PfUtils.py --strict

# 3. 문서 빌드
cd docs
make html

# 4. 테스트
pytest tests/ -v
```

**예상 효과**:
- 코드 일관성 100%
- Type hint 커버리지 0% → 70%+
- API 문서 자동화
- 개발자 경험 향상 (IDE 자동완성)

---

## 📅 Phase 2: 테스트 커버리지 확대 (Week 3-5)

### 목표
전체 테스트 커버리지를 40%에서 60%+로 향상시켜 리팩토링 안전성 확보

### Sprint 2.1: PfUtils.py 테스트 확대 (Week 3)

#### Task 2.1.1: 파일 파서 테스트 추가
**예상 시간**: 1일
**담당**: Developer
**우선순위**: High
**현재 커버리지**: 61% → **목표**: 80%

**작업 내용**:

**1. Nexus 파서 테스트**:
```python
# tests/test_utils_parser.py
import pytest
from PfUtils import PhyloDatafile

class TestNexusParser:
    """Tests for Nexus format parser"""

    def test_parse_simple_nexus(self, sample_nexus_file):
        """Test parsing simple Nexus file"""
        parser = PhyloDatafile(sample_nexus_file)
        taxa, matrix = parser.parse_nexus()

        assert len(taxa) == 3
        assert taxa == ["Taxon_A", "Taxon_B", "Taxon_C"]
        assert len(matrix) == 3
        assert matrix[0] == ["0", "1", "0"]

    def test_parse_nexus_with_gaps(self, nexus_with_gaps):
        """Test parsing Nexus with gap characters"""
        parser = PhyloDatafile(nexus_with_gaps)
        taxa, matrix = parser.parse_nexus()

        # Gaps should be preserved as "-"
        assert "-" in matrix[0]

    def test_parse_nexus_with_polymorphism(self, nexus_with_polymorphism):
        """Test parsing Nexus with polymorphic characters"""
        parser = PhyloDatafile(nexus_with_polymorphism)
        taxa, matrix = parser.parse_nexus()

        # Polymorphisms should be stored as lists
        assert isinstance(matrix[0][0], list)
        assert set(matrix[0][0]) == {"0", "1"}

    def test_parse_nexus_missing_data(self, nexus_with_missing):
        """Test parsing Nexus with missing data"""
        parser = PhyloDatafile(nexus_with_missing)
        taxa, matrix = parser.parse_nexus()

        # Missing data should be "?"
        assert "?" in matrix[1]

    def test_parse_malformed_nexus(self):
        """Test error handling for malformed Nexus"""
        with pytest.raises(ValueError):
            parser = PhyloDatafile("nonexistent.nex")
            parser.parse_nexus()
```

**2. Phylip 파서 테스트**:
```python
class TestPhylipParser:
    """Tests for Phylip format parser"""

    def test_parse_sequential_phylip(self, sequential_phylip):
        """Test parsing sequential Phylip format"""
        parser = PhyloDatafile(sequential_phylip)
        taxa, matrix = parser.parse_phylip()

        assert len(taxa) == 3
        assert len(matrix) == 3

    def test_parse_interleaved_phylip(self, interleaved_phylip):
        """Test parsing interleaved Phylip format"""
        parser = PhyloDatafile(interleaved_phylip)
        taxa, matrix = parser.parse_phylip()

        # Should produce same result as sequential
        assert len(taxa) == 3
        assert len(matrix) == 3

    def test_detect_phylip_format(self, sequential_phylip):
        """Test automatic format detection"""
        parser = PhyloDatafile(sequential_phylip)
        format_type = parser.detect_format()

        assert format_type == "phylip"
```

**3. TNT 파서 테스트**:
```python
class TestTNTParser:
    """Tests for TNT format parser"""

    def test_parse_tnt_xread(self, tnt_xread_file):
        """Test parsing TNT xread format"""
        parser = PhyloDatafile(tnt_xread_file)
        taxa, matrix = parser.parse_tnt()

        assert len(taxa) == 3
        assert len(matrix) == 3

    def test_tnt_special_characters(self, tnt_with_special):
        """Test TNT format with special characters"""
        parser = PhyloDatafile(tnt_with_special)
        taxa, matrix = parser.parse_tnt()

        # Test handling of brackets, etc.
        assert "[" not in str(matrix)
```

**Fixtures 추가** (conftest.py):
```python
@pytest.fixture
def nexus_with_gaps(temp_dir):
    """Nexus file with gap characters"""
    content = """#NEXUS
begin data;
dimensions ntax=3 nchar=5;
format datatype=standard gap=- missing=?;
matrix
Taxon_A 01-10
Taxon_B 10?01
Taxon_C 01010
;
end;
"""
    path = os.path.join(temp_dir, "gaps.nex")
    with open(path, 'w') as f:
        f.write(content)
    return path

@pytest.fixture
def nexus_with_polymorphism(temp_dir):
    """Nexus file with polymorphic characters"""
    content = """#NEXUS
begin data;
dimensions ntax=3 nchar=3;
format datatype=standard;
matrix
Taxon_A (01)10
Taxon_B 0(12)0
Taxon_C 001
;
end;
"""
    path = os.path.join(temp_dir, "poly.nex")
    with open(path, 'w') as f:
        f.write(content)
    return path
```

**완료 기준**:
- [ ] Nexus 파서 테스트 10개 이상
- [ ] Phylip 파서 테스트 8개 이상
- [ ] TNT 파서 테스트 6개 이상
- [ ] Edge cases 커버 (빈 파일, 잘못된 형식, 특수 문자)
- [ ] 커버리지 80% 달성

---

#### Task 2.1.2: Fitch 알고리즘 테스트 추가
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: High

**작업 내용**:

```python
# tests/test_utils_fitch.py
import pytest
from PfUtils import fitch_algorithm

class TestFitchAlgorithm:
    """Tests for Fitch ancestral state reconstruction"""

    def test_fitch_simple_tree(self):
        """Test Fitch on simple 3-taxon tree"""
        tree = "((A:1,B:1)AB:1,C:2);"
        states = {"A": "0", "B": "0", "C": "1"}

        result = fitch_algorithm(tree, states)

        # Internal node AB should be "0"
        assert result["AB"] == "0"
        # Root should be ambiguous or optimized
        assert result["root"] in ["0", "1"]

    def test_fitch_polymorphic_characters(self):
        """Test Fitch with polymorphic characters"""
        tree = "((A:1,B:1)AB:1,C:2);"
        states = {"A": ["0", "1"], "B": "1", "C": "1"}

        result = fitch_algorithm(tree, states)

        assert result["AB"] == "1"

    def test_fitch_missing_data(self):
        """Test Fitch with missing data"""
        tree = "((A:1,B:1)AB:1,C:2);"
        states = {"A": "?", "B": "1", "C": "0"}

        result = fitch_algorithm(tree, states)

        # Should handle missing data gracefully
        assert "AB" in result

    def test_fitch_large_tree(self):
        """Test Fitch on larger tree (10 taxa)"""
        # Create larger test case
        tree = "(((A:1,B:1)AB:1,(C:1,D:1)CD:1)ABCD:1,((E:1,F:1)EF:1,(G:1,H:1)GH:1)EFGH:1,(I:1,J:1)IJ:1);"
        states = {
            "A": "0", "B": "0", "C": "1", "D": "1",
            "E": "0", "F": "1", "G": "1", "H": "1",
            "I": "0", "J": "0"
        }

        result = fitch_algorithm(tree, states)

        # Verify all internal nodes reconstructed
        assert len(result) > len(states)
```

**완료 기준**:
- [ ] 기본 기능 테스트 5개
- [ ] Edge case 테스트 3개
- [ ] 성능 테스트 1개 (대형 트리)
- [ ] Fitch 알고리즘 커버리지 90%+

---

#### Task 2.1.3: 경로 처리 함수 Edge Case 테스트
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

```python
# tests/test_utils_paths.py
import pytest
import platform
from unittest.mock import patch, MagicMock
from PfUtils import (
    get_default_result_directory_path,
    create_result_directory,
    get_available_windows_drives
)

class TestPathHandling:
    """Tests for path handling utilities"""

    def test_default_path_windows(self):
        """Test default path on Windows"""
        with patch('platform.system', return_value='Windows'):
            with patch('PfUtils.get_available_windows_drives', return_value=['C', 'D']):
                path = get_default_result_directory_path()
                assert path.startswith('C:\\') or path.startswith('D:\\')

    def test_default_path_unix(self):
        """Test default path on Unix"""
        with patch('platform.system', return_value='Linux'):
            path = get_default_result_directory_path()
            assert 'PFResults' in path
            assert not path.startswith('C:')

    def test_create_directory_success(self, temp_dir):
        """Test successful directory creation"""
        target = os.path.join(temp_dir, "test_results")
        result = create_result_directory(target)

        assert result is True
        assert os.path.exists(target)

    def test_create_directory_permission_denied(self):
        """Test directory creation with no permissions"""
        # Mock permission error
        with patch('os.makedirs', side_effect=PermissionError):
            result = create_result_directory("/root/forbidden")
            assert result is False

    def test_create_directory_already_exists(self, temp_dir):
        """Test creating directory that already exists"""
        # Should succeed without error
        result = create_result_directory(temp_dir)
        assert result is True

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_get_available_drives_windows(self):
        """Test drive enumeration on Windows"""
        drives = get_available_windows_drives()

        assert isinstance(drives, list)
        assert len(drives) > 0
        assert 'C' in drives  # C: almost always exists

    def test_get_available_drives_unix(self):
        """Test drive enumeration returns empty on Unix"""
        with patch('platform.system', return_value='Linux'):
            drives = get_available_windows_drives()
            assert drives == []
```

**완료 기준**:
- [ ] 플랫폼별 테스트 (Windows, Linux, macOS)
- [ ] 권한 에러 시나리오
- [ ] 경로 정규화 테스트
- [ ] 경로 처리 함수 커버리지 85%+

---

### Sprint 2.2: PfDialog.py 테스트 확대 (Week 4)

#### Task 2.2.1: PreferencesDialog 테스트 추가
**예상 시간**: 1일
**담당**: Developer
**우선순위**: High

**작업 내용**:

```python
# tests/test_dialog_preferences.py
import pytest
from PyQt5.QtCore import QSettings
from PfDialog import PreferencesDialog
import PfUtils as pu

class TestPreferencesDialog:
    """Tests for PreferencesDialog"""

    def test_load_default_settings(self, qapp):
        """Test loading default settings"""
        dialog = PreferencesDialog(parent=None)

        # Should load default paths
        assert dialog.ledResultPath.text() == pu.DEFAULT_RESULT_DIRECTORY
        assert dialog.ledTNT.text() == ""
        assert dialog.ledIQTree.text() == ""

    def test_save_settings(self, qapp):
        """Test saving settings to QSettings"""
        dialog = PreferencesDialog(parent=None)

        # Set paths
        dialog.ledTNT.setText("/usr/bin/tnt")
        dialog.ledResultPath.setText("/tmp/results")

        # Accept dialog (triggers save)
        dialog.accept()

        # Verify saved to QSettings
        assert qapp.settings.value("SoftwarePath/TNT") == "/usr/bin/tnt"
        assert qapp.settings.value("ResultPath") == "/tmp/results"

    def test_browse_tnt_path(self, qapp, qtbot, monkeypatch):
        """Test browsing for TNT path"""
        dialog = PreferencesDialog(parent=None)

        # Mock file dialog
        monkeypatch.setattr(
            'PyQt5.QtWidgets.QFileDialog.getOpenFileName',
            lambda *args, **kwargs: ("/usr/bin/tnt", "")
        )

        # Click browse button
        qtbot.mouseClick(dialog.pbtnBrowseTNT, Qt.LeftButton)

        # Path should be updated
        assert dialog.ledTNT.text() == "/usr/bin/tnt"

    def test_path_normalization(self, qapp):
        """Test path normalization on save"""
        dialog = PreferencesDialog(parent=None)

        # Set path with mixed separators
        dialog.ledResultPath.setText("C:/Users\\Test/Results")
        dialog.accept()

        # Should be normalized
        saved = qapp.settings.value("ResultPath")
        assert "\\" not in saved or "/" not in saved  # Only one separator type
```

**완료 기준**:
- [ ] 설정 로드 테스트 3개
- [ ] 설정 저장 테스트 3개
- [ ] 파일 다이얼로그 테스트 3개
- [ ] PreferencesDialog 커버리지 70%+

---

#### Task 2.2.2: AnalysisDialog 검증 로직 테스트
**예상 시간**: 1일
**담당**: Developer
**우선순위**: High

**작업 내용**:

```python
# tests/test_dialog_analysis.py
import pytest
from PfDialog import AnalysisDialog
from PfModel import ANALYSIS_TYPE_PARSIMONY, ANALYSIS_TYPE_ML

class TestAnalysisDialog:
    """Tests for AnalysisDialog validation logic"""

    def test_checkbox_disabled_when_software_missing(self, qapp):
        """Test checkboxes disabled when software not configured"""
        # TNT not configured
        qapp.tnt_path = ""

        dialog = AnalysisDialog(parent=None)

        # Parsimony checkbox should be disabled
        assert not dialog.cbxParsimony.isEnabled()
        assert "TNT" in dialog.cbxParsimony.toolTip()

    def test_checkbox_enabled_when_software_configured(self, qapp):
        """Test checkboxes enabled when software configured"""
        qapp.tnt_path = "/usr/bin/tnt"

        dialog = AnalysisDialog(parent=None)

        # Parsimony checkbox should be enabled
        assert dialog.cbxParsimony.isEnabled()

    def test_validate_no_analysis_selected(self, qapp):
        """Test validation fails when no analysis selected"""
        dialog = AnalysisDialog(parent=None)

        # Don't check any checkbox
        dialog.cbxParsimony.setChecked(False)
        dialog.cbxML.setChecked(False)

        # Should fail validation
        assert not dialog.validate()

    def test_validate_analysis_selected(self, qapp):
        """Test validation passes when analysis selected"""
        qapp.tnt_path = "/usr/bin/tnt"
        dialog = AnalysisDialog(parent=None)

        # Check parsimony
        dialog.cbxParsimony.setChecked(True)

        # Should pass validation
        assert dialog.validate()

    def test_result_directory_creation(self, qapp, temp_dir):
        """Test result directory field"""
        qapp.result_path = temp_dir
        dialog = AnalysisDialog(parent=None)

        # Should suggest path under result_path
        suggested = dialog.get_suggested_result_directory()
        assert suggested.startswith(temp_dir)
```

**완료 기준**:
- [ ] 검증 로직 테스트 5개
- [ ] UI 상태 테스트 4개
- [ ] 경로 처리 테스트 3개
- [ ] AnalysisDialog 커버리지 60%+

---

#### Task 2.2.3: TreeViewer 렌더링 로직 테스트
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

```python
# tests/test_dialog_treeviewer.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from PfDialog import TreeViewer

class TestTreeViewer:
    """Tests for TreeViewer rendering logic"""

    def test_load_newick_tree(self, qapp):
        """Test loading Newick format tree"""
        viewer = TreeViewer()
        newick = "((A:1,B:1)AB:1,C:2);"

        viewer.load_tree(newick)

        # Should parse tree
        assert viewer.tree is not None

    @patch('matplotlib.pyplot.savefig')
    def test_render_tree_to_svg(self, mock_savefig, qapp):
        """Test rendering tree to SVG"""
        viewer = TreeViewer()
        newick = "((A:1,B:1)AB:1,C:2);"

        viewer.load_tree(newick)
        viewer.render()

        # Should call savefig
        assert mock_savefig.called

    def test_character_mapping_overlay(self, qapp):
        """Test character state mapping on tree"""
        viewer = TreeViewer()
        newick = "((A:1,B:1)AB:1,C:2);"
        character_states = {"A": "0", "B": "1", "C": "0"}

        viewer.load_tree(newick)
        viewer.set_character_mapping(character_states)

        # Should store character states
        assert viewer.character_states == character_states

    def test_invalid_newick(self, qapp):
        """Test error handling for invalid Newick"""
        viewer = TreeViewer()

        with pytest.raises(ValueError):
            viewer.load_tree("invalid((newick")
```

**완료 기준**:
- [ ] 트리 로딩 테스트 3개
- [ ] 렌더링 테스트 3개 (mock 사용)
- [ ] 문자 매핑 테스트 2개
- [ ] 에러 처리 테스트 2개
- [ ] TreeViewer 커버리지 60%+

---

### Sprint 2.3: PhyloForester.py 주요 로직 테스트 (Week 5)

#### Task 2.3.1: 데이터 저장소 로직 테스트
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Medium
**목표**: 0% → 30%

**작업 내용**:

```python
# tests/test_main_datastorage.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt5.QtWidgets import QApplication
import sys

# PhyloForester.py의 주요 로직만 테스트 (GUI 제외)

class TestDataStorage:
    """Tests for data_storage management logic"""

    @patch('PhyloForester.PhyloForesterMainWindow')
    def test_initialize_data_storage(self, mock_window):
        """Test data_storage initialization"""
        # data_storage는 딕셔너리로 초기화되어야 함
        window = mock_window()
        window.data_storage = {}

        assert isinstance(window.data_storage, dict)
        assert 'project' in window.data_storage or len(window.data_storage) == 0

    @patch('PhyloForester.PhyloForesterMainWindow')
    def test_add_project_to_storage(self, mock_window):
        """Test adding project to data_storage"""
        window = mock_window()
        window.data_storage = {'project': {}}

        project_id = 1
        project_obj = Mock()

        # Add project
        window.data_storage['project'][project_id] = {
            'object': project_obj,
            'widget': None,
            'tree_item': None,
            'datamatrix': {}
        }

        # Verify structure
        assert project_id in window.data_storage['project']
        assert window.data_storage['project'][project_id]['object'] == project_obj

    @patch('PhyloForester.PhyloForesterMainWindow')
    def test_cascade_delete_project(self, mock_window):
        """Test cascading delete of project removes datamatrices"""
        window = mock_window()
        window.data_storage = {
            'project': {
                1: {
                    'object': Mock(),
                    'datamatrix': {
                        10: {'object': Mock()},
                        11: {'object': Mock()}
                    }
                }
            }
        }

        # Delete project
        del window.data_storage['project'][1]

        # Project should be removed
        assert 1 not in window.data_storage['project']
```

**주의사항**:
- GUI 위젯 생성 없이 로직만 테스트
- Mock을 활용하여 의존성 분리
- 핵심 비즈니스 로직에 집중

**완료 기준**:
- [ ] data_storage 초기화 테스트 2개
- [ ] 프로젝트 추가/삭제 테스트 4개
- [ ] 데이터매트릭스 추가/삭제 테스트 4개
- [ ] 분석 추가/삭제 테스트 4개

---

#### Task 2.3.2: 프로젝트/데이터매트릭스/분석 생성 플로우 테스트
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Low

**작업 내용**:

```python
# tests/test_main_workflow.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from PfModel import PfProject, PfDatamatrix, PfAnalysis

class TestWorkflow:
    """Tests for creation workflows"""

    def test_create_project_workflow(self, test_db):
        """Test project creation workflow"""
        # Simulate user input
        project_data = {
            'project_name': 'Test Project',
            'project_desc': 'Description'
        }

        # Create project
        project = PfProject.create(**project_data, created_at=datetime.now(), modified_at=datetime.now())

        # Verify
        assert project.project_name == 'Test Project'
        assert project.id is not None

    def test_create_datamatrix_workflow(self, test_project):
        """Test datamatrix creation workflow"""
        dm_data = {
            'project': test_project,
            'datamatrix_name': 'Test Matrix',
            'datamatrix_index': 1,
            'n_taxa': 3,
            'n_chars': 5
        }

        dm = PfDatamatrix.create(**dm_data)

        assert dm.datamatrix_name == 'Test Matrix'
        assert dm.project == test_project

    def test_delete_project_cascade(self, test_project, test_datamatrix):
        """Test deleting project cascades to datamatrices"""
        project_id = test_project.id
        dm_count = PfDatamatrix.select().where(PfDatamatrix.project == test_project).count()

        assert dm_count > 0

        # Delete project
        test_project.delete_instance(recursive=True)

        # Datamatrices should be deleted
        dm_count = PfDatamatrix.select().where(PfDatamatrix.project_id == project_id).count()
        assert dm_count == 0
```

**완료 기준**:
- [ ] 프로젝트 생성 플로우 테스트 2개
- [ ] 데이터매트릭스 생성 플로우 테스트 2개
- [ ] 분석 생성 플로우 테스트 2개
- [ ] 삭제 cascade 테스트 3개

---

### Phase 2 완료 기준 및 검증

**완료 기준**:
- [x] PfUtils.py 커버리지 61% → 80%+
- [x] PfDialog.py 커버리지 48% → 70%+
- [x] PhyloForester.py 커버리지 0% → 30%+
- [x] 전체 커버리지 40% → 60%+
- [x] 모든 테스트 통과

**검증 방법**:
```bash
# 커버리지 측정
pytest tests/ --cov=. --cov-report=html --cov-report=term

# 리포트 확인
open htmlcov/index.html
```

**예상 효과**:
- 리팩토링 안정성 확보
- 버그 사전 감지 능력 향상
- CI/CD 신뢰도 향상

---

## 📅 Phase 3: 에러 핸들링 및 안정성 개선 (Week 6-7)

### 목표
전역 예외 처리 강화 및 사용자 친화적 에러 메시지로 안정성 향상

### Sprint 3.1: 전역 예외 처리 (Week 6, Day 1-2)

#### Task 3.1.1: 전역 Exception Handler 추가
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: Critical

**작업 내용**:

**1. 전역 예외 핸들러 구현** (PhyloForester.py):
```python
import sys
import traceback
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSlot

class PhyloForesterMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set up global exception handler
        sys.excepthook = self.global_exception_handler

        # ...

    def global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler for uncaught exceptions.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        # Don't catch KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Log the error
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.critical(f"Uncaught exception:\n{error_msg}")

        # Show user-friendly message
        self.show_error_dialog(exc_type, exc_value, exc_traceback)

    def show_error_dialog(self, exc_type, exc_value, exc_traceback):
        """Show user-friendly error dialog.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        # User-friendly message
        user_msg = self.translate_exception_to_user_message(exc_type, exc_value)

        # Technical details (for bug reports)
        technical_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # Create dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Unexpected Error")
        msg.setText(user_msg)
        msg.setInformativeText("The application will continue running, but some features may not work correctly.")
        msg.setDetailedText(technical_details)
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

    def translate_exception_to_user_message(self, exc_type, exc_value):
        """Translate technical exception to user-friendly message.

        Args:
            exc_type: Exception type
            exc_value: Exception value

        Returns:
            User-friendly error message
        """
        # Map common exceptions to user messages
        error_messages = {
            FileNotFoundError: "A required file could not be found. Please check the file path and try again.",
            PermissionError: "Permission denied. Please check file permissions or run with administrator privileges.",
            ValueError: "Invalid input data. Please check your input and try again.",
            KeyError: "An internal data error occurred. This might be a bug.",
            OSError: "A system error occurred. Please check available disk space and permissions.",
        }

        # Get user message or default
        user_msg = error_messages.get(exc_type,
            f"An unexpected error occurred: {exc_type.__name__}")

        # Add exception details
        user_msg += f"\n\nDetails: {str(exc_value)}"

        return user_msg
```

**2. 로그 파일 저장**:
```python
# PfLogger.py 수정
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """Set up logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Optional log file path. If None, creates default in user directory
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Default log file location
    if log_file is None:
        log_dir = os.path.join(USER_PROFILE_DIRECTORY, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"PhyloForester_{datetime.now().strftime('%Y%m%d')}.log")

    # File handler (keeps last 7 days of logs)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=7
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file

    # Console handler (only INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

**완료 기준**:
- [ ] 전역 exception handler 구현
- [ ] 사용자 친화적 에러 다이얼로그
- [ ] 로그 파일 자동 저장
- [ ] 로그 로테이션 (7일 보관)

---

#### Task 3.1.2: 사용자 친화적 에러 메시지
**예상 시간**: 2시간
**담당**: Developer
**우선순위**: High

**작업 내용**:

**에러 메시지 매핑 테이블 확장**:
```python
# PhyloForester.py
class ErrorMessages:
    """User-friendly error messages"""

    # File errors
    FILE_NOT_FOUND = "The file '{filename}' could not be found. Please check the file path and try again."
    FILE_PERMISSION = "Cannot access file '{filename}'. Please check permissions."
    FILE_CORRUPT = "The file '{filename}' appears to be corrupted or in an invalid format."

    # Database errors
    DB_CONNECTION = "Cannot connect to the database. The application will try to recover."
    DB_CORRUPTION = "Database corruption detected. Please restore from backup or contact support."

    # Analysis errors
    ANALYSIS_SOFTWARE_NOT_FOUND = "{software} executable not found at '{path}'. Please configure in Preferences."
    ANALYSIS_FAILED = "Analysis failed: {reason}. Check the log for details."
    ANALYSIS_TIMEOUT = "Analysis timed out after {minutes} minutes. Consider reducing dataset size."

    # Data errors
    INVALID_DATAMATRIX = "Invalid datamatrix data. Please check taxa and character counts."
    INVALID_NEWICK = "Invalid tree format. Please check the Newick string syntax."

    # General
    UNEXPECTED_ERROR = "An unexpected error occurred. The application will continue, but some features may not work."
    OUT_OF_MEMORY = "Not enough memory to complete this operation. Try closing other applications."

def show_error(self, error_type, **kwargs):
    """Show user-friendly error message.

    Args:
        error_type: Error message template from ErrorMessages class
        **kwargs: Format parameters for the message
    """
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Error")
    msg.setText(error_type.format(**kwargs))
    msg.exec_()
```

**사용 예시**:
```python
# Before:
try:
    with open(filename, 'r') as f:
        data = f.read()
except Exception as e:
    print(f"Error: {e}")

# After:
try:
    with open(filename, 'r') as f:
        data = f.read()
except FileNotFoundError:
    self.show_error(ErrorMessages.FILE_NOT_FOUND, filename=filename)
    self.logger.error(f"File not found: {filename}")
except PermissionError:
    self.show_error(ErrorMessages.FILE_PERMISSION, filename=filename)
    self.logger.error(f"Permission denied: {filename}")
except Exception as e:
    self.show_error(ErrorMessages.UNEXPECTED_ERROR)
    self.logger.exception(f"Error reading file {filename}")
```

**완료 기준**:
- [ ] 에러 메시지 템플릿 20개 이상
- [ ] 주요 에러 발생 지점에 적용
- [ ] 한국어/영어 번역 추가

---

### Sprint 3.2: 입력 검증 강화 (Week 6, Day 3-5)

#### Task 3.2.1: 파일 경로 검증
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: High

**작업 내용**:

**경로 검증 유틸리티** (PfUtils.py):
```python
import os
from pathlib import Path
from typing import Tuple

def validate_file_path(file_path: str, must_exist: bool = True) -> Tuple[bool, str]:
    """Validate file path for security and accessibility.

    Args:
        file_path: Path to validate
        must_exist: Whether file must already exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Convert to Path object
        path = Path(file_path)

        # Check for path traversal attempts
        if ".." in file_path:
            return False, "Invalid path: path traversal not allowed"

        # Check if path is absolute (safer)
        if not path.is_absolute():
            # Make absolute
            path = path.resolve()

        # Check existence if required
        if must_exist and not path.exists():
            return False, f"File does not exist: {file_path}"

        # Check if it's actually a file (not directory)
        if must_exist and not path.is_file():
            return False, f"Not a file: {file_path}"

        # Check read permissions
        if must_exist and not os.access(str(path), os.R_OK):
            return False, f"No read permission: {file_path}"

        return True, ""

    except Exception as e:
        return False, f"Invalid path: {str(e)}"

def validate_directory_path(dir_path: str, must_exist: bool = False, must_be_writable: bool = True) -> Tuple[bool, str]:
    """Validate directory path.

    Args:
        dir_path: Directory path to validate
        must_exist: Whether directory must already exist
        must_be_writable: Whether directory must be writable

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(dir_path)

        # Check for path traversal
        if ".." in dir_path:
            return False, "Invalid path: path traversal not allowed"

        # Make absolute
        if not path.is_absolute():
            path = path.resolve()

        # Check existence
        if must_exist and not path.exists():
            return False, f"Directory does not exist: {dir_path}"

        if must_exist and not path.is_dir():
            return False, f"Not a directory: {dir_path}"

        # Check write permissions
        if must_be_writable and path.exists():
            if not os.access(str(path), os.W_OK):
                return False, f"No write permission: {dir_path}"

        return True, ""

    except Exception as e:
        return False, f"Invalid path: {str(e)}"
```

**적용 예시**:
```python
# PhyloForester.py - File open dialog
def on_action_import_datamatrix(self):
    """Import datamatrix from file"""
    filename, _ = QFileDialog.getOpenFileName(
        self, "Import Datamatrix", "", "All Files (*.*)"
    )

    if not filename:
        return

    # Validate path
    is_valid, error_msg = pu.validate_file_path(filename, must_exist=True)
    if not is_valid:
        self.show_error(ErrorMessages.FILE_NOT_FOUND, filename=filename)
        self.logger.error(f"Invalid file path: {error_msg}")
        return

    try:
        # Import datamatrix
        self.import_datamatrix(filename)
    except Exception as e:
        self.logger.exception(f"Error importing datamatrix from {filename}")
        self.show_error(ErrorMessages.FILE_CORRUPT, filename=filename)
```

**완료 기준**:
- [ ] 파일 경로 검증 함수 구현
- [ ] 디렉토리 경로 검증 함수 구현
- [ ] 모든 파일 열기/저장에 적용
- [ ] 테스트 케이스 10개 이상

---

#### Task 3.2.2: 데이터매트릭스 입력 검증
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

**검증 함수** (PfUtils.py):
```python
from typing import List, Tuple

def validate_datamatrix(
    taxa_list: List[str],
    datamatrix: List[List[str]],
    n_taxa: int,
    n_chars: int
) -> Tuple[bool, str]:
    """Validate datamatrix data.

    Args:
        taxa_list: List of taxon names
        datamatrix: Matrix of character states
        n_taxa: Expected number of taxa
        n_chars: Expected number of characters

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check taxa count
    if len(taxa_list) != n_taxa:
        return False, f"Expected {n_taxa} taxa, got {len(taxa_list)}"

    # Check duplicate taxa names
    if len(set(taxa_list)) != len(taxa_list):
        duplicates = [name for name in set(taxa_list) if taxa_list.count(name) > 1]
        return False, f"Duplicate taxon names: {', '.join(duplicates)}"

    # Check matrix dimensions
    if len(datamatrix) != n_taxa:
        return False, f"Matrix has {len(datamatrix)} rows, expected {n_taxa}"

    for i, row in enumerate(datamatrix):
        if len(row) != n_chars:
            return False, f"Row {i} has {len(row)} characters, expected {n_chars}"

    # Check character states (should be 0-9, A-Z, or ?)
    valid_chars = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ?-')
    for i, row in enumerate(datamatrix):
        for j, cell in enumerate(row):
            # Handle polymorphism (list)
            if isinstance(cell, list):
                for state in cell:
                    if state not in valid_chars:
                        return False, f"Invalid character state '{state}' at row {i}, col {j}"
            elif cell not in valid_chars:
                return False, f"Invalid character state '{cell}' at row {i}, col {j}"

    return True, ""

def sanitize_taxon_name(name: str) -> str:
    """Sanitize taxon name for safe use.

    Args:
        name: Original taxon name

    Returns:
        Sanitized taxon name
    """
    # Remove dangerous characters
    safe_name = re.sub(r'[^\w\s-]', '_', name)

    # Limit length
    if len(safe_name) > 100:
        safe_name = safe_name[:100]

    # Remove leading/trailing whitespace
    safe_name = safe_name.strip()

    return safe_name
```

**적용**:
```python
# PfDialog.py - DatamatrixDialog
def validate(self):
    """Validate datamatrix input"""
    # Get data
    taxa_list = self.get_taxa_list()
    datamatrix = self.get_datamatrix()
    n_taxa = self.spnTaxa.value()
    n_chars = self.spnChars.value()

    # Sanitize taxon names
    taxa_list = [pu.sanitize_taxon_name(name) for name in taxa_list]

    # Validate
    is_valid, error_msg = pu.validate_datamatrix(taxa_list, datamatrix, n_taxa, n_chars)

    if not is_valid:
        QMessageBox.warning(self, "Invalid Data", error_msg)
        return False

    return True
```

**완료 기준**:
- [ ] 데이터매트릭스 검증 함수 구현
- [ ] Taxon 이름 sanitization
- [ ] Dialog에서 검증 적용
- [ ] 테스트 케이스 15개

---

### Sprint 3.3: 복구 메커니즘 (Week 7)

#### Task 3.3.1: 분석 실행 중단 시 복구
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

```python
# PhyloForester.py
def on_analysis_interrupted(self, analysis_id):
    """Handle interrupted analysis.

    Args:
        analysis_id: ID of interrupted analysis
    """
    try:
        analysis = PfAnalysis.get_by_id(analysis_id)

        # Mark as stopped
        analysis.analysis_status = ANALYSIS_STATUS_STOPPED
        analysis.save()

        # Clean up process
        if analysis_id in self.running_processes:
            process = self.running_processes[analysis_id]
            if process.state() != QProcess.NotRunning:
                process.kill()
                process.waitForFinished(5000)
            del self.running_processes[analysis_id]

        # Log
        self.logger.warning(f"Analysis {analysis_id} interrupted and marked as stopped")

        # Offer recovery options
        self.offer_analysis_recovery(analysis)

    except Exception as e:
        self.logger.exception(f"Error handling interrupted analysis {analysis_id}")

def offer_analysis_recovery(self, analysis):
    """Offer options to recover from interrupted analysis.

    Args:
        analysis: PfAnalysis instance
    """
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Analysis Interrupted")
    msg.setText(f"Analysis '{analysis.analysis_name}' was interrupted.")
    msg.setInformativeText("Would you like to restart it?")

    btnRestart = msg.addButton("Restart Analysis", QMessageBox.YesRole)
    btnDelete = msg.addButton("Delete Analysis", QMessageBox.DestructiveRole)
    btnKeep = msg.addButton("Keep as Stopped", QMessageBox.NoRole)

    msg.exec_()
    clicked = msg.clickedButton()

    if clicked == btnRestart:
        self.restart_analysis(analysis)
    elif clicked == btnDelete:
        analysis.delete_instance(recursive=True)
    # else: keep as stopped
```

**완료 기준**:
- [ ] 중단된 분석 감지
- [ ] 복구 옵션 제공
- [ ] 재시작 기능 구현

---

#### Task 3.3.2: 데이터베이스 손상 감지 및 복구
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

```python
# PhyloForester.py
import shutil
from datetime import datetime

def check_database_integrity(self):
    """Check database integrity on startup.

    Returns:
        True if database is OK, False if corrupted
    """
    try:
        # Try to query database
        project_count = PfProject.select().count()
        self.logger.info(f"Database OK: {project_count} projects found")
        return True

    except Exception as e:
        self.logger.error(f"Database integrity check failed: {e}")
        return False

def backup_database(self):
    """Create database backup.

    Returns:
        Path to backup file
    """
    db_path = gDatabase.database
    backup_dir = os.path.join(USER_PROFILE_DIRECTORY, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"PhyloForester_{timestamp}.db")

    shutil.copy2(db_path, backup_path)
    self.logger.info(f"Database backed up to {backup_path}")

    # Keep only last 10 backups
    self.cleanup_old_backups(backup_dir, keep=10)

    return backup_path

def cleanup_old_backups(self, backup_dir, keep=10):
    """Remove old backup files.

    Args:
        backup_dir: Directory containing backups
        keep: Number of backups to keep
    """
    backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("PhyloForester_")],
        reverse=True
    )

    for old_backup in backups[keep:]:
        os.remove(os.path.join(backup_dir, old_backup))
        self.logger.debug(f"Removed old backup: {old_backup}")

def recover_from_backup(self):
    """Recover database from most recent backup.

    Returns:
        True if recovery successful
    """
    backup_dir = os.path.join(USER_PROFILE_DIRECTORY, "backups")

    if not os.path.exists(backup_dir):
        return False

    backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("PhyloForester_")],
        reverse=True
    )

    if not backups:
        return False

    latest_backup = os.path.join(backup_dir, backups[0])
    db_path = gDatabase.database

    try:
        # Close database
        gDatabase.close()

        # Restore from backup
        shutil.copy2(latest_backup, db_path)

        # Reopen
        gDatabase.connect(reuse_if_open=True)

        self.logger.info(f"Database recovered from {latest_backup}")
        return True

    except Exception as e:
        self.logger.exception("Database recovery failed")
        return False

def check_db(self):
    """Check database on startup (modified)"""
    # Check integrity
    if not self.check_database_integrity():
        # Offer recovery
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Database Error")
        msg.setText("The database appears to be corrupted.")
        msg.setInformativeText("Would you like to restore from the most recent backup?")

        btnRestore = msg.addButton("Restore from Backup", QMessageBox.YesRole)
        btnExit = msg.addButton("Exit", QMessageBox.NoRole)

        msg.exec_()

        if msg.clickedButton() == btnRestore:
            if self.recover_from_backup():
                QMessageBox.information(self, "Success", "Database restored successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to restore database. The application will exit.")
                sys.exit(1)
        else:
            sys.exit(1)

    # Create backup (weekly)
    last_backup = self.settings.value("LastBackup", "")
    today = datetime.now().strftime("%Y%m%d")

    if last_backup != today:
        self.backup_database()
        self.settings.setValue("LastBackup", today)
```

**완료 기준**:
- [ ] 데이터베이스 무결성 체크
- [ ] 자동 백업 (주 1회)
- [ ] 백업에서 복구 기능
- [ ] 오래된 백업 자동 정리

---

### Phase 3 완료 기준 및 검증

**완료 기준**:
- [x] 전역 exception handler 구현
- [x] 사용자 친화적 에러 메시지 20개+
- [x] 파일 경로 검증 적용
- [x] 데이터매트릭스 검증 적용
- [x] 분석 중단 복구 기능
- [x] 데이터베이스 백업/복구 기능

**검증 방법**:
```bash
# 1. 에러 시나리오 테스트
pytest tests/test_error_handling.py -v

# 2. 복구 기능 테스트
pytest tests/test_recovery.py -v

# 3. 수동 테스트
# - 존재하지 않는 파일 열기
# - 잘못된 형식 파일 가져오기
# - 분석 중 강제 종료
# - 데이터베이스 파일 손상
```

**예상 효과**:
- 크래시 없는 실행 99%+
- 사용자 친화적 에러 메시지
- 데이터 손실 방지

---

## 📅 Phase 4: 성능 최적화 (Week 8)

### 목표
프로파일링을 통해 병목 지점을 찾고 UI 반응성을 개선

### Sprint 4.1: 프로파일링 및 병목 분석 (Week 8, Day 1-3)

#### Task 4.1.1: cProfile로 성능 프로파일링
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

**1. 프로파일링 스크립트 작성** (profile_app.py):
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Performance profiling script for PhyloForester."""

import cProfile
import pstats
import io
from pstats import SortKey
import sys
from PyQt5.QtWidgets import QApplication

# Import main application
import PhyloForester

def profile_application_startup():
    """Profile application startup."""
    pr = cProfile.Profile()
    pr.enable()

    # Create application
    app = QApplication(sys.argv)
    window = PhyloForester.PhyloForesterMainWindow()

    pr.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(SortKey.CUMULATIVE)
    ps.print_stats(50)  # Top 50 functions

    print("=== Application Startup Profile ===")
    print(s.getvalue())

    # Save to file
    ps.dump_stats('profile_startup.prof')

def profile_datamatrix_load():
    """Profile loading large datamatrix."""
    # TODO: Implement
    pass

def profile_analysis_execution():
    """Profile analysis execution workflow."""
    # TODO: Implement
    pass

if __name__ == "__main__":
    profile_application_startup()
```

**2. 프로파일 결과 분석**:
```bash
# Run profiler
python profile_app.py

# Visualize with snakeviz
pip install snakeviz
snakeviz profile_startup.prof
```

**3. 병목 지점 문서화**:
- 가장 시간이 오래 걸리는 함수 10개
- 가장 많이 호출되는 함수 10개
- 최적화 가능한 지점 리스트업

**완료 기준**:
- [ ] 프로파일링 스크립트 작성
- [ ] 앱 시작, 데이터 로드, 분석 실행 프로파일링
- [ ] 병목 지점 문서화
- [ ] 최적화 우선순위 결정

---

#### Task 4.1.2: 메모리 프로파일링
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

```python
# memory_profile.py
from memory_profiler import profile
import PhyloForester

@profile
def test_large_datamatrix():
    """Test memory usage with large datamatrix."""
    # Create large datamatrix (100 taxa x 1000 characters)
    taxa_list = [f"Taxon_{i}" for i in range(100)]
    datamatrix = [["0", "1"] * 500 for _ in range(100)]

    # Simulate loading
    # ...

if __name__ == "__main__":
    test_large_datamatrix()
```

**실행**:
```bash
pip install memory_profiler
python -m memory_profiler memory_profile.py
```

**완료 기준**:
- [ ] 메모리 사용량 측정
- [ ] 메모리 누수 검사
- [ ] 대용량 데이터 처리 시 메모리 사용 최적화

---

#### Task 4.1.3: 데이터베이스 쿼리 최적화
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

**1. N+1 쿼리 문제 찾기**:
```python
# PfModel.py - Before (N+1 problem)
def get_all_projects_with_datamatrices():
    projects = PfProject.select()
    for project in projects:
        # This causes N queries (one per project)
        datamatrices = project.datamatrices
        print(f"{project.project_name}: {len(datamatrices)} datamatrices")

# After (optimized with prefetch)
def get_all_projects_with_datamatrices():
    projects = PfProject.select().prefetch(PfDatamatrix)
    for project in projects:
        # Now only 2 queries total (projects + datamatrices)
        datamatrices = project.datamatrices
        print(f"{project.project_name}: {len(datamatrices)} datamatrices")
```

**2. 인덱스 추가**:
```python
# PfModel.py - Add indexes for frequently queried fields
class PfProject(Model):
    project_name = CharField(max_length=255, unique=True, index=True)
    created_at = DateTimeField(default=datetime.now, index=True)

class PfDatamatrix(Model):
    datamatrix_index = IntegerField(index=True)

class PfAnalysis(Model):
    analysis_status = CharField(max_length=20, index=True)
```

**3. 쿼리 성능 측정**:
```python
import time

# Measure query time
start = time.time()
result = PfProject.select().prefetch(PfDatamatrix, PfAnalysis)
end = time.time()
print(f"Query took {(end - start) * 1000:.2f}ms")
```

**완료 기준**:
- [ ] N+1 쿼리 문제 해결
- [ ] 적절한 인덱스 추가
- [ ] 쿼리 시간 50% 단축

---

### Sprint 4.2: UI 반응성 개선 (Week 8, Day 4-5)

#### Task 4.2.1: 무거운 작업을 QThread로 이동
**예상 시간**: 1일
**담당**: Developer
**우선순위**: High

**작업 내용**:

**1. Worker Thread 클래스 생성**:
```python
# PhyloForester.py
from PyQt5.QtCore import QThread, pyqtSignal

class DataImportWorker(QThread):
    """Worker thread for importing datamatrix files."""

    # Signals
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(object)  # Result data
    error = pyqtSignal(str)  # Error message

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        """Import datamatrix in background thread."""
        try:
            # Parse file (CPU-intensive)
            parser = pu.PhyloDatafile(self.filename)

            # Emit progress
            self.progress.emit(25)

            # Detect format
            format_type = parser.detect_format()
            self.progress.emit(50)

            # Parse data
            if format_type == "nexus":
                taxa, matrix = parser.parse_nexus()
            elif format_type == "phylip":
                taxa, matrix = parser.parse_phylip()
            else:
                taxa, matrix = parser.parse_tnt()

            self.progress.emit(100)

            # Emit result
            self.finished.emit({
                'taxa': taxa,
                'matrix': matrix,
                'format': format_type
            })

        except Exception as e:
            self.error.emit(str(e))

class TreeRenderWorker(QThread):
    """Worker thread for rendering tree visualization."""

    finished = pyqtSignal(str)  # SVG path
    error = pyqtSignal(str)

    def __init__(self, newick, output_path, character_states=None):
        super().__init__()
        self.newick = newick
        self.output_path = output_path
        self.character_states = character_states

    def run(self):
        """Render tree in background thread."""
        try:
            # Heavy matplotlib rendering
            # ...
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))
```

**2. 메인 윈도우에서 사용**:
```python
# PhyloForester.py
def on_action_import_datamatrix(self):
    """Import datamatrix from file (with progress)."""
    filename, _ = QFileDialog.getOpenFileName(...)

    if not filename:
        return

    # Show progress dialog
    progress = QProgressDialog("Importing datamatrix...", "Cancel", 0, 100, self)
    progress.setWindowModality(Qt.WindowModal)

    # Create worker
    self.import_worker = DataImportWorker(filename)

    # Connect signals
    self.import_worker.progress.connect(progress.setValue)
    self.import_worker.finished.connect(self.on_import_finished)
    self.import_worker.error.connect(self.on_import_error)

    # Start background import
    self.import_worker.start()

def on_import_finished(self, data):
    """Handle import completion."""
    # Update UI (runs in main thread)
    self.create_datamatrix_from_data(data)
    QMessageBox.information(self, "Success", "Datamatrix imported successfully")

def on_import_error(self, error_msg):
    """Handle import error."""
    QMessageBox.warning(self, "Import Error", error_msg)
```

**완료 기준**:
- [ ] DataImportWorker 구현
- [ ] TreeRenderWorker 구현
- [ ] 진행 표시 다이얼로그
- [ ] UI가 freeze되지 않음

---

#### Task 4.2.2: 대용량 데이터매트릭스 로딩 최적화
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

**1. Lazy loading 구현**:
```python
# PfDialog.py - DatamatrixWidget
class DatamatrixWidget(QWidget):
    """Widget for displaying/editing datamatrix."""

    def __init__(self, datamatrix_id, parent=None):
        super().__init__(parent)
        self.datamatrix_id = datamatrix_id
        self.loaded = False

        # Don't load data until widget is shown
        # ...

    def showEvent(self, event):
        """Load data when widget is first shown."""
        if not self.loaded:
            self.load_data()
            self.loaded = True
        super().showEvent(event)

    def load_data(self):
        """Load datamatrix data from database."""
        # Only load when needed
        dm = PfDatamatrix.get_by_id(self.datamatrix_id)
        # ...
```

**2. 페이지네이션 (대용량 테이블)**:
```python
# PfDialog.py - DatamatrixTableModel
class DatamatrixTableModel(QAbstractTableModel):
    """Table model with pagination for large datasets."""

    ROWS_PER_PAGE = 100

    def __init__(self, taxa_list, datamatrix):
        super().__init__()
        self.full_data = datamatrix
        self.current_page = 0
        self.total_pages = (len(datamatrix) + self.ROWS_PER_PAGE - 1) // self.ROWS_PER_PAGE

    def rowCount(self, parent=None):
        """Return number of rows in current page."""
        start = self.current_page * self.ROWS_PER_PAGE
        end = min(start + self.ROWS_PER_PAGE, len(self.full_data))
        return end - start

    def data(self, index, role=Qt.DisplayRole):
        """Get data for current page."""
        if not index.isValid():
            return None

        # Offset by current page
        actual_row = self.current_page * self.ROWS_PER_PAGE + index.row()
        # ...

    def next_page(self):
        """Load next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.layoutChanged.emit()

    def prev_page(self):
        """Load previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.layoutChanged.emit()
```

**완료 기준**:
- [ ] Lazy loading 구현
- [ ] 대용량 테이블 페이지네이션
- [ ] 1000 taxa 이상 데이터매트릭스 테스트
- [ ] 로딩 시간 50% 단축

---

### Phase 4 완료 기준 및 검증

**완료 기준**:
- [x] 프로파일링 완료 및 병목 지점 파악
- [x] 무거운 작업 QThread로 이동
- [x] 데이터베이스 쿼리 최적화
- [x] 대용량 데이터 로딩 최적화

**검증 방법**:
```bash
# 성능 벤치마크
python benchmark.py

# 예상 결과:
# - 앱 시작 시간: 2s → 1s
# - 대용량 데이터 로드: 10s → 5s
# - UI 반응성: No freeze
```

**예상 효과**:
- 응답 시간 50% 단축
- UI freeze 없음
- 대용량 프로젝트 처리 가능

---

## 📅 Phase 5: 사용자 경험 개선 (Week 9-10)

### 목표
UI/UX 일관성 향상 및 사용자 친화적 기능 추가

### Sprint 5.1: UI/UX 일관성 (Week 9)

#### Task 5.1.1: 다이얼로그 크기/위치 저장 및 복원
**예상 시간**: 3시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

```python
# PfDialog.py - Base dialog class
class PfDialog(QDialog):
    """Base class for all dialogs with geometry persistence."""

    def __init__(self, parent=None, settings_key=None):
        super().__init__(parent)
        self.settings_key = settings_key or self.__class__.__name__
        self.settings = QSettings("PaleoBytes", "PhyloForester")

        # Restore geometry
        self.restore_geometry()

    def restore_geometry(self):
        """Restore dialog size and position from settings."""
        geometry = self.settings.value(f"DialogGeometry/{self.settings_key}")
        if geometry:
            self.restoreGeometry(geometry)

    def save_geometry(self):
        """Save dialog size and position to settings."""
        self.settings.setValue(
            f"DialogGeometry/{self.settings_key}",
            self.saveGeometry()
        )

    def closeEvent(self, event):
        """Save geometry on close."""
        self.save_geometry()
        super().closeEvent(event)

# Usage in existing dialogs
class ProjectDialog(PfDialog):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, settings_key="ProjectDialog")
        # ...
```

**완료 기준**:
- [ ] 모든 다이얼로그에 적용
- [ ] 크기/위치 복원 테스트
- [ ] 멀티 모니터 환경 테스트

---

#### Task 5.1.2: 키보드 단축키 일관성 및 문서화
**예상 시간**: 4시간
**담당**: Developer
**우선순위**: Medium

**작업 내용**:

**1. 단축키 표준화**:
```python
# PhyloForester.py - Standardized shortcuts
SHORTCUTS = {
    # File operations
    'new_project': 'Ctrl+N',
    'open_project': 'Ctrl+O',
    'save': 'Ctrl+S',
    'quit': 'Ctrl+Q',

    # Edit operations
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Shift+Z',
    'copy': 'Ctrl+C',
    'paste': 'Ctrl+V',
    'cut': 'Ctrl+X',

    # View operations
    'refresh': 'F5',
    'preferences': 'Ctrl+,',

    # Help
    'help': 'F1',
    'about': 'Ctrl+H',

    # Analysis
    'run_analysis': 'Ctrl+R',
    'stop_analysis': 'Ctrl+T',
}

def setup_shortcuts(self):
    """Set up all keyboard shortcuts."""
    # File menu
    self.action_new_project.setShortcut(SHORTCUTS['new_project'])
    self.action_open_project.setShortcut(SHORTCUTS['open_project'])
    # ...
```

**2. 단축키 문서**:
```rst
# docs/shortcuts.rst
Keyboard Shortcuts
==================

File Operations
---------------

* **Ctrl+N**: New Project
* **Ctrl+O**: Open Project
* **Ctrl+S**: Save
* **Ctrl+Q**: Quit

Edit Operations
---------------

* **Ctrl+Z**: Undo
* **Ctrl+Shift+Z**: Redo
* **Ctrl+C**: Copy
* **Ctrl+V**: Paste
* **Ctrl+X**: Cut

...
```

**완료 기준**:
- [ ] 단축키 표준화
- [ ] 충돌 제거
- [ ] 문서화
- [ ] 도움말에 추가

---

### Sprint 5.2: 도움말 시스템 (Week 9-10)

#### Task 5.2.1: 컨텍스트 도움말 (F1)
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Low

**작업 내용**:

```python
# PhyloForester.py
def keyPressEvent(self, event):
    """Handle F1 for context help."""
    if event.key() == Qt.Key_F1:
        self.show_context_help()
        event.accept()
    else:
        super().keyPressEvent(event)

def show_context_help(self):
    """Show context-sensitive help."""
    # Get current widget
    current = self.focusWidget()

    # Map widget types to help topics
    help_topics = {
        'ProjectDialog': 'user_guide.html#creating-projects',
        'DatamatrixDialog': 'user_guide.html#datamatrix-management',
        'AnalysisDialog': 'analysis_guide.html#running-analyses',
        'PreferencesDialog': 'user_guide.html#preferences',
    }

    # Find appropriate help topic
    topic = 'index.html'  # Default
    for widget_type, help_url in help_topics.items():
        if widget_type in str(type(current)):
            topic = help_url
            break

    # Open help in browser
    help_url = f"https://phyloforester.readthedocs.io/en/latest/{topic}"
    QDesktopServices.openUrl(QUrl(help_url))
```

**완료 기준**:
- [ ] F1 키 핸들러 구현
- [ ] 컨텍스트별 도움말 매핑
- [ ] 온라인/오프라인 도움말 지원

---

#### Task 5.2.2: 첫 실행 시 튜토리얼
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Low

**작업 내용**:

```python
# PhyloForester.py
def check_first_run(self):
    """Check if this is first run and show tutorial."""
    first_run = self.settings.value("FirstRun", True, type=bool)

    if first_run:
        self.show_welcome_tutorial()
        self.settings.setValue("FirstRun", False)

def show_welcome_tutorial(self):
    """Show welcome tutorial for new users."""
    tutorial = QDialog(self)
    tutorial.setWindowTitle("Welcome to PhyloForester")
    tutorial.setMinimumSize(600, 400)

    layout = QVBoxLayout(tutorial)

    # Welcome message
    welcome = QLabel(
        "<h2>Welcome to PhyloForester!</h2>"
        "<p>Let's get you started with a quick tutorial.</p>"
    )
    layout.addWidget(welcome)

    # Steps
    steps = QTextEdit()
    steps.setReadOnly(True)
    steps.setHtml("""
        <h3>Quick Start Guide</h3>
        <ol>
            <li><b>Create a Project:</b> File → New Project</li>
            <li><b>Import Data:</b> Right-click project → Import Datamatrix</li>
            <li><b>Run Analysis:</b> Right-click datamatrix → Run Analysis</li>
            <li><b>View Results:</b> Double-click analysis to view trees</li>
        </ol>

        <h3>Need Help?</h3>
        <p>Press <b>F1</b> any time for context-sensitive help.</p>
        <p>Visit our documentation at
           <a href="https://phyloforester.readthedocs.io">
           https://phyloforester.readthedocs.io</a>
        </p>
    """)
    layout.addWidget(steps)

    # Buttons
    button_layout = QHBoxLayout()
    btn_skip = QPushButton("Skip Tutorial")
    btn_skip.clicked.connect(tutorial.reject)
    btn_start = QPushButton("Let's Get Started!")
    btn_start.clicked.connect(tutorial.accept)
    button_layout.addWidget(btn_skip)
    button_layout.addWidget(btn_start)
    layout.addLayout(button_layout)

    tutorial.exec_()
```

**완료 기준**:
- [ ] 첫 실행 감지
- [ ] 환영 튜토리얼 다이얼로그
- [ ] 단계별 가이드
- [ ] 스킵 옵션

---

### Sprint 5.3: 국제화 완성 (Week 10)

#### Task 5.3.1: 번역 완성도 확인
**예상 시간**: 1일
**담당**: Developer
**우선순위**: Low

**작업 내용**:

```bash
# 번역 누락 확인
pylupdate5 PhyloForester.py PfDialog.py PfModel.py PfUtils.py \
    -ts translations/PhyloForester_en.ts \
    -ts translations/PhyloForester_ko.ts

# Qt Linguist로 번역
linguist translations/PhyloForester_ko.ts

# 컴파일
lrelease translations/PhyloForester_ko.ts
```

**완료 기준**:
- [ ] 모든 UI 문자열 번역
- [ ] 에러 메시지 번역
- [ ] 도움말 번역
- [ ] 번역 완성도 95%+

---

## 📅 Phase 6: 보안 및 규정 준수 (Week 11)

### Sprint 6.1: 보안 스캐닝

#### Task 6.1.1: Bandit 통합
**예상 시간**: 2시간

**작업 내용**:

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install Bandit
      run: pip install bandit

    - name: Run Bandit
      run: bandit -r . -f json -o bandit-report.json
      continue-on-error: true

    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: bandit-report
        path: bandit-report.json
```

**완료 기준**:
- [ ] Bandit CI 통합
- [ ] 보안 이슈 해결
- [ ] 주간 자동 스캔

---

#### Task 6.1.2: Safety (의존성 취약점)
**예상 시간**: 1시간

```yaml
# .github/workflows/security.yml (추가)
    - name: Check dependencies
      run: |
        pip install safety
        safety check --json
```

---

## 📅 Phase 7: 개발자 경험 개선 (Week 12)

### Sprint 7.1: 개발 환경

#### Task 7.1.1: VS Code 설정
**예상 시간**: 2시간

```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

---

#### Task 7.1.2: Makefile/Task Runner
**예상 시간**: 2시간

```makefile
# Makefile
.PHONY: help install test lint format clean build

help:
	@echo "PhyloForester Development Commands"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run linter"
	@echo "  format     Format code"
	@echo "  clean      Clean build artifacts"
	@echo "  build      Build application"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v --cov=.

lint:
	ruff check .
	mypy PfLogger.py PfModel.py

format:
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

build:
	python build.py
```

---

## 🎯 로드맵 요약

| Phase | 기간 | 목표 | 주요 작업 |
|-------|------|------|----------|
| **1. 코드 품질 기반** | Week 1-2 | Type hints 70%+, Linting 100% | Ruff, mypy, docstring |
| **2. 테스트 확대** | Week 3-5 | Coverage 60%+ | 파서, 다이얼로그, 메인 로직 테스트 |
| **3. 안정성** | Week 6-7 | 크래시 0%, 복구 기능 | 예외 처리, 검증, 백업 |
| **4. 성능** | Week 8 | 응답시간 50% 단축 | 프로파일링, QThread, 최적화 |
| **5. UX** | Week 9-10 | 사용성 향상 | 도움말, 튜토리얼, 일관성 |
| **6. 보안** | Week 11 | 취약점 0개 | Bandit, Safety, 코드 서명 |
| **7. 개발자 경험** | Week 12 | 온보딩 간소화 | 개발 환경, 문서, 가이드 |

---

## 📊 성공 지표 (3개월 후)

### 품질 지표
- [x] 테스트 커버리지: 40% → 60%+
- [x] Type hint 커버리지: 0% → 80%+
- [x] Linting 통과율: ~70% → 100%
- [x] 보안 취약점: 미확인 → 0개

### 성능 지표
- [x] 앱 시작 시간: 50% 단축
- [x] 대용량 데이터 로드: 50% 단축
- [x] UI freeze: 0회

### 안정성 지표
- [x] 크래시 없는 실행: 99%+
- [x] 데이터 손실: 0건
- [x] 자동 백업: 주 1회

### 개발 효율
- [x] PR 처리 시간: < 2일
- [x] CI/CD 성공률: > 95%
- [x] 문서화율: > 90%

---

## 🚀 Quick Wins (1주 안에)

바로 시작하고 싶다면:

1. **Ruff 설정** (Day 1, 4시간)
   - pyproject.toml 생성
   - 자동 수정 적용
   - CI 강제 적용

2. **Type hints 기초** (Day 2, 4시간)
   - PfLogger.py 완료
   - PfModel.py 시작

3. **전역 exception handler** (Day 3, 3시간)
   - 전역 핸들러 구현
   - 사용자 친화적 메시지

4. **Pre-commit hooks** (Day 4, 1시간)
   - 설정 파일 생성
   - 로컬 테스트

5. **테스트 확대** (Day 5, 1일)
   - PfUtils 파서 테스트 추가
   - 커버리지 70% 달성

**총 소요**: **5일** (40시간)
**즉시 효과**: 코드 품질 향상, 버그 감소, 개발자 경험 개선

---

## 📝 다음 단계

1. **이 계획 검토 및 승인**
2. **우선순위 조정** (필요시)
3. **Phase 1 시작**: Ruff 설정부터
4. **주간 진행상황 리뷰**
5. **계획 업데이트** (새로운 요구사항 반영)

---

**문서 버전**: 1.0
**작성일**: 2025-11-04
**다음 리뷰**: 2025-11-11 (Phase 1 완료 후)
