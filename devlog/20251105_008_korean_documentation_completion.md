# 008 - 문서 한국어 번역 작업 완료 보고서

**작성일**: 2025-11-05
**관련 계획**: [P04 Korean Documentation Plan](20251105_P04_korean_documentation_plan.md)
**상태**: ✅ 완료

## 1. 작업 개요

PhyloForester 프로젝트 문서의 완전한 한국어 번역 및 다국어 지원 인프라 구축.

### 목표
- 모든 문서를 한국어로 번역
- Modan2 스타일의 언어 전환 기능 구현
- 자동 빌드 및 배포 시스템 구축

### 결과
- ✅ 7개 문서 완전 번역 (2,399 줄)
- ✅ 양방향 언어 전환 UI 구현
- ✅ GitHub Pages 자동 배포 성공

---

## 2. 완료된 작업 목록

### 2.1 번역 작업

#### 번역된 문서
| 문서명 | 원본 (영문) | 번역 (한국어) | 줄 수 |
|--------|------------|--------------|-------|
| Index | index.rst | index.po | 163 |
| Installation | installation.rst | installation.po | 217 |
| User Guide | user_guide.rst | user_guide.po | 399 |
| Analysis Guide | analysis_guide.rst | analysis_guide.po | 460 |
| Troubleshooting | troubleshooting.rst | troubleshooting.po | 421 |
| Developer Guide | developer_guide.rst | developer_guide.po | 601 |
| Changelog | changelog.rst | changelog.po | 138 |
| **합계** | - | - | **2,399** |

#### 번역 가이드라인
- **어조**: 정중한 해요체 사용
- **용어**: 기술 용어는 영문 병기
  - Example: "파서모니 분석 (Parsimony Analysis)"
- **UI 용어**: 일관성 유지
  - Project → 프로젝트
  - Datamatrix → 데이터매트릭스
  - Analysis → 분석

### 2.2 인프라 구축

#### 생성/수정된 파일
```
docs/
├── build_all_languages.py          # 다국어 빌드 스크립트 (신규)
├── index_redirect.html             # 언어 자동 감지 리디렉트 (신규)
├── _templates/
│   └── layout.html                 # 언어 전환 버튼 UI (수정)
├── locale/ko/LC_MESSAGES/          # 한국어 번역 파일 (신규)
│   ├── index.po
│   ├── installation.po
│   ├── user_guide.po
│   ├── analysis_guide.po
│   ├── troubleshooting.po
│   ├── developer_guide.po
│   └── changelog.po
├── Makefile                        # 한국어 빌드 타겟 추가 (수정)
└── requirements.txt                # sphinx-intl 2.1.0 추가 (수정)

.github/workflows/
└── docs.yml                        # 다국어 빌드 워크플로우 (수정)
```

---

## 3. 기술적 구현 세부사항

### 3.1 Sphinx i18n 시스템

#### POT 파일 생성
```bash
make gettext  # .pot 파일 생성
```

생성된 POT 파일:
- `docs/_build/gettext/*.pot` (7개 파일)

#### PO 파일 생성 및 관리
```bash
sphinx-intl update -p _build/gettext -l ko  # .po 파일 생성/업데이트
```

### 3.2 다국어 빌드 스크립트

**`build_all_languages.py`** 주요 기능:
```python
LANGUAGES = ["en", "ko"]

def build_language(lang: str) -> bool:
    """각 언어별로 독립적인 빌드 디렉토리 생성"""
    build_dir = DOCS_DIR / "_build" / "html" / lang

    if lang == "en":
        cmd = ["sphinx-build", "-b", "html", ".", str(build_dir)]
    else:
        cmd = ["sphinx-build", "-b", "html", "-D", f"language={lang}",
               ".", str(build_dir)]
```

**빌드 결과 구조**:
```
docs/_build/html/
├── index.html          # 자동 리디렉트 페이지
├── en/                 # 영문 문서
│   ├── index.html
│   ├── installation.html
│   └── ...
└── ko/                 # 한국어 문서
    ├── index.html
    ├── installation.html
    └── ...
```

### 3.3 언어 전환 UI

**위치**: 고정 위치 (Fixed position)
- 위치: 화면 우측 상단 (top: 10px, right: 10px)
- z-index: 1000 (최상위)

