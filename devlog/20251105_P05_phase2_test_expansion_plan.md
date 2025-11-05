# 2025-11-05 P05: Phase 2 - Test Coverage Expansion Plan

## 계획 개요

**목표**: PhyloForester 테스트 커버리지를 36.65%에서 60%+로 확장
**기간**: 2-3일
**현재 버전**: v0.1.0
**우선순위**: High (코드 품질 기반 위에 테스트 강화)

---

## 📊 현재 상황

### 테스트 커버리지 현황 (2025-11-05)

| 모듈 | 라인 수 | 커버리지 | 목표 | 우선순위 |
|------|---------|----------|------|----------|
| **version.py** | 5 | 100.00% | 100% | ✅ 완료 |
| **PfLogger.py** | 28 | 96.43% | 98%+ | 🟢 우수 |
| **PfModel.py** | 325 | 82.46% | 90%+ | 🟡 개선 필요 |
| **PfUtils.py** | 570 | 61.40% | 80%+ | 🟠 확장 필요 |
| **PfDialog.py** | 2,157 | 48.63% | 60%+ | 🔴 Critical |
| **PhyloForester.py** | 1,551 | 0.00% | 10%+ | 🔴 미래 작업 |
| **총계** | **4,636** | **36.65%** | **60%+** | 🎯 목표 |

### 기존 테스트 현황

**총 82개 테스트**:
- `tests/test_utils.py`: 39개 (PfUtils 테스트)
- `tests/test_model.py`: 28개 (PfModel 테스트)
- `tests/test_dialogs.py`: 15개 (PfDialog 테스트)

**강점**:
- ✅ pytest-qt로 GUI 테스트 가능
- ✅ Fixtures 잘 구성됨 (conftest.py)
- ✅ pytest-cov로 커버리지 측정
- ✅ 모든 테스트 통과 (82 passed)

**약점**:
- ❌ PhyloForester.py 전혀 테스트 안 됨
- ❌ PfDialog.py 절반만 커버
- ❌ PfUtils.py 파일 파싱 함수 일부 미테스트
- ❌ 통합 테스트 부족

---

## 🎯 Phase 2 목표

### 주요 목표

1. **전체 커버리지 60%+ 달성**
   - 현재: 36.65% → 목표: 60%+
   - 약 23% 상승 필요

2. **핵심 모듈 강화**
   - PfUtils.py: 61% → 80%+
   - PfModel.py: 82% → 90%+
   - PfDialog.py: 48% → 60%+

3. **엣지 케이스 커버리지**
   - 에러 처리 경로
   - 예외 상황
   - 경계 조건

### 성공 지표

| 지표 | 현재 | 목표 | 측정 |
|------|------|------|------|
| 전체 커버리지 | 36.65% | 60%+ | pytest --cov |
| 테스트 개수 | 82 | 120+ | pytest --collect-only |
| 테스트 통과율 | 100% | 100% | pytest |
| 빌드 성공률 | 95% | 100% | GitHub Actions |

---

## 📅 작업 계획

### Sprint 2.1: PfUtils 테스트 확장 (Day 1, 4-6시간)

**목표**: PfUtils.py 커버리지 61% → 80%+

#### Task 2.1.1: 파일 파싱 테스트 확장

**대상 함수** (현재 미테스트):
```python
# 184-193: _parse_nexus_format() - 내부 함수
# 212-222: _parse_phylip_format() - 내부 함수
# 237-249: _parse_tnt_format() - 내부 함수
# 273: _detect_format() - 내부 함수
# 284-287: _validate_matrix() - 내부 함수
```

