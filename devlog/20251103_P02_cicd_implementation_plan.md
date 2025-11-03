# 2025-11-03 P02: CI/CD Pipeline Implementation Plan

## 계획 개요

**기반 프로젝트**: Modan2 CI/CD 시스템
**목표**: PhyloForester를 위한 완전 자동화된 CI/CD 파이프라인 구축
**기간**: 2-3주
**우선순위**: Testing > Build Automation > Release Automation > Documentation

---

## 📋 현황 분석

### PhyloForester 현재 상태
- ✅ 버전 관리 시스템 구축 완료 (version.py, manage_version.py)
- ✅ 테스트 스위트 존재 (82 tests)
- ✅ PyInstaller 빌드 스크립트 존재 (build.sh, build.bat)
- ❌ GitHub Actions 워크플로우 없음
- ❌ 자동화된 테스트 실행 없음
- ❌ 자동화된 빌드 없음
- ❌ 릴리스 자동화 없음

### Modan2 CI/CD 시스템 (참고)
Modan2는 다음과 같은 완전한 CI/CD 파이프라인을 갖추고 있음:

1. **Test Workflow** (`test.yml`)
   - Python 3.11, 3.12 매트릭스 테스트
   - PyQt5 GUI 테스트 (xvfb 사용)
   - 코드 커버리지 측정 및 Codecov 업로드
   - Ruff 린터 통합

2. **Build Workflow** (`reusable_build.yml`)
   - Windows: Inno Setup 인스톨러 + Portable ZIP
   - macOS: DMG 이미지
   - Linux: AppImage
   - version.py에서 버전 자동 추출
   - Build number 자동 증가

3. **Release Workflow** (`release.yml`)
   - Git 태그 푸시 시 자동 트리거
   - 테스트 실행 → 빌드 → 릴리스 생성
   - SHA256 체크섬 생성
   - Pre-release 자동 감지 (alpha/beta/rc)

4. **Documentation Workflow** (`docs.yml`)
   - Sphinx 기반 다국어 문서 (영어/한국어)
   - GitHub Pages 자동 배포

---

## 🎯 목표 및 범위

### Phase 1: Testing Infrastructure (Week 1)
자동화된 테스트 실행 환경 구축

### Phase 2: Build Automation (Week 2)
크로스 플랫폼 빌드 자동화

### Phase 3: Release Automation (Week 3)
릴리스 프로세스 완전 자동화

### Phase 4: Documentation (Optional)
문서 자동 배포 (필요시)

---

## 📅 Phase 1: Testing Infrastructure (1주차)

### Sprint 1.1: Test Workflow 구축 (Day 1-2)

#### Task 1.1.1: 기본 Test Workflow 생성
**예상 시간**: 3시간
**파일**: `.github/workflows/test.yml`

**작업 내용**:
```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    if: "!contains(github.event.head_commit.message, '[skip ci]')"
    runs-on: ubuntu-latest
    timeout-minutes: 30

    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          xvfb \
          libxcb-xinerama0 \
          libxcb-icccm4 \
          libxcb-image0 \
          libxcb-keysyms1 \
          libxcb-randr0 \
          libxcb-render-util0 \
          libxcb-xfixes0 \
          libxcb-shape0 \
          libxcb-cursor0 \
          qt5-qmake \
          qtbase5-dev \
          libqt5gui5 \
          libqt5core5a \
          libqt5widgets5

    - name: Cache pip dependencies
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      env:
        QT_QPA_PLATFORM: offscreen
      run: |
        xvfb-run -a pytest tests/ \
          --cov=. \
          --cov-report=xml \
          --cov-report=term \
          -v

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
```

**검증 기준**:
- [ ] Push 시 자동 실행
- [ ] 3개 Python 버전에서 모두 테스트 통과
- [ ] PyQt5 GUI 테스트 정상 작동

#### Task 1.1.2: Lint 통합
**예상 시간**: 1시간
**파일**: `.github/workflows/test.yml` 수정

**작업 내용**:
- Ruff 린터 추가
- 코드 스타일 검사 (optional, continue-on-error)

**검증 기준**:
- [ ] 린터 경고 표시
- [ ] 빌드 실패하지 않음 (optional)

### Sprint 1.2: 테스트 개선 (Day 3-4)

#### Task 1.2.1: requirements-ci.txt 생성
**예상 시간**: 30분
**파일**: `requirements-ci.txt`

