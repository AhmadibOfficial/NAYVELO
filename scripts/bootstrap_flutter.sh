#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v flutter >/dev/null || { echo 'Flutter SDK is not installed; install a stable Flutter SDK first.' >&2; exit 1; }
cd "$ROOT/apps/customer_app"
flutter create --platforms=android,ios --project-name=nayvelo_customer --org=com.nayvelo .
flutter pub get
flutter analyze
flutter test
printf '\nFlutter source and Android/iOS wrappers verified.\n'
