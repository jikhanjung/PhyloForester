# 2025-11-05 P04: PhyloForester 문서 한국어 번역 계획

## 계획 개요

**목표**: PhyloForester 문서를 한국어로 번역하고 영어↔한국어 전환 가능한 다국어 문서 시스템 구축
**참고 프로젝트**: Modan2 (/mnt/d/projects/Modan2)
**방법**: Sphinx gettext 기반 i18n (Internationalization)
**기간**: 1주 (5 작업일)
**우선순위**: High (Phase 2 시작 전 완료)

---

## 📊 현황 분석

### PhyloForester 현재 문서 구조

```
docs/
├── conf.py                     # Sphinx 설정 (i18n 설정 이미 있음)
├── index.rst                   # 163 lines
├── installation.rst            # 217 lines
├── user_guide.rst              # 399 lines
├── analysis_guide.rst          # 460 lines
├── troubleshooting.rst         # 421 lines
├── developer_guide.rst         # 601 lines
├── changelog.rst               # 138 lines
├── docstring_style_guide.md    # 464 lines (개발자용, 번역 제외)
└── requirements.txt
```

**총 번역 대상**: 7개 파일, ~2,400 라인 (docstring_style_guide.md 제외)

### Modan2 참고 구조

```
docs/
├── conf.py                     # i18n 설정
├── locale/
│   └── ko/
│       └── LC_MESSAGES/
│           ├── index.po
│           ├── installation.po
│           ├── user_guide.po
│           ├── developer_guide.po
│           └── changelog.po
├── *.rst                       # 영어 원본
└── ...
```

**핵심 기술**:
- Sphinx `sphinx.ext.intersphinx` 확장
- `sphinx-intl` 도구로 .pot/.po 파일 생성 및 관리
- `locale_dirs`, `gettext_compact`, `language` 설정
- GitHub Pages에서 다국어 빌드

---

## 🎯 목표 및 성공 지표

### 완료 기준

| 항목 | 목표 | 측정 방법 |
|------|------|----------|
| **번역 완료율** | 100% | 7개 파일 모두 .po 파일 생성 및 번역 |
| **빌드 성공** | 영어/한국어 빌드 모두 성공 | `make html` 및 `make -e SPHINXOPTS="-D language='ko'" html` |
| **링크 동작** | 언어 전환 링크 동작 | 수동 테스트 |
| **GitHub Pages 배포** | 영어/한국어 페이지 모두 배포 | docs.github.io 확인 |
| **CI/CD 통합** | 문서 빌드 자동화 | GitHub Actions 워크플로우 |

### 성공 지표

✅ **사용자 경험**:
- 한국어 사용자가 모국어로 문서 읽기 가능
- 영어↔한국어 전환이 한 클릭으로 가능
- 모든 스크린샷과 예시가 맥락에 맞게 번역됨

✅ **유지보수성**:
- 영어 원본 수정 시 번역 업데이트 프로세스 명확
- `sphinx-intl` 도구로 번역 상태 추적 가능
- CI/CD에서 번역 누락 감지

✅ **프로젝트 품질**:
- 국제적인 사용자 기반 확대
- 한국 연구자들의 접근성 향상
- 프로젝트 성숙도 시각화

---

## 📅 작업 계획 (5일)

### Day 1: 인프라 설정 (4시간)

#### Task 1.1: sphinx-intl 설치 및 설정
**예상 시간**: 1시간
**우선순위**: Critical

**작업 내용**:
1. `sphinx-intl` 패키지 설치
2. `requirements.txt`에 추가
3. `docs/Makefile` 확인 및 수정 (필요 시)

**명령어**:
```bash
pip install sphinx-intl
echo "sphinx-intl>=2.1.0" >> docs/requirements.txt
```

**검증**:
```bash
sphinx-intl --version
```

**완료 기준**:
- [ ] sphinx-intl 설치 완료
- [ ] requirements.txt 업데이트
- [ ] 설치 테스트 통과

---

#### Task 1.2: POT 파일 생성
**예상 시간**: 30분
**우선순위**: Critical

