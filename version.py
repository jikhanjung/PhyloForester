"""
PhyloForester Version Information
Single Source of Truth for version management
"""

from __future__ import annotations

import semver

__version__: str = "0.1.0"

# semver 라이브러리를 사용해 안전하게 파싱
_ver: semver.VersionInfo = semver.VersionInfo.parse(__version__)
__version_info__: tuple[int, int, int] = (_ver.major, _ver.minor, _ver.patch)