**테스트 추가**:
```python
# tests/test_utils.py에 추가

def test_phylodatafile_nexus_variations(tmp_path):
    """Test Nexus format variations."""
    # Interleaved format
    nexus_content = """
    #NEXUS
    BEGIN DATA;
        DIMENSIONS NTAX=3 NCHAR=5;
        FORMAT DATATYPE=STANDARD SYMBOLS="01" INTERLEAVE;
        MATRIX
        Taxon1  01
        Taxon2  10
        Taxon3  11

        Taxon1  010
        Taxon2  101
        Taxon3  110
    ;
    END;
    """
    # Test parsing...

def test_phylodatafile_phylip_sequential(tmp_path):
    """Test Phylip sequential format."""
    # Sequential format test

def test_phylodatafile_phylip_interleaved(tmp_path):
    """Test Phylip interleaved format."""
    # Interleaved format test

def test_phylodatafile_tnt_format(tmp_path):
    """Test TNT xread format."""
    tnt_content = """
    xread
    'Test dataset'
    5 3
    Taxon1  01010
    Taxon2  10101
    Taxon3  11001
    ;
    """
    # Test parsing...

def test_phylodatafile_invalid_format(tmp_path):
    """Test error handling for invalid format."""
    # Should raise DataParsingError

def test_phylodatafile_empty_file(tmp_path):
    """Test error handling for empty file."""
    # Should raise FileOperationError
```

**예상 추가**: 10-15개 테스트

---

#### Task 2.1.2: Fitch 알고리즘 테스트 확장

**대상 함수** (현재 부분 테스트):
```python
# 1093-1112: reconstruct_ancestral_states() - 일부만 테스트됨
# 1131-1149: bottom_up_pass() - 내부 함수
# 1170-1206: top_down_pass() - 내부 함수
```

**테스트 추가**:
```python
def test_fitch_missing_data():
    """Test Fitch algorithm with missing data (?)."""
    tree_newick = "((A,B),C);"
    states = {'A': '0', 'B': '1', 'C': '?'}
    result = reconstruct_ancestral_states(tree_newick, states)
    assert result is not None

def test_fitch_polymorphic_data():
    """Test Fitch algorithm with polymorphic states."""
    tree_newick = "((A,B),C);"
    states = {'A': '01', 'B': '1', 'C': '0'}  # A has polymorphism
    result = reconstruct_ancestral_states(tree_newick, states)
    assert result is not None

def test_fitch_complex_tree():
    """Test Fitch on complex tree with 10+ taxa."""
    # Large tree test

def test_fitch_invalid_tree():
    """Test error handling for invalid tree."""
    with pytest.raises(Exception):
        reconstruct_ancestral_states("invalid", {})
```

**예상 추가**: 5-8개 테스트

---

#### Task 2.1.3: 유틸리티 함수 테스트

**대상 함수** (현재 미테스트):
```python
# 103-106: safe_file_write() - 부분 테스트
# 131-134: safe_json_loads() - 미테스트
# 320-333: get_unique_name() - 미테스트
# 352-357: resource_path() - 미테스트
```

**테스트 추가**:
```python
def test_safe_json_loads_valid():
    """Test JSON parsing with valid data."""
    result = safe_json_loads('{"key": "value"}')
    assert result == {"key": "value"}

def test_safe_json_loads_invalid():
    """Test JSON parsing with invalid data."""
    with pytest.raises(DataParsingError):
        safe_json_loads('invalid json')

def test_get_unique_name_basic():
    """Test unique name generation."""
    existing = ["Project1", "Project2"]
    result = get_unique_name("Project", existing)
    assert result == "Project3"

def test_get_unique_name_gaps():
    """Test unique name with gaps in numbering."""
    existing = ["Project1", "Project3"]
    result = get_unique_name("Project", existing)
    assert result == "Project2"

def test_resource_path_bundled():
    """Test resource path in bundled mode."""
    # Mock sys._MEIPASS

def test_resource_path_development():
    """Test resource path in development mode."""
    # Normal path
```

**예상 추가**: 8-10개 테스트

**Sprint 2.1 예상 결과**:
- PfUtils.py: 61% → 80%+ (20% 증가)
- 추가 테스트: 23-33개
- 전체 커버리지: ~43-45%

---

### Sprint 2.2: PfModel 테스트 확장 (Day 1-2, 3-4시간)

**목표**: PfModel.py 커버리지 82% → 90%+

#### Task 2.2.1: 미커버 메서드 테스트