**작업 내용**:
```txt
# CI/CD specific dependencies
pytest>=7.0.0
pytest-qt>=4.2.0
pytest-cov>=4.0.0
pytest-timeout>=2.1.0
ruff>=0.1.0
```

#### Task 1.2.2: 테스트 분리 실행
**예상 시간**: 2시간

**작업 내용**:
- Unit tests, Model tests, Dialog tests 분리 실행
- 각 테스트 그룹별 커버리지 측정
- 타임아웃 설정

**검증 기준**:
- [ ] 테스트 그룹별 실행 가능
- [ ] 개별 커버리지 리포트 생성

---

## 📅 Phase 2: Build Automation (2주차)

### Sprint 2.1: Reusable Build Workflow (Day 1-3)

#### Task 2.1.1: build.py 스크립트 개선
**예상 시간**: 4시간
**파일**: `build.py`

**작업 내용**:
Modan2의 build.py를 PhyloForester에 맞게 수정:

```python
import os
import platform
import re
import subprocess
from pathlib import Path

# Import version from centralized version file
try:
    from version import __version__ as VERSION
except ImportError:
    def get_version_from_file():
        with open("version.py") as f:
            content = f.read()
            match = re.search(r'__version__ = "(.*?)"', content)
            if match:
                return match.group(1)
        raise RuntimeError("Unable to find version string")
    VERSION = get_version_from_file()

import PfUtils as pu

def run_pyinstaller(args):
    """Runs PyInstaller with the specified arguments."""
    pyinstaller_cmd = ["pyinstaller"] + args
    subprocess.run(pyinstaller_cmd, check=True)
    print("PyInstaller completed successfully")

def build_windows():
    """Build Windows executable and installer"""
    print(f"Building PhyloForester {VERSION} for Windows...")

    # PyInstaller arguments
    args = [
        "--onedir",
        "--noconsole",
        "--name=PhyloForester",
        "--add-data=icons/*.png;icons",
        "--add-data=data/*.*;data",
        "--add-data=translations/*.qm;translations",
        "--icon=icons/PhyloForester.png",
        "--noconfirm",
        "PhyloForester.py"
    ]

    run_pyinstaller(args)

    # Create Inno Setup installer if available
    if platform.system() == "Windows":
        create_inno_setup_installer()

def build_macos():
    """Build macOS application bundle and DMG"""
    print(f"Building PhyloForester {VERSION} for macOS...")
    # Similar to Modan2 macOS build

def build_linux():
    """Build Linux AppImage"""
    print(f"Building PhyloForester {VERSION} for Linux...")
    # Similar to Modan2 Linux build

if __name__ == "__main__":
    system = platform.system()
    if system == "Windows":
        build_windows()
    elif system == "Darwin":
        build_macos()
    elif system == "Linux":
        build_linux()
```

**검증 기준**:
- [ ] 로컬에서 각 플랫폼 빌드 성공
- [ ] version.py에서 버전 자동 추출
- [ ] 빌드 결과물 정상 실행

#### Task 2.1.2: Reusable Build Workflow 생성
**예상 시간**: 6시간
**파일**: `.github/workflows/reusable_build.yml`

**작업 내용**:
Modan2의 reusable_build.yml을 PhyloForester에 맞게 수정:

```yaml
name: Reusable Build Workflow
on:
  workflow_call:
    inputs:
      build_number:
        required: true
        type: string

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Get Version String
        id: get_version
        shell: bash
        run: echo "VERSION=$(python -c 'from version import __version__; print(__version__)')" >> $GITHUB_OUTPUT

      - name: Download and Install Inno Setup
        shell: pwsh
        run: |
          # Download and install Inno Setup
          # Similar to Modan2

      - name: Build Windows
        shell: pwsh
        run: |
          python build.py
        env:
          BUILD_NUMBER: ${{ inputs.build_number }}

      - name: Create ZIP
        shell: pwsh
        run: |
          $zipFileName = "PhyloForester-Windows-v${{ steps.get_version.outputs.VERSION }}-build${{ inputs.build_number }}.zip"
          Compress-Archive -Path dist/PhyloForester/* -DestinationPath $zipFileName

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: phyloforester-windows
          path: PhyloForester-Windows-*.zip

  build-macos:
    runs-on: macos-latest
    # Similar structure to Windows

  build-linux:
    runs-on: ubuntu-latest
    # Similar structure to Windows
```