**작업 내용**:
1. `conf.py`에서 i18n 설정 확인 (이미 있음)
2. gettext 빌드로 .pot 파일 생성
3. 생성된 파일 확인

**명령어**:
```bash
cd docs
make gettext
```

**예상 출력**:
```
Build finished. The message catalogs are in _build/gettext.
```

**생성 파일**:
```
docs/_build/gettext/
├── index.pot
├── installation.pot
├── user_guide.pot
├── analysis_guide.pot
├── troubleshooting.pot
├── developer_guide.pot
└── changelog.pot
```

**완료 기준**:
- [ ] .pot 파일 7개 생성
- [ ] 각 파일의 msgid 수 확인
- [ ] 특수 문자 인코딩 정상 확인

---

#### Task 1.3: PO 파일 생성
**예상 시간**: 30분
**우선순위**: Critical

**작업 내용**:
1. `sphinx-intl`로 한국어 .po 파일 생성
2. locale 디렉토리 구조 확인
3. Git에 추가

**명령어**:
```bash
cd docs
sphinx-intl update -p _build/gettext -l ko
```

**생성 구조**:
```
docs/locale/
└── ko/
    └── LC_MESSAGES/
        ├── index.po
        ├── installation.po
        ├── user_guide.po
        ├── analysis_guide.rst
        ├── troubleshooting.po
        ├── developer_guide.po
        └── changelog.po
```

**완료 기준**:
- [ ] locale/ko/LC_MESSAGES/ 디렉토리 생성
- [ ] .po 파일 7개 생성
- [ ] 파일 구조가 Modan2와 일치

---

#### Task 1.4: 빌드 스크립트 작성
**예상 시간**: 2시간
**우선순위**: High

**작업 내용**:
1. 다국어 빌드 스크립트 작성
2. 영어/한국어 빌드 테스트
3. 언어 전환 링크 추가

**파일**: `docs/build_all_languages.py`

```python
#!/usr/bin/env python3
"""Build Sphinx documentation for all languages."""

import subprocess
import sys
from pathlib import Path

LANGUAGES = ['en', 'ko']
DOCS_DIR = Path(__file__).parent

def build_language(lang: str) -> bool:
    """Build documentation for a specific language.

    Args:
        lang: Language code ('en' or 'ko')

    Returns:
        True if build succeeded, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Building documentation for: {lang}")
    print('='*60)

    build_dir = DOCS_DIR / '_build' / 'html' / lang

    if lang == 'en':
        # English (default)
        cmd = ['make', 'html']
    else:
        # Other languages
        cmd = [
            'sphinx-build',
            '-b', 'html',
            '-D', f'language={lang}',
            '.',
            str(build_dir)
        ]

    result = subprocess.run(
        cmd,
        cwd=DOCS_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"ERROR: Build failed for {lang}")
        print(result.stderr)
        return False

    print(f"SUCCESS: Documentation built at {build_dir}")
    return True

def main():
    """Build documentation for all languages."""
    success = True

    for lang in LANGUAGES:
        if not build_language(lang):
            success = False

    if success:
        print(f"\n{'='*60}")
        print("All language builds completed successfully!")
        print('='*60)
        return 0
    else:
        print("\nERROR: Some builds failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

**Makefile 추가 타겟**:
```makefile
# Build all languages
.PHONY: all-languages
all-languages:
	python build_all_languages.py

# Build Korean only
.PHONY: html-ko
html-ko:
	sphinx-build -b html -D language='ko' . _build/html/ko