**대상 메서드** (현재 미테스트):
```python
# Line 97-98: setup_database_location() - 일부만 테스트
# Line 143-145: PfProject.get_analyses() - 미테스트
# Line 246-250: PfDatamatrix.get_taxa_list() - 부분 테스트
# Line 271: PfDatamatrix.get_character_list() - 부분 테스트
# Line 317-321: PfDatamatrix.datamatrix_as_list() - 부분 테스트
# Line 339-343: PfDatamatrix.set_datamatrix_from_list() - 미테스트
# Line 354-358: PfDatamatrix.get_nexus_matrix() - 미테스트
# Line 416: PfDatamatrix validation - 미테스트
```

**테스트 추가**:
```python
# tests/test_model.py에 추가

def test_project_get_analyses(sample_project, sample_analysis):
    """Test getting all analyses from a project."""
    analyses = sample_project.get_analyses()
    assert len(analyses) > 0
    assert sample_analysis in analyses

def test_datamatrix_get_taxa_list_empty(sample_datamatrix):
    """Test get_taxa_list with empty datamatrix."""
    sample_datamatrix.taxa_list_json = "[]"
    sample_datamatrix.save()
    taxa = sample_datamatrix.get_taxa_list()
    assert taxa == []

def test_datamatrix_set_from_list(sample_datamatrix):
    """Test setting datamatrix from list."""
    matrix = [
        ["0", "1", "0"],
        ["1", "0", "1"],
    ]
    sample_datamatrix.set_datamatrix_from_list(matrix)
    result = sample_datamatrix.datamatrix_as_list()
    assert result == matrix

def test_datamatrix_get_nexus_matrix(sample_datamatrix):
    """Test Nexus format export."""
    nexus = sample_datamatrix.get_nexus_matrix()
    assert "BEGIN DATA" in nexus
    assert "MATRIX" in nexus
    assert "END;" in nexus

def test_datamatrix_validation_invalid_characters():
    """Test validation with invalid character states."""
    # Should raise validation error

def test_analysis_status_transitions(sample_analysis):
    """Test valid status transitions."""
    # READY -> RUNNING -> FINISHED
    assert sample_analysis.status == ANALYSIS_STATUS_READY
    sample_analysis.status = ANALYSIS_STATUS_RUNNING
    sample_analysis.save()
    # Test transition
```

**예상 추가**: 10-15개 테스트

---

#### Task 2.2.2: 엣지 케이스 테스트

**대상**:
- 빈 프로젝트/데이터매트릭스 처리
- NULL 값 처리
- Foreign key cascade 동작
- 트랜잭션 롤백

**테스트 추가**:
```python
def test_project_delete_cascade(sample_project, sample_datamatrix):
    """Test that deleting project cascades to datamatrices."""
    project_id = sample_project.id
    datamatrix_id = sample_datamatrix.id

    sample_project.delete_instance()

    # Datamatrix should be deleted
    with pytest.raises(PfDatamatrix.DoesNotExist):
        PfDatamatrix.get_by_id(datamatrix_id)

def test_datamatrix_with_null_values(sample_project):
    """Test datamatrix with NULL optional fields."""
    dm = PfDatamatrix.create(
        dm_name="Test",
        project=sample_project,
        datamatrix_json=None,  # NULL
        taxa_list_json=None,   # NULL
    )
    assert dm.get_taxa_list() == []

def test_analysis_concurrent_update(sample_analysis):
    """Test concurrent analysis updates."""
    # Simulate race condition
```

**예상 추가**: 5-8개 테스트

**Sprint 2.2 예상 결과**:
- PfModel.py: 82% → 90%+ (8% 증가)
- 추가 테스트: 15-23개
- 전체 커버리지: ~47-50%

---

### Sprint 2.3: PfDialog 기본 테스트 추가 (Day 2-3, 4-5시간)

**목표**: PfDialog.py 커버리지 48% → 60%+

**현실적 접근**:
- GUI 테스트는 복잡하고 시간이 오래 걸림
- 기본적인 dialog 생성/초기화만 테스트
- 로직 부분 위주로 테스트 (UI 인터랙션 최소화)