**구현** (`docs/_templates/layout.html`):
```html
<div class="language-switcher">
  <span class="icon">🌐</span>
  {% if language == 'ko' %}
    <a onclick="switchLanguage('en')">English</a>
    <span class="separator">|</span>
    <span class="current">한국어</span>
  {% else %}
    <span class="current">English</span>
    <span class="separator">|</span>
    <a onclick="switchLanguage('ko')">한국어</a>
  {% endif %}
</div>
```

**JavaScript 페이지 유지 기능**:
```javascript
function switchLanguage(targetLang) {
    var currentPath = window.location.pathname;
    var pageName = currentPath.split('/').pop() || 'index.html';

    // 언어 코드만 변경하고 페이지명 유지
    if (currentPath.includes('/en/')) {
        newPath = currentPath.replace('/en/', '/' + targetLang + '/');
    } else if (currentPath.includes('/ko/')) {
        newPath = currentPath.replace('/ko/', '/' + targetLang + '/');
    }

    window.location.href = newPath;
}
```

### 3.4 자동 언어 감지 및 리디렉트

**`index_redirect.html`** 기능:
1. 브라우저 언어 감지 (`navigator.language`)
2. 한국어 사용자 → `/ko/index.html`로 리디렉트
3. 기타 언어 → `/en/index.html`로 리디렉트
4. 수동 선택 옵션 제공

**구현 코드**:
```javascript
var userLang = navigator.language || navigator.userLanguage;
if (userLang.startsWith('ko')) {
    window.location.href = 'ko/index.html';
} else {
    window.location.href = 'en/index.html';
}
```

### 3.5 GitHub Actions 워크플로우

**수정 사항** (`.github/workflows/docs.yml`):

```yaml
- name: Build multi-language documentation
  run: |
    cd docs
    python build_all_languages.py

- name: Create index redirect page
  run: |
    cp docs/index_redirect.html docs/_build/html/index.html

- name: Create .nojekyll file
  run: |
    touch docs/_build/html/.nojekyll
```

**빌드 프로세스**:
1. 영문 문서 빌드 → `_build/html/en/`
2. 한국어 문서 빌드 → `_build/html/ko/`
3. 리디렉트 페이지 복사 → `_build/html/index.html`
4. `.nojekyll` 파일 생성 (GitHub Pages용)
5. GitHub Pages에 배포

---

## 4. 배포 및 검증

### 4.1 배포 확인
- ✅ 자동 언어 감지 작동
- ✅ 언어 전환 버튼 양쪽 페이지에서 표시
- ✅ 페이지 유지 기능 (user_guide.html → user_guide.html)
- ✅ 모든 문서 정상 렌더링
- ✅ 한국어 폰트 및 특수문자 정상 표시

### 4.2 테스트 케이스
1. **자동 리디렉트 테스트**
   - 한국어 브라우저 → `/ko/index.html` ✅
   - 영어 브라우저 → `/en/index.html` ✅

2. **언어 전환 테스트**
   - `/en/user_guide.html` → `/ko/user_guide.html` ✅
   - `/ko/analysis_guide.html` → `/en/analysis_guide.html` ✅

3. **모바일 반응형 테스트**
   - 언어 전환 버튼 위치 유지 ✅
   - 터치 이벤트 정상 작동 ✅

---

## 5. 번역 품질 관리

### 5.1 주요 용어 사전
| English | 한국어 | 비고 |
|---------|--------|------|
| Parsimony | 파서모니 | 절약법 대신 음차 사용 |
| Maximum Likelihood | 최대 우도법 | |
| Bayesian Inference | 베이지안 추론 | |
| Character Matrix | 형질 매트릭스 | |
| Datamatrix | 데이터매트릭스 | |
| Phylogenetic Tree | 계통수 | |
| Consensus Tree | 합의 계통수 | |
| Bootstrap | 부트스트랩 | 음차 사용 |
| MCMC | MCMC | 약어 그대로 사용 |
| TNT | TNT | 소프트웨어명 그대로 |

### 5.2 문체 예시

**Before (직역)**:
> "Click the New Project button to create a project."

**After (자연스러운 번역)**:
> "새 프로젝트를 만들려면 '새 프로젝트' 버튼을 클릭하세요."

---

## 6. 향후 유지보수 가이드

### 6.1 문서 업데이트 시 절차

1. **영문 문서 수정**
   ```bash
   # 1. .rst 파일 수정
   vim docs/installation.rst

   # 2. POT 파일 재생성
   cd docs
   make gettext

   # 3. PO 파일 업데이트
   sphinx-intl update -p _build/gettext -l ko
   ```