**검증 기준**:
- [ ] Windows 빌드 성공
- [ ] macOS 빌드 성공
- [ ] Linux 빌드 성공
- [ ] 아티팩트 정상 업로드

### Sprint 2.2: Build Workflow 통합 (Day 4-5)

#### Task 2.2.1: Main Build Workflow 생성
**예상 시간**: 2시간
**파일**: `.github/workflows/build.yml`

**작업 내용**:
```yaml
name: Build

permissions:
  contents: write

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  call-build-workflow:
    if: "!contains(github.event.head_commit.message, '[skip ci]')"
    uses: ./.github/workflows/reusable_build.yml
    with:
      build_number: ${{ github.run_number }}
```

**검증 기준**:
- [ ] main 브랜치 푸시 시 자동 빌드
- [ ] 빌드 번호 자동 증가
- [ ] `[skip ci]` 메시지로 건너뛰기 가능

---

## 📅 Phase 3: Release Automation (3주차)

### Sprint 3.1: Release Workflow (Day 1-3)

#### Task 3.1.1: Release Workflow 생성
**예상 시간**: 4시간
**파일**: `.github/workflows/release.yml`

**작업 내용**:
```yaml
name: Release

permissions:
  contents: write

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  test:
    uses: ./.github/workflows/test.yml

  call-build-workflow:
    needs: test
    uses: ./.github/workflows/reusable_build.yml
    with:
      build_number: ${{ github.run_number }}

  create-release:
    needs: call-build-workflow
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: release-files/

      - name: Generate SHA256 checksums
        run: |
          cd release-files
          find . -type f \( -name "*.zip" -o -name "*.dmg" -o -name "*.AppImage" \) -exec sha256sum {} \; > ../SHA256SUMS.txt

      - name: Prepare release body
        id: release_body
        run: |
          # Extract from CHANGELOG.md
          # Similar to Modan2

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          name: PhyloForester ${{ github.ref_name }}
          body: ${{ steps.release_body.outputs.RELEASE_BODY }}
          prerelease: ${{ contains(github.ref_name, '-alpha') || contains(github.ref_name, '-beta') || contains(github.ref_name, '-rc') }}
          files: |
            release-files/phyloforester-windows/*.zip
            release-files/phyloforester-macos/*.dmg
            release-files/phyloforester-linux/*.AppImage
            SHA256SUMS.txt
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**검증 기준**:
- [ ] 태그 푸시 시 자동 릴리스
- [ ] 테스트 실패 시 빌드 중단
- [ ] Pre-release 자동 감지
- [ ] SHA256 체크섬 포함

#### Task 3.1.2: Manual Release Workflow
**예상 시간**: 2시간
**파일**: `.github/workflows/manual-release.yml`

**작업 내용**:
수동 릴리스 트리거 워크플로우 (테스트용)

**검증 기준**:
- [ ] GitHub UI에서 수동 실행 가능
- [ ] 버전 번호 입력 가능

### Sprint 3.2: 패키징 스크립트 (Day 4-5)

#### Task 3.2.1: Windows Inno Setup 스크립트
**예상 시간**: 3시간
**파일**: `packaging/windows/phyloforester.iss`

**작업 내용**:
Modan2의 Inno Setup 스크립트를 PhyloForester에 맞게 수정:

```iss
[Setup]
AppName=PhyloForester
AppVersion={#VERSION}
AppPublisher=PaleoBytes
AppPublisherURL=https://github.com/jikhanjung/PhyloForester
DefaultDirName={autopf}\PhyloForester
DefaultGroupName=PhyloForester
OutputBaseFilename=PhyloForester-Setup-v{#VERSION}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Files]
Source: "dist\PhyloForester\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PhyloForester"; Filename: "{app}\PhyloForester.exe"
Name: "{autodesktop}\PhyloForester"; Filename: "{app}\PhyloForester.exe"
```

#### Task 3.2.2: Linux AppImage 스크립트
**예상 시간**: 3시간
**파일**: `packaging/linux/create_appimage.sh`

**작업 내용**:
```bash
#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Create AppDir structure
mkdir -p build_linux/AppDir/usr/{bin,lib,share}

# Copy executable
cp -r dist/PhyloForester/* build_linux/AppDir/usr/bin/

# Create .desktop file
cat > build_linux/AppDir/phyloforester.desktop << EOF
[Desktop Entry]
Type=Application
Name=PhyloForester
Exec=PhyloForester
Icon=phyloforester
Categories=Science;Education;
EOF

# Copy icon
cp icons/PhyloForester.png build_linux/AppDir/phyloforester.png

# Create AppImage
appimagetool build_linux/AppDir build_linux/PhyloForester-Linux-$VERSION.AppImage
```

#### Task 3.2.3: macOS DMG 생성
**예상 시간**: 3시간

**작업 내용**:
- create-dmg 사용
- Info.plist 생성
- App bundle 구조 생성

---

## 📅 Phase 4: Documentation (Optional)

### Sprint 4.1: Documentation Workflow (선택적)

#### Task 4.1.1: Sphinx 문서 설정
**예상 시간**: 4시간 (필요 시)

**작업 내용**:
- docs/ 디렉토리 생성
- Sphinx 설정
- 사용자 매뉴얼 작성

#### Task 4.1.2: GitHub Pages 배포
**예상 시간**: 2시간
**파일**: `.github/workflows/docs.yml`

**작업 내용**:
Modan2의 docs.yml 참고하여 작성

**검증 기준**:
- [ ] docs/ 변경 시 자동 배포
- [ ] GitHub Pages에 접근 가능

---

## 📋 Sprint별 체크리스트

### Phase 1: Testing Infrastructure
- [ ] test.yml 워크플로우 생성
- [ ] PyQt5 GUI 테스트 환경 설정
- [ ] 코드 커버리지 측정
- [ ] Codecov 통합
- [ ] Ruff 린터 통합
- [ ] requirements-ci.txt 생성
- [ ] 테스트 분리 실행

### Phase 2: Build Automation
- [ ] build.py 스크립트 작성
- [ ] reusable_build.yml 작성
- [ ] Windows 빌드 설정
- [ ] macOS 빌드 설정
- [ ] Linux 빌드 설정
- [ ] build.yml 메인 워크플로우
- [ ] 빌드 아티팩트 업로드

### Phase 3: Release Automation
- [ ] release.yml 워크플로우
- [ ] manual-release.yml 워크플로우
- [ ] SHA256 체크섬 생성
- [ ] CHANGELOG.md 파싱
- [ ] Pre-release 감지
- [ ] Inno Setup 스크립트
- [ ] AppImage 스크립트
- [ ] DMG 생성 스크립트

### Phase 4: Documentation (Optional)
- [ ] Sphinx 설정
- [ ] 문서 작성
- [ ] docs.yml 워크플로우
- [ ] GitHub Pages 배포

---

## 🔧 필요한 파일 및 디렉토리 구조

```
PhyloForester/
├── .github/
│   └── workflows/
│       ├── test.yml              # NEW
│       ├── build.yml             # NEW
│       ├── reusable_build.yml    # NEW
│       ├── release.yml           # NEW
│       ├── manual-release.yml    # NEW
│       └── docs.yml              # NEW (Optional)
├── packaging/
│   ├── windows/
│   │   └── phyloforester.iss     # NEW
│   ├── macos/
│   │   └── create_dmg.sh         # NEW
│   └── linux/
│       └── create_appimage.sh    # NEW
├── build.py                       # NEW (전체 개선)
├── requirements-ci.txt            # NEW
├── version.py                     # EXISTS
├── manage_version.py              # EXISTS
└── CHANGELOG.md                   # EXISTS
```

---

## 🎯 우선순위 및 의존성

### 필수 (High Priority)
1. **Test Workflow** - 코드 품질 보증의 기반
2. **Build Automation** - 릴리스 프로세스의 핵심
3. **Release Workflow** - 배포 자동화

### 권장 (Medium Priority)
4. **Packaging Scripts** - 사용자 경험 개선
5. **Manual Release** - 테스트 및 긴급 릴리스

### 선택 (Low Priority)
6. **Documentation** - 사용자 문서화 (나중에 추가 가능)

---

## 📊 예상 일정

| Week | Phase | Tasks | Estimated Hours |
|------|-------|-------|----------------|
| 1 | Testing | Test workflow, Lint | 15h |
| 2 | Build | build.py, Workflows | 25h |
| 3 | Release | Release workflow, Packaging | 20h |
| 4 (Optional) | Docs | Sphinx, Pages | 10h |

**총 예상 시간**: 60-70 hours (3-4주)

---

## 🚀 실행 전략

### Week 1: Foundation
1. Test workflow부터 시작 (가장 중요)
2. 로컬에서 테스트 실행 확인
3. GitHub Actions에서 실행 확인
4. 커버리지 측정 확인

### Week 2: Build
1. build.py 로컬 테스트
2. 각 플랫폼별 순차적 구현 (Windows → Linux → macOS)
3. 아티팩트 생성 확인

### Week 3: Release
1. Manual release workflow로 테스트
2. Tag 기반 자동 릴리스 테스트
3. Pre-release 테스트

---

## ⚠️ 주의사항 및 고려사항

### 1. 테스트 환경
- **PyQt5 GUI 테스트**: xvfb 필수 (Linux), offscreen 모드
- **타임아웃**: GUI 테스트는 시간이 오래 걸릴 수 있음
- **커버리지**: 최소 70% 목표

### 2. 빌드 환경
- **Windows**: Inno Setup 6.2.2+ 필요
- **macOS**: create-dmg brew 패키지 필요
- **Linux**: linuxdeploy, appimagetool 필요

### 3. 릴리스 프로세스
- **버전 태그**: `v0.1.0` 형식 엄수
- **CHANGELOG.md**: 릴리스 전 업데이트 필수
- **Pre-release**: alpha/beta/rc 자동 감지

### 4. 보안
- **GitHub Tokens**: 자동으로 제공되는 GITHUB_TOKEN 사용
- **Secrets**: 추가 secrets 필요 없음 (현재)
- **Permissions**: contents: write 필요

---

## 📈 성공 지표

### Phase 1 완료 기준
- [ ] Push 시 자동 테스트 실행
- [ ] 모든 테스트 통과
- [ ] 커버리지 리포트 생성
- [ ] Codecov에 데이터 업로드

### Phase 2 완료 기준
- [ ] 3개 플랫폼 모두 빌드 성공
- [ ] 빌드 아티팩트 다운로드 가능
- [ ] 빌드된 실행파일 정상 작동

### Phase 3 완료 기준
- [ ] 태그 푸시 시 자동 릴리스
- [ ] GitHub Release 페이지에 표시
- [ ] 다운로드 가능한 인스톨러/패키지
- [ ] SHA256 체크섬 포함

---

## 🔄 Modan2와의 차이점

### 유사점
- PyQt5 기반 데스크톱 애플리케이션
- version.py 기반 버전 관리
- pytest 테스트 프레임워크
- 3개 플랫폼 지원 (Windows, macOS, Linux)

### 차이점
| 항목 | Modan2 | PhyloForester |
|------|--------|---------------|
| Python 버전 | 3.11, 3.12 | 3.9, 3.10, 3.11 |
| 메인 파일 | Modan2.py | PhyloForester.py |
| 아이콘 위치 | icons/Modan2_2.png | icons/PhyloForester.png |
| 문서화 | Sphinx 다국어 | TBD (선택적) |
| 추가 의존성 | OpenGL | Biopython, matplotlib |

---

## 📚 참고 자료

### Modan2 CI/CD 파일
- `.github/workflows/test.yml` - 테스트 워크플로우
- `.github/workflows/reusable_build.yml` - 빌드 워크플로우
- `.github/workflows/release.yml` - 릴리스 워크플로우
- `build.py` - 빌드 스크립트

### GitHub Actions 문서
- [GitHub Actions 기본](https://docs.github.com/en/actions)
- [Workflow 문법](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Reusable workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)

### 패키징 도구
- [PyInstaller](https://pyinstaller.org/)
- [Inno Setup](https://jrsoftware.org/isinfo.php)
- [create-dmg](https://github.com/create-dmg/create-dmg)
- [AppImageKit](https://appimage.org/)

---

## 🎓 학습 포인트

이 계획을 통해 다음을 학습하고 구현할 수 있습니다:

1. **CI/CD 파이프라인**: 현대적인 소프트웨어 개발 프로세스
2. **크로스 플랫폼 빌드**: Windows, macOS, Linux 동시 지원
3. **자동화된 테스트**: 코드 품질 보증
4. **릴리스 관리**: Semantic Versioning과 자동화된 배포
5. **GitHub Actions**: Workflow 작성 및 디버깅

---

## 🔜 다음 단계

1. **Phase 1 시작**: test.yml 워크플로우 생성
2. **로컬 테스트**: 워크플로우 동작 확인
3. **피드백 수집**: 문제점 파악 및 개선
4. **문서화**: 각 단계별 devlog 작성

---

**작성일**: 2025-11-03
**작성자**: PhyloForester Development Team
**상태**: 📋 Planning
**다음 리뷰**: Phase 1 완료 후