#### Task 2.3.1: Dialog 초기화 테스트

**대상 클래스**:
```python
# ProjectDialog
# DatamatrixDialog
# AnalysisDialog
# PreferencesDialog
# ProgressDialog
```

**테스트 추가**:
```python
# tests/test_dialogs.py 확장

def test_project_dialog_init_create_mode(qtbot):
    """Test ProjectDialog initialization in create mode."""
    dialog = ProjectDialog(None, mode='create')
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "New Project"
    assert dialog.name_edit.text() == ""
    assert dialog.desc_edit.toPlainText() == ""

def test_project_dialog_init_edit_mode(qtbot, sample_project):
    """Test ProjectDialog initialization in edit mode."""
    dialog = ProjectDialog(None, mode='edit', project=sample_project)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Edit Project"
    assert dialog.name_edit.text() == sample_project.project_name

def test_datamatrix_dialog_init_create(qtbot, sample_project):
    """Test DatamatrixDialog initialization."""
    dialog = DatamatrixDialog(None, project=sample_project, mode='create')
    qtbot.addWidget(dialog)

    assert dialog.project == sample_project
    assert dialog.mode == 'create'

def test_analysis_dialog_parsimony_options(qtbot, sample_datamatrix):
    """Test AnalysisDialog with Parsimony analysis type."""
    dialog = AnalysisDialog(
        None,
        datamatrix=sample_datamatrix,
        analysis_type=ANALYSIS_TYPE_PARSIMONY
    )
    qtbot.addWidget(dialog)

    # Parsimony-specific options should be visible
    assert dialog.parsimony_widget.isVisible()
    assert not dialog.ml_widget.isVisible()

def test_preferences_dialog_init(qtbot):
    """Test PreferencesDialog initialization."""
    dialog = PreferencesDialog(None)
    qtbot.addWidget(dialog)

    # Should load current settings
    assert dialog is not None
```

**예상 추가**: 10-15개 테스트

---

#### Task 2.3.2: Dialog 로직 테스트

**대상**:
- 입력 검증 로직
- 데이터 변환 로직
- 상태 변경 로직

**테스트 추가**:
```python
def test_project_dialog_validation_empty_name(qtbot):
    """Test ProjectDialog validation with empty name."""
    dialog = ProjectDialog(None, mode='create')
    qtbot.addWidget(dialog)

    dialog.name_edit.setText("")

    # Accept should fail or show error
    # (구현에 따라)

def test_datamatrix_dialog_add_taxon(qtbot, sample_project):
    """Test adding a taxon to datamatrix."""
    dialog = DatamatrixDialog(None, project=sample_project, mode='create')
    qtbot.addWidget(dialog)

    initial_count = dialog.taxa_list.count()

    dialog.taxon_name_edit.setText("NewTaxon")
    dialog.on_add_taxon_clicked()

    assert dialog.taxa_list.count() == initial_count + 1

def test_datamatrix_dialog_remove_taxon(qtbot, sample_datamatrix):
    """Test removing a taxon from datamatrix."""
    dialog = DatamatrixDialog(
        None,
        datamatrix=sample_datamatrix,
        mode='edit'
    )
    qtbot.addWidget(dialog)

    initial_count = dialog.taxa_list.count()

    dialog.taxa_list.setCurrentRow(0)
    dialog.on_remove_taxon_clicked()

    assert dialog.taxa_list.count() == initial_count - 1

def test_analysis_dialog_change_type(qtbot, sample_datamatrix):
    """Test changing analysis type updates UI."""
    dialog = AnalysisDialog(
        None,
        datamatrix=sample_datamatrix,
        analysis_type=ANALYSIS_TYPE_PARSIMONY
    )
    qtbot.addWidget(dialog)

    # Change to ML
    dialog.type_combo.setCurrentText("Maximum Likelihood")

    # ML options should now be visible
    assert dialog.ml_widget.isVisible()
    assert not dialog.parsimony_widget.isVisible()
```

**예상 추가**: 8-12개 테스트