2. **한국어 번역 추가**
   ```bash
   # locale/ko/LC_MESSAGES/*.po 파일 편집
   vim locale/ko/LC_MESSAGES/installation.po
   ```

3. **빌드 및 확인**
   ```bash
   # 로컬 빌드
   python build_all_languages.py

   # 브라우저로 확인
   open _build/html/index.html
   ```

4. **배포**
   ```bash
   git add .
   git commit -m "docs: Update installation guide and Korean translation"
   git push origin main
   ```

### 6.2 새 언어 추가 시

1. **언어 코드 추가**
   ```python
   # build_all_languages.py
   LANGUAGES = ["en", "ko", "ja"]  # 일본어 추가 예시
   ```

2. **PO 파일 생성**
   ```bash
   sphinx-intl update -p _build/gettext -l ja
   ```

3. **번역 작업**
   ```bash
   # locale/ja/LC_MESSAGES/*.po 파일 편집
   ```

4. **언어 전환 UI 수정**
   ```html
   <!-- docs/_templates/layout.html -->
   <a onclick="switchLanguage('ja')">日本語</a>
   ```

---

## 7. 통계 및 성과

### 7.1 번역 통계
- **총 번역 줄 수**: 2,399 줄
- **총 문서 수**: 7개
- **작업 기간**: 1일
- **번역 속도**: ~2,400 줄/일

### 7.2 파일 통계
```
docs/locale/ko/LC_MESSAGES/
├── index.po              163 lines
├── installation.po       217 lines
├── user_guide.po         399 lines
├── analysis_guide.po     460 lines
├── troubleshooting.po    421 lines
├── developer_guide.po    601 lines
└── changelog.po          138 lines
```

### 7.3 코드 추가/수정 통계
- **신규 파일**: 9개 (번역 파일 7개 + 스크립트 2개)
- **수정 파일**: 4개 (layout.html, Makefile, requirements.txt, docs.yml)
- **총 추가 라인**: ~3,000 라인

---

## 8. 문제 해결 기록

### 8.1 언어 전환 버튼 미표시 문제

**문제**:
- 초기 구현에서 영문 페이지에 한국어 링크가 표시되지 않음
- Footer에만 표시되어 접근성 낮음

**해결**:
- Modan2 구조 참고하여 고정 위치 버튼으로 변경
- `{% block document %}` 사용하여 모든 페이지에 표시
- JavaScript로 페이지 경로 동적 변경 구현

### 8.2 Sphinx-intl 버전 문제

**문제**:
- sphinx-intl 2.0.0에서 일부 기능 제한

**해결**:
- requirements.txt에서 2.1.0으로 업데이트
- GitHub Actions에서도 동일 버전 사용

### 8.3 Pre-commit Hook 오류

**문제**:
- 첫 커밋 시 Ruff, 줄바꿈, 혼합 인코딩 오류

**해결**:
- Pre-commit hooks가 자동 수정
- 두 번째 커밋에서 모든 검사 통과

---

## 9. 참고 자료

### 9.1 관련 문서
- [P04 한국어 문서화 계획](20251105_P04_korean_documentation_plan.md)
- [Modan2 프로젝트](https://github.com/jikhanjung/Modan2) - 언어 전환 UI 참고

### 9.2 기술 문서
- [Sphinx Internationalization](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html)
- [sphinx-intl Documentation](https://sphinx-intl.readthedocs.io/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

---

## 10. 결론

### 10.1 달성한 목표
✅ 모든 문서의 완전한 한국어 번역 완료
✅ 사용자 친화적인 언어 전환 UI 구현
✅ 자동화된 빌드 및 배포 시스템 구축
✅ 향후 확장 가능한 다국어 인프라 확립

### 10.2 기대 효과
- **접근성 향상**: 한국어 사용자의 문서 접근성 대폭 개선
- **사용자 경험**: 자연스러운 언어 전환으로 UX 향상
- **확장성**: 추가 언어 지원 용이
- **유지보수성**: 자동화된 빌드로 관리 부담 감소

### 10.3 다음 단계
문서화 작업 완료 후 Phase 2 (Test Coverage Expansion)로 진행.

---

**작성자**: Claude Code
**검토일**: 2025-11-05
**문서 버전**: 1.0