```

**테스트**:
```bash
cd docs
python build_all_languages.py
```

**완료 기준**:
- [ ] build_all_languages.py 작성 완료
- [ ] 영어 빌드 성공
- [ ] 한국어 빌드 성공 (번역 전이라도 구조 확인)
- [ ] Makefile 타겟 추가

---

### Day 2: 핵심 사용자 문서 번역 (6시간)

#### Task 2.1: index.rst 번역
**예상 시간**: 2시간
**우선순위**: Critical
**라인 수**: 163 lines

**작업 내용**:
1. `locale/ko/LC_MESSAGES/index.po` 번역
2. 프로젝트 소개, 주요 기능, Quick Start
3. 기술 스택, 시스템 요구사항
4. 빌드 및 확인

**주요 섹션**:
- Welcome message
- Features (주요 기능)
- Quick Start (빠른 시작)
- Technology Stack (기술 스택)
- System Requirements (시스템 요구사항)

**번역 가이드라인**:
- 기술 용어는 한영 병기 (예: "Parsimony 분석")
- 소프트웨어 이름은 영어 유지 (TNT, IQTree, MrBayes)
- 키보드 단축키는 영어 유지 (Ctrl+C, Ctrl+V)

**검증**:
```bash
make html-ko
firefox _build/html/ko/index.html
```

**완료 기준**:
- [ ] index.po 100% 번역
- [ ] 한국어 빌드 성공
- [ ] 번역 품질 검토
- [ ] 링크 동작 확인

---

#### Task 2.2: installation.rst 번역
**예상 시간**: 2시간
**우선순위**: Critical
**라인 수**: 217 lines

**작업 내용**:
1. `locale/ko/LC_MESSAGES/installation.po` 번역
2. Windows, macOS, Linux 설치 가이드
3. 소스 빌드 방법
4. 외부 소프트웨어 설치 (TNT, IQTree, MrBayes)

**주요 섹션**:
- Installation methods (설치 방법)
- Platform-specific instructions (플랫폼별 설치)
- Building from source (소스에서 빌드)
- External dependencies (외부 의존성)
- Configuration (설정)

**완료 기준**:
- [ ] installation.po 100% 번역
- [ ] 플랫폼별 명령어 확인
- [ ] 경로 및 파일명 번역 일관성 확인

---

#### Task 2.3: user_guide.rst 번역
**예상 시간**: 2시간
**우선순위**: Critical
**라인 수**: 399 lines

**작업 내용**:
1. `locale/ko/LC_MESSAGES/user_guide.po` 번역
2. 프로젝트/Datamatrix 생성 및 관리
3. 분석 실행 및 결과 확인
4. UI 요소 설명

**주요 섹션**:
- Getting Started (시작하기)
- Project Management (프로젝트 관리)
- Datamatrix Editing (데이터 행렬 편집)
- Running Analyses (분석 실행)
- Viewing Results (결과 보기)
- Keyboard Shortcuts (키보드 단축키)

**UI 용어 통일**:
- Project → 프로젝트
- Datamatrix → 데이터 행렬
- Analysis → 분석
- Tree → 계통수
- Taxa → 분류군 (복수형 그대로)
- Character → 형질

**완료 기준**:
- [ ] user_guide.po 100% 번역
- [ ] UI 용어 일관성 확인
- [ ] 스크린샷 캡션 번역

---

### Day 3: 분석 및 문제해결 문서 번역 (6시간)

#### Task 3.1: analysis_guide.rst 번역
**예상 시간**: 3시간
**우선순위**: High
**라인 수**: 460 lines

**작업 내용**:
1. `locale/ko/LC_MESSAGES/analysis_guide.po` 번역
2. Parsimony, ML, Bayesian 분석 상세 설명
3. 파라미터 설명 및 예시
4. 결과 해석 가이드

**주요 섹션**:
- Parsimony Analysis (절약 분석)
- Maximum Likelihood Analysis (최대우도법 분석)
- Bayesian Inference (베이지안 추론)
- Analysis Parameters (분석 매개변수)
- Interpreting Results (결과 해석)
- Character Mapping (형질 매핑)

**전문 용어**:
- Parsimony → 절약법 (Parsimony)
- Maximum Likelihood → 최대우도법 (Maximum Likelihood)
- Bayesian Inference → 베이지안 추론 (Bayesian Inference)
- Bootstrap → 부트스트랩
- Consensus tree → 합의 계통수
- Synapomorphy → 공유 파생 형질

**완료 기준**:
- [ ] analysis_guide.po 100% 번역
- [ ] 전문 용어 한영 병기 확인
- [ ] 수식 및 알고리즘 설명 정확성 확인

---

#### Task 3.2: troubleshooting.rst 번역
**예상 시간**: 3시간
**우선순위**: High
**라인 수**: 421 lines

**작업 내용**:
1. `locale/ko/LC_MESSAGES/troubleshooting.po` 번역
2. 일반적인 문제 및 해결 방법
3. 에러 메시지 설명
4. FAQ

**주요 섹션**:
- Common Issues (일반적인 문제)
- Installation Problems (설치 문제)
- Analysis Failures (분석 실패)
- Performance Issues (성능 문제)
- Data Import Errors (데이터 가져오기 오류)
- Error Messages (오류 메시지)

**에러 메시지 번역 원칙**:
- 에러 코드는 영어 유지
- 설명은 한국어로
- 해결 방법은 단계별로 명확하게

**완료 기준**:
- [ ] troubleshooting.po 100% 번역
- [ ] 에러 메시지 정확성 확인
- [ ] 해결 방법 명확성 검토

---

### Day 4: 개발자 문서 및 변경사항 번역 (6시간)

#### Task 4.1: developer_guide.rst 번역
**예상 시간**: 4시간
**우선순위**: Medium
**라인 수**: 601 lines (가장 긴 문서)

**작업 내용**:
1. `locale/ko/LC_MESSAGES/developer_guide.po` 번역
2. 아키텍처 설명
3. 개발 환경 설정
4. 기여 가이드

**주요 섹션**:
- Architecture Overview (아키텍처 개요)
- Development Setup (개발 환경 설정)
- Code Structure (코드 구조)
- Database Schema (데이터베이스 스키마)
- Testing (테스트)
- Contributing Guidelines (기여 가이드)
- Release Process (릴리스 프로세스)

**코드 및 기술 용어**:
- 클래스/함수명은 영어 유지
- 주석은 한국어로
- 파일 경로는 영어 유지

**완료 기준**:
- [ ] developer_guide.po 100% 번역
- [ ] 코드 예시 주석 번역
- [ ] 기술 용어 일관성 확인

---

#### Task 4.2: changelog.rst 번역
**예상 시간**: 2시간
**우선순위**: Medium
**라인 수**: 138 lines

**작업 내용**:
1. `locale/ko/LC_MESSAGES/changelog.po` 번역
2. 버전별 변경사항
3. 기능 추가, 버그 수정 등

**주요 섹션**:
- Version history (버전 히스토리)
- Added features (추가된 기능)
- Changed features (변경된 기능)
- Fixed bugs (수정된 버그)

**Changelog 용어**:
- Added → 추가
- Changed → 변경
- Deprecated → 폐기 예정
- Removed → 제거
- Fixed → 수정
- Security → 보안

**완료 기준**:
- [ ] changelog.po 100% 번역
- [ ] 버전별 항목 모두 번역
- [ ] Keep a Changelog 형식 유지

---

### Day 5: 통합, 테스트, 배포 (6시간)

#### Task 5.1: 언어 전환 UI 구현
**예상 시간**: 2시간
**우선순위**: High

**작업 내용**:
1. HTML 템플릿에 언어 전환 링크 추가
2. CSS 스타일 적용
3. 양방향 전환 테스트

**구현 방법 1: _templates/layout.html**

```html
{% extends "!layout.html" %}