**Sprint 2.3 예상 결과**:
- PfDialog.py: 48% → 60%+ (12% 증가)
- 추가 테스트: 18-27개
- 전체 커버리지: ~55-60%

---

## 📊 예상 최종 결과

### 커버리지 목표

| 모듈 | 현재 | 목표 | 증가 |
|------|------|------|------|
| PfUtils.py | 61.40% | 80%+ | +19% |
| PfModel.py | 82.46% | 90%+ | +8% |
| PfDialog.py | 48.63% | 60%+ | +12% |
| **전체** | **36.65%** | **60%+** | **+23%** |

### 테스트 개수

- 현재: 82개
- 추가: 56-83개
- 목표: 138-165개

### 시간 배분

- Sprint 2.1 (PfUtils): 4-6시간
- Sprint 2.2 (PfModel): 3-4시간
- Sprint 2.3 (PfDialog): 4-5시간
- **총 예상**: 11-15시간 (2-3일)

---

## 🚀 실행 전략

### 우선순위

1. **High Priority** (반드시 달성):
   - PfUtils 파일 파싱 테스트
   - PfModel 미커버 메서드 테스트
   - PfDialog 기본 초기화 테스트

2. **Medium Priority** (시간 있으면):
   - Fitch 알고리즘 엣지 케이스
   - PfModel cascade 동작
   - PfDialog 복잡한 로직

3. **Low Priority** (Phase 3 이후):
   - PhyloForester.py 메인 윈도우 테스트
   - 완전한 통합 테스트
   - E2E 테스트

### 작업 순서

1. **PfUtils 먼저** (가장 영향 큰 모듈)
   - 파일 파싱 테스트 → 큰 커버리지 증가
   - 유틸리티 함수 → 빠르게 추가 가능

2. **PfModel 다음** (거의 완성)
   - 나머지 8% 채우기
   - 빠르게 90% 달성

3. **PfDialog 마지막** (가장 어려움)
   - 기본만 테스트
   - 60% 목표만 달성

### 측정 방법

각 Sprint 후 커버리지 측정:
```bash
pytest --cov=. --cov-report=term-missing --cov-report=html
```

목표 미달 시:
- 추가 테스트 케이스 식별
- 중요도 높은 것부터 보완

---

## ⚠️ 제약사항 및 리스크

### 제약사항

1. **GUI 테스트의 한계**
   - PyQt5 GUI는 완전 테스트 어려움
   - 기본 동작만 검증
   - 실제 사용자 인터랙션은 수동 테스트

2. **외부 의존성**
   - TNT, IQTree, MrBayes는 mock 필요
   - 실제 실행은 통합 테스트에서

3. **데이터베이스 테스트**
   - SQLite in-memory 사용
   - 실제 파일 DB와 차이 있을 수 있음

### 리스크

1. **시간 초과**
   - 완화: 우선순위 높은 것만 먼저
   - 60% 달성 못하면 55%로 조정

2. **테스트 불안정**
   - GUI 테스트는 타이밍 이슈 가능
   - qtbot.wait() 적절히 사용

3. **코드 변경 필요**
   - 테스트 불가능한 코드 발견 가능
   - 리팩토링 필요할 수도

---

## 📝 다음 단계

Phase 2 완료 후:
1. **Phase 3: 추가 코드 품질 개선**
   - 나머지 Ruff 에러 수정
   - Type hints 완성도 높이기
   - 복잡도 개선

2. **Phase 4: 성능 최적화**
   - 프로파일링
   - 병목 지점 개선
   - 대용량 데이터 처리

3. **Phase 5: 사용자 피드백 반영**
   - 버그 수정
   - 기능 개선
   - UX 향상

---

## 참고 자료

- [P03 Quality Improvement Plan](20251104_P03_quality_improvement_plan.md)
- [Phase 1 Completion Log](20251104_007_phase1_code_quality_foundation.md)
- [pytest documentation](https://docs.pytest.org/)
- [pytest-qt documentation](https://pytest-qt.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)

---

**작성자**: Claude Code
**검토자**: (To be assigned)
**상태**: Draft → Ready → In Progress → Completed
