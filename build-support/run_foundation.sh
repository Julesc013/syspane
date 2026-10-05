#!/bin/sh
# Optional wrapper around the same documented CMake/CTest/package commands.
set -eu
cd "$(dirname "$0")/.."
export SYSPANE_LINUX_BUILD_ROOT="${SYSPANE_LINUX_BUILD_ROOT:-$HOME/.cache/syspane/campaign-229a498}"
case "${1:-all}" in
  configure) cmake --preset linux-x64-gcc13 ;;
  build) cmake --build --preset linux-x64-gcc13 ;;
  test) ctest --preset linux-x64-gcc13 --output-on-failure ;;
  package) python3 build-support/package_smoke.py --profile linux-x64-gcc13 --build-dir "$SYSPANE_LINUX_BUILD_ROOT/linux-x64-gcc13" ;;
  all)
    cmake --preset linux-x64-gcc13
    cmake --build --preset linux-x64-gcc13
    ctest --preset linux-x64-gcc13 --output-on-failure
    python3 build-support/package_smoke.py --profile linux-x64-gcc13 --build-dir "$SYSPANE_LINUX_BUILD_ROOT/linux-x64-gcc13"
    ;;
  *) echo 'expected configure, build, test, package or all' >&2; exit 2 ;;
esac