{% block footer %}
  {{ super() }}
  <div class="language-switcher">
    <p>
      {% if language == 'ko' %}
        🌐 <a href="{{ pathto(pagename, 1, '../../en/html/') }}">English</a>
      {% else %}
        🌐 <a href="{{ pathto(pagename, 1, '../../ko/html/') }}">한국어</a>
      {% endif %}
    </p>
  </div>
{% endblock %}
```

**구현 방법 2: conf.py html_context**

```python
html_context = {
    'display_github': True,
    'github_user': 'jikhanjung',
    'github_repo': 'PhyloForester',
    'github_version': 'main',
    'conf_py_path': '/docs/',
    # Language switcher
    'languages': [
        ('English', 'en'),
        ('한국어', 'ko'),
    ],
}
```

**완료 기준**:
- [ ] 언어 전환 링크 표시
- [ ] 클릭 시 올바른 페이지로 이동
- [ ] 양방향 전환 동작 확인

---

#### Task 5.2: 전체 빌드 및 테스트
**예상 시간**: 2시간
**우선순위**: Critical

**작업 내용**:
1. 모든 언어 빌드
2. 링크 확인 (내부/외부)
3. 이미지 및 리소스 확인
4. 번역 품질 검토

**테스트 체크리스트**:
```bash
# 1. Clean build
cd docs
make clean
python build_all_languages.py

# 2. Check English
firefox _build/html/en/index.html

# 3. Check Korean
firefox _build/html/ko/index.html

# 4. Link checker
sphinx-build -b linkcheck . _build/linkcheck

# 5. Check all pages
for file in _build/html/ko/*.html; do
    echo "Checking $file"
    # Manual visual inspection
done
```

**검증 항목**:
- [ ] 모든 페이지 빌드 성공
- [ ] 한글 인코딩 정상 (UTF-8)
- [ ] 모든 내부 링크 동작
- [ ] 이미지 정상 로드
- [ ] 코드 블록 정상 표시
- [ ] 테이블 정상 렌더링
- [ ] 언어 전환 동작

**완료 기준**:
- [ ] 빌드 에러 0개
- [ ] 링크 에러 0개
- [ ] 번역 누락 0개

---

#### Task 5.3: GitHub Actions 워크플로우 수정
**예상 시간**: 2시간
**우선순위**: High

**작업 내용**:
1. `.github/workflows/docs.yml` 수정
2. 다국어 빌드 자동화
3. GitHub Pages 배포 구조 변경

**워크플로우 수정**:

```yaml
name: Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '.github/workflows/docs.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'docs/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r docs/requirements.txt
        pip install sphinx-intl

    - name: Build all languages
      run: |
        cd docs
        python build_all_languages.py

    - name: Create index redirect
      run: |
        # Redirect root to English by default
        cat > docs/_build/html/index.html << EOF
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta http-equiv="refresh" content="0; url=en/index.html">
          <title>PhyloForester Documentation</title>
        </head>
        <body>
          <p>Redirecting to <a href="en/index.html">documentation</a>...</p>
        </body>
        </html>
        EOF

    - name: Deploy to GitHub Pages
      if: github.event_name == 'push'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/_build/html
        cname: phyloforester.readthedocs.io  # If using custom domain
```

**배포 구조**:
```
docs/_build/html/
├── index.html          # Redirect to en/
├── en/
│   ├── index.html
│   ├── installation.html
│   └── ...
└── ko/
    ├── index.html
    ├── installation.html
    └── ...
```

**URL 구조**:
- 영어: `https://jikhanjung.github.io/PhyloForester/en/`
- 한국어: `https://jikhanjung.github.io/PhyloForester/ko/`

**완료 기준**:
- [ ] 워크플로우 파일 수정
- [ ] 로컬에서 빌드 테스트
- [ ] GitHub Actions 빌드 성공
- [ ] GitHub Pages 배포 확인
- [ ] 영어/한국어 URL 모두 접근 가능

---

## 📝 번역 가이드라인

### 용어 통일 원칙

#### 소프트웨어 및 기술
| 영어 | 한국어 | 비고 |
|------|--------|------|
| PhyloForester | PhyloForester | 제품명, 번역 안 함 |
| Parsimony | 절약법 (Parsimony) | 한영 병기 |
| Maximum Likelihood | 최대우도법 (Maximum Likelihood) | 한영 병기 |
| Bayesian Inference | 베이지안 추론 (Bayesian Inference) | 한영 병기 |
| TNT | TNT | 소프트웨어명 |
| IQTree | IQTree | 소프트웨어명 |
| MrBayes | MrBayes | 소프트웨어명 |

#### UI 요소
| 영어 | 한국어 | 비고 |
|------|--------|------|
| Project | 프로젝트 | |
| Datamatrix | 데이터 행렬 | |
| Analysis | 분석 | |
| Tree | 계통수 | |
| Taxa (plural) | 분류군 | 복수형 그대로 |
| Character | 형질 | |
| State | 상태 | |
| Dialog | 대화상자 | |
| Widget | 위젯 | |

#### 분석 용어
| 영어 | 한국어 | 비고 |
|------|--------|------|
| Bootstrap | 부트스트랩 | |
| Consensus tree | 합의 계통수 | |
| Synapomorphy | 공유 파생 형질 | |
| Outgroup | 외집단 | |
| Ingroup | 내집단 | |
| Branch | 가지 | |
| Node | 마디 | |
| Clade | 분지군 | |
| Ancestral state | 조상 상태 | |

#### 파일 형식
| 영어 | 한국어 | 비고 |
|------|--------|------|
| Nexus | Nexus | 형식명 |
| Phylip | Phylip | 형식명 |
| Newick | Newick | 형식명 |

### 번역 스타일

#### 1. 존댓말 사용
- 사용자 대상 문서는 존댓말 (해요체)
- 예: "프로젝트를 생성하세요", "분석을 실행할 수 있습니다"

#### 2. 기술 용어 한영 병기
- 처음 등장 시 한영 병기
- 이후 한국어만 사용
- 예: "절약법(Parsimony) 분석은..." → 이후 "절약법 분석"

#### 3. 키보드 단축키
- 영어 그대로 유지
- 예: Ctrl+C, Ctrl+V, Ctrl+Z

#### 4. 파일 경로
- 영어 유지
- 예: `~/PhyloForester/data/`, `C:\Users\...`

#### 5. 코드 및 명령어
- 영어 유지
- 주석만 한국어로
```python
# 프로젝트 생성
project = PfProject.create(name="test")
```

#### 6. 에러 메시지
- 에러 코드: 영어 유지
- 설명: 한국어
```
Error: FileNotFoundError
설명: 파일을 찾을 수 없습니다.
```

---

## 🔧 개발 워크플로우

### 일일 작업 순서

1. **POT 업데이트** (원본 변경 시)
```bash
cd docs
make gettext
sphinx-intl update -p _build/gettext -l ko
```

2. **번역 작업**
```bash
# .po 파일 편집
vim locale/ko/LC_MESSAGES/index.po
```

3. **빌드 및 확인**
```bash
make html-ko
firefox _build/html/ko/index.html
```

4. **번역 상태 확인**
```bash
sphinx-intl stat
```

**출력 예시**:
```
locale/ko/LC_MESSAGES/index.po: 45 translated, 2 fuzzy, 0 untranslated.
locale/ko/LC_MESSAGES/user_guide.po: 120 translated, 5 fuzzy, 3 untranslated.
```

5. **커밋**
```bash
git add docs/locale/
git commit -m "docs: Add Korean translation for index and user guide"
```

### PO 파일 편집

#### 추천 도구
1. **Poedit** (GUI, 추천)
   - 다운로드: https://poedit.net/
   - 자동 번역 제안 기능
   - 오타 검사

2. **Vi/Vim** (터미널)
   ```bash
   vim locale/ko/LC_MESSAGES/index.po
   ```

3. **VS Code** (에디터)
   - 확장: gettext (PO file editor)

#### PO 파일 구조
```po
#: ../../index.rst:4
msgid "Welcome to PhyloForester's documentation!"
msgstr "PhyloForester 문서에 오신 것을 환영합니다!"

#: ../../index.rst:20
msgid ""
"**Project Management**: Organize phylogenetic analyses in a hierarchical "
"structure"
msgstr ""
"**프로젝트 관리**: 계층적 구조로 계통발생 분석을 조직화합니다"
```

#### 번역 팁
- `msgid`: 번역하지 말 것 (원본)
- `msgstr`: 번역 내용 입력
- `#:`: 원본 파일 위치 (참고용)
- 여러 줄: 각 줄을 `""` 로 감싸고 이어서 작성

---

## 📦 산출물

### 생성 파일

```
docs/
├── build_all_languages.py      # 다국어 빌드 스크립트 (NEW)
├── locale/                      # 번역 파일 (NEW)
│   └── ko/
│       └── LC_MESSAGES/
│           ├── index.po
│           ├── installation.po
│           ├── user_guide.po
│           ├── analysis_guide.po
│           ├── troubleshooting.po
│           ├── developer_guide.po
│           └── changelog.po
├── _templates/                  # HTML 템플릿 (수정)
│   └── layout.html             # 언어 전환 링크
├── _build/
│   ├── gettext/                # POT 파일 (임시)
│   └── html/
│       ├── index.html          # 리디렉션
│       ├── en/                 # 영어 문서
│       └── ko/                 # 한국어 문서
├── conf.py                     # (이미 i18n 설정 있음)
└── requirements.txt            # sphinx-intl 추가
```

### 문서

1. **README_i18n.md** - i18n 사용 가이드
2. **TRANSLATION_GUIDE.md** - 번역 가이드 (이 문서 요약)
3. **devlog 업데이트** - 작업 내용 기록

---

## 🚀 배포 전략

### GitHub Pages 구조

**Before** (현재):
```
https://jikhanjung.github.io/PhyloForester/
└── index.html (영어 문서)
```

**After** (다국어):
```
https://jikhanjung.github.io/PhyloForester/
├── index.html (리디렉션 → en/)
├── en/
│   └── index.html (영어 문서)
└── ko/
    └── index.html (한국어 문서)
```

### 브라우저 언어 감지 (선택사항)

**index.html 고급 버전**:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>PhyloForester Documentation</title>
  <script>
    // Detect browser language
    var userLang = navigator.language || navigator.userLanguage;
    var lang = userLang.startsWith('ko') ? 'ko' : 'en';
    window.location.href = lang + '/index.html';
  </script>
</head>
<body>
  <p>Redirecting to documentation...</p>
  <p><a href="en/index.html">English</a> | <a href="ko/index.html">한국어</a></p>
</body>
</html>
```

---

## ⚠️ 주의사항 및 리스크

### 1. 번역 품질
**리스크**: 전문 용어 오역 가능성
**완화**:
- 생물정보학/계통발생 전문가 검토 필요
- 한영 병기로 명확성 유지
- 커뮤니티 피드백 수집

### 2. 유지보수
**리스크**: 영어 원본 업데이트 시 번역 동기화 누락
**완화**:
- CI/CD에서 번역 상태 체크
- `sphinx-intl stat`로 정기 확인
- CHANGELOG에 문서 변경사항 기록

### 3. 빌드 시간 증가
**리스크**: 2배 빌드 시간 (영어 + 한국어)
**완화**:
- 변경된 언어만 빌드하는 옵션
- GitHub Actions 캐싱 활용

### 4. URL 구조 변경
**리스크**: 기존 북마크/링크 깨짐
**완화**:
- 리디렉션 페이지로 영어 기본 제공
- Google Search Console 업데이트

---

## 📊 진행 상황 추적

### 번역 진행률

| 파일 | 라인 수 | 예상 시간 | 상태 | 완료일 |
|------|---------|----------|------|--------|
| index.rst | 163 | 2시간 | ⬜ Pending | - |
| installation.rst | 217 | 2시간 | ⬜ Pending | - |
| user_guide.rst | 399 | 2시간 | ⬜ Pending | - |
| analysis_guide.rst | 460 | 3시간 | ⬜ Pending | - |
| troubleshooting.rst | 421 | 3시간 | ⬜ Pending | - |
| developer_guide.rst | 601 | 4시간 | ⬜ Pending | - |
| changelog.rst | 138 | 2시간 | ⬜ Pending | - |
| **Total** | **2,399** | **18시간** | **0%** | - |

상태:
- ⬜ Pending - 대기 중
- 🔵 In Progress - 진행 중
- ✅ Completed - 완료
- ⚠️ Review Needed - 검토 필요

### 인프라 작업

| 작업 | 예상 시간 | 상태 | 완료일 |
|------|----------|------|--------|
| sphinx-intl 설정 | 1시간 | ⬜ Pending | - |
| POT/PO 파일 생성 | 1시간 | ⬜ Pending | - |
| 빌드 스크립트 | 2시간 | ⬜ Pending | - |
| 언어 전환 UI | 2시간 | ⬜ Pending | - |
| GitHub Actions 수정 | 2시간 | ⬜ Pending | - |
| 테스트 및 검증 | 2시간 | ⬜ Pending | - |
| **Total** | **10시간** | **0%** | - |

---

## ✅ 완료 체크리스트

### 인프라 설정
- [ ] sphinx-intl 설치
- [ ] POT 파일 생성 (7개)
- [ ] PO 파일 생성 (7개)
- [ ] build_all_languages.py 작성
- [ ] Makefile 타겟 추가
- [ ] 언어 전환 UI 구현

### 번역 작업
- [ ] index.rst → index.po (100%)
- [ ] installation.rst → installation.po (100%)
- [ ] user_guide.rst → user_guide.po (100%)
- [ ] analysis_guide.rst → analysis_guide.po (100%)
- [ ] troubleshooting.rst → troubleshooting.po (100%)
- [ ] developer_guide.rst → developer_guide.po (100%)
- [ ] changelog.rst → changelog.po (100%)

### 품질 검증
- [ ] 모든 파일 빌드 성공
- [ ] 한글 인코딩 정상
- [ ] 모든 링크 동작
- [ ] 이미지 정상 로드
- [ ] 용어 일관성 확인
- [ ] 번역 품질 검토

### CI/CD
- [ ] GitHub Actions 워크플로우 수정
- [ ] 다국어 빌드 자동화
- [ ] GitHub Pages 배포 성공
- [ ] 영어/한국어 URL 접근 가능

### 문서화
- [ ] README_i18n.md 작성
- [ ] TRANSLATION_GUIDE.md 작성
- [ ] devlog 업데이트
- [ ] CHANGELOG 업데이트

---

## 🎯 성공 기준

### Phase 완료 조건

1. **번역 완료**: 7개 문서 100% 번역
2. **빌드 성공**: 영어/한국어 빌드 모두 성공
3. **배포 성공**: GitHub Pages에서 양 언어 접근 가능
4. **품질 검증**: 링크, 이미지, 인코딩 모두 정상
5. **CI/CD 통합**: 자동화된 빌드 및 배포

### 품질 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 번역 완료율 | 100% | sphinx-intl stat |
| 빌드 성공률 | 100% | GitHub Actions |
| 링크 에러 | 0개 | sphinx linkcheck |
| 인코딩 에러 | 0개 | 수동 확인 |
| 용어 일관성 | 100% | 수동 검토 |

---

## 📚 참고 자료

### Sphinx i18n
- [Sphinx Internationalization](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html)
- [sphinx-intl Documentation](https://sphinx-intl.readthedocs.io/)
- [gettext Tutorial](https://www.gnu.org/software/gettext/manual/gettext.html)

### 번역 도구
- [Poedit](https://poedit.net/) - PO 파일 에디터
- [Transifex](https://www.transifex.com/) - 온라인 번역 플랫폼 (선택사항)

### 참고 프로젝트
- Modan2: `/mnt/d/projects/Modan2/docs/`
- Read the Docs 다국어 예시

---

## 📅 타임라인

```
Week 1: 문서 한국어 번역
├── Day 1: 인프라 설정 (4h)
├── Day 2: 핵심 사용자 문서 (6h)
├── Day 3: 분석 및 문제해결 (6h)
├── Day 4: 개발자 문서 및 변경사항 (6h)
└── Day 5: 통합, 테스트, 배포 (6h)

Total: 28 시간 (실제 작업일 5일)

Week 2: Phase 2 시작
└── Test Coverage Expansion
```

---

## 🔄 다음 단계 (이 계획 완료 후)

1. **Phase 2: Test Coverage Expansion** 시작
2. **커뮤니티 피드백** 수집 (한국어 번역 품질)
3. **추가 언어 고려** (일본어, 중국어 등)
4. **번역 자동화** 도구 검토 (AI 번역 + 인간 검토)

---

## 📝 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-11-05 | 1.0 | 초안 작성 | Claude Code |

---

**작성자**: Claude Code
**검토자**: (To be assigned)
**승인자**: (To be assigned)
**상태**: Draft → Approved → In Progress → Completed
