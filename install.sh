#!/usr/bin/env bash
#
# AR-C2-3 installer — ROS 2 Jazzy on Ubuntu 24.04 (Noble).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash
#   ./install.sh
#   ./install.sh --skip-ros
#   ./install.sh --skip-venv
#   ./install.sh --skip-build
#   ./install.sh --help
#
# Options can be passed through the pipe with:
#   curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash -s -- --skip-ros

set -euo pipefail

REPO_URL="https://github.com/Quinten175/AR-C2-3.git"
REPO_NAME="AR-C2-3"

# ---------------------------------------------------------------------------
# Bootstrap for `curl ... | bash`: the script is read from stdin, so clone the
# repository and re-exec the on-disk copy (keeps $0 and relative paths sane).
# ---------------------------------------------------------------------------
bootstrap_piped() {
  local target="${AR_C2_3_DIR:-$PWD/$REPO_NAME}"

  if ! command -v git >/dev/null 2>&1; then
    echo "[install] git not found — installing it via apt" >&2
    sudo apt-get update -qq
    sudo apt-get install -y -qq git
  fi

  if [[ -d "$target/.git" ]]; then
    echo "[install] Reusing existing clone at $target" >&2
    git -C "$target" pull --ff-only --quiet || true
  elif [[ -d "$target" ]]; then
    echo "[install] $target exists but is not a git clone." >&2
    echo "[install] Remove it or set AR_C2_3_DIR to another path, then retry." >&2
    exit 1
  else
    echo "[install] Cloning $REPO_URL into $target" >&2
    git clone --depth 1 "$REPO_URL" "$target"
  fi

  # Detach stdin from the curl pipe so nothing consumes leftover script bytes.
  exec bash "$target/install.sh" "$@" </dev/null
}

# When piped into bash, the script comes from stdin and BASH_SOURCE[0] is
# unset or "bash"/"stdin" rather than a real file — bootstrap in that case.
_piped_src="${BASH_SOURCE[0]:-}"
if [[ -z "$_piped_src" || "$_piped_src" == "bash" || "$_piped_src" == "stdin" || ! -f "$_piped_src" ]]; then
  bootstrap_piped "$@"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$SCRIPT_DIR"
SRC_DIR="$WORKSPACE_ROOT/PI5/src"
VENV_DIR="$WORKSPACE_ROOT/.venv"
# Target: Ubuntu 24.04 (noble) with ROS 2 Jazzy.
# Override the distro with ROS_DISTRO=<distro> if you know what you are doing.
UBUNTU_CODENAME="$(. /etc/os-release && echo "${UBUNTU_CODENAME:-unknown}")"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"
ROS2_APT_SOURCE="http://packages.ros.org/ros2/ubuntu"
ROS2_KEYRING="/usr/share/keyrings/ros-archive-keyring.gpg"
# Open Robotics ROS signing key fingerprint — the downloaded key is verified
# against this before it is trusted for apt.
ROS2_KEY_FINGERPRINT="C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654"
# Primary: GitHub-hosted ros.key (already binary keyring format; this is the
# source the official ROS install docs use). Fallback: packages.ros.org
# (ASCII-armored) — its TLS cert has been seen to mismatch while the host is
# served from the ftp.osuosl.org mirror.
ROS2_KEY_URL_PRIMARY="https://raw.githubusercontent.com/ros/rosdistro/master/ros.key"
ROS2_KEY_URL_FALLBACK="https://packages.ros.org/ros2.gpg"

if [[ -t 1 ]]; then
  C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'; C_RED='\033[0;31m'; C_BLUE='\033[1;34m'; C_RESET='\033[0m'
else
  C_GREEN=''; C_YELLOW=''; C_RED=''; C_BLUE=''; C_RESET=''
fi
readonly C_GREEN C_YELLOW C_RED C_BLUE C_RESET

log()  { printf '%b\n' "${C_BLUE}[install]${C_RESET} $*"; }
ok()   { printf '%b\n' "${C_GREEN}[  OK  ]${C_RESET} $*"; }
warn() { printf '%b\n' "${C_YELLOW}[ WARN ]${C_RESET} $*"; }
die()  { printf '%b\n' "${C_RED}[ FAIL ]${C_RESET} $*" >&2; exit 1; }

# ROS 2 setup scripts reference intentionally-unset vars (e.g.
# AMENT_TRACE_SETUP_FILES), which aborts under `set -u`. Temporarily relax
# nounset while sourcing them, then restore it. errexit/pipefail stay on —
# they don't conflict with the ROS setup scripts.
safe_source() {
  local __file="$1"
  set +u
  # shellcheck disable=SC1090
  source "$__file"
  set -u
}

SKIP_ROS=false
SKIP_VENV=false
SKIP_BUILD=false

usage() {
  cat <<'EOF'
AR-C2-3 installer (Ubuntu 24.04, ROS 2 Jazzy)

Usage:
  ./install.sh [options]
  curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash -s -- [options]

Options:
  --skip-ros    Skip ROS 2 installation (it must already be present)
  --skip-venv   Skip Python venv creation and pip requirements
  --skip-build  Skip the colcon workspace build
  -h, --help    Show this help

Environment:
  ROS_DISTRO    ROS 2 distro to install (default: jazzy)
  AR_C2_3_DIR   Clone target when run via curl | bash (default: $PWD/AR-C2-3)
EOF
  exit 0
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skip-ros)   SKIP_ROS=true;   shift ;;
      --skip-venv)  SKIP_VENV=true;  shift ;;
      --skip-build) SKIP_BUILD=true; shift ;;
      -h|--help)    usage ;;
      *) die "Unknown option: $1 (see --help)" ;;
    esac
  done
}

check_prereqs() {
  if [[ $EUID -eq 0 ]]; then
    die "Do not run as root; the script uses sudo where needed."
  fi
  command -v sudo >/dev/null 2>&1 || die "sudo is required"
  command -v apt-get >/dev/null 2>&1 || die "apt-get not found — this script targets Ubuntu 24.04 (ROS 2 Jazzy)"

  if [[ "$UBUNTU_CODENAME" != "noble" ]]; then
    warn "This script targets Ubuntu 24.04 (noble); detected: $UBUNTU_CODENAME — continuing with ROS 2 $ROS_DISTRO"
  else
    ok "Ubuntu 24.04 (noble) detected — using ROS 2 $ROS_DISTRO"
  fi

  log "Updating apt package lists"
  sudo apt-get update -qq
  sudo apt-get install -y -qq curl ca-certificates gnupg lsb-release git build-essential python3 python3-venv python3-pip >/dev/null
  ok "Base tools present"
}

verify_ros_keyring() {
  local keyring="$1" fpr
  fpr="$(gpg --show-keys --with-colons "$keyring" 2>/dev/null | awk -F: '/^fpr:/ {print $10; exit}')"
  [[ "$fpr" == "$ROS2_KEY_FINGERPRINT" ]]
}

fetch_ros_keyring() {
  local tmp
  tmp="$(mktemp)"

  log "Fetching ROS 2 apt signing key"
  if curl -fsSL "$ROS2_KEY_URL_PRIMARY" -o "$tmp"; then
    # GitHub ros.key is already in binary keyring format.
    sudo install -m 0644 "$tmp" "$ROS2_KEYRING"
  elif curl -fsSL "$ROS2_KEY_URL_FALLBACK" -o "$tmp"; then
    # packages.ros.org serves an ASCII-armored key.
    sudo gpg --batch --yes --dearmor -o "$ROS2_KEYRING" "$tmp"
  else
    rm -f "$tmp"
    die "Could not download the ROS 2 signing key from github.com/ros/rosdistro or packages.ros.org"
  fi
  rm -f "$tmp"

  if ! verify_ros_keyring "$ROS2_KEYRING"; then
    die "ROS 2 signing key fingerprint mismatch — aborting"
  fi
  ok "ROS 2 signing key installed (fingerprint verified)"
}

install_ros2() {
  if [[ -f "/opt/ros/$ROS_DISTRO/setup.bash" ]]; then
    ok "ROS 2 $ROS_DISTRO already installed, skipping apt install"
  else
    log "Installing ROS 2 $ROS_DISTRO (this can take a while)"
    fetch_ros_keyring
    echo "deb [arch=$(dpkg --print-architecture) signed-by=$ROS2_KEYRING] $ROS2_APT_SOURCE $UBUNTU_CODENAME main" \
      | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq "ros-$ROS_DISTRO-ros-base" "ros-$ROS_DISTRO-slam-toolbox" "ros-$ROS_DISTRO-nav2-bringup"
    ok "ROS 2 $ROS_DISTRO installed"
  fi

  if ! command -v colcon >/dev/null 2>&1; then
    sudo apt-get install -y -qq python3-colcon-common-extensions
  fi
  if ! command -v rosdep >/dev/null 2>&1; then
    sudo apt-get install -y -qq python3-rosdep
  fi
  if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
    sudo rosdep init 2>/dev/null || true
  fi
  rosdep update --rosdistro="$ROS_DISTRO" >/dev/null 2>&1 || warn "rosdep update failed (continuing anyway)"
  ok "colcon and rosdep ready"
}

install_venv() {
  log "Creating Python venv at $VENV_DIR"
  if [[ -d "$VENV_DIR" ]]; then
    warn "venv already exists, reusing it (delete $VENV_DIR to recreate)"
  else
    python3 -m venv "$VENV_DIR"
    ok "venv created"
  fi

  # shellcheck disable=SC1091
  safe_source "$VENV_DIR/bin/activate"
  pip install --upgrade pip setuptools wheel

  log "Installing Python dependencies into venv"
  pip install -r "$WORKSPACE_ROOT/requirements.txt"

  # Make the ROS 2 Python packages (rclpy, ...) importable from the venv.
  local pyver ros_site
  pyver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  ros_site="/opt/ros/$ROS_DISTRO/lib/python$pyver/site-packages"
  if [[ -d "$ros_site" && -n "$(ls -A "$ros_site" 2>/dev/null)" ]]; then
    printf '%s\n' "$ros_site" > "$VENV_DIR/lib/python$pyver/site-packages/ros2.pth"
    ok "Linked ROS 2 Python packages into venv via .pth"
  else
    warn "Could not find ROS 2 site-packages dir; rclpy may not import in venv"
  fi

  ok "venv ready: source $VENV_DIR/bin/activate"
}

build_workspace() {
  safe_source "/opt/ros/$ROS_DISTRO/setup.bash"

  local build_dir="$WORKSPACE_ROOT/build"
  local install_dir="$WORKSPACE_ROOT/install"
  local log_dir="$WORKSPACE_ROOT/log"
  mkdir -p "$build_dir" "$install_dir" "$log_dir"
  # COLCON_IGNORE markers so colcon does not re-scan its own output dirs
  touch "$build_dir/COLCON_IGNORE" "$install_dir/COLCON_IGNORE" "$log_dir/COLCON_IGNORE"

  log "Building ROS 2 workspace with colcon"
  cd "$WORKSPACE_ROOT"
  colcon build --symlink-install \
    --base-paths "$SRC_DIR" \
    --cmake-args -DCMAKE_BUILD_TYPE=Release
  safe_source "$install_dir/setup.bash"
  ok "Workspace built and sourced"
}

main() {
  parse_args "$@"
  check_prereqs
  [[ $SKIP_ROS == true ]]   || install_ros2
  [[ $SKIP_VENV == true ]]  || install_venv
  [[ $SKIP_BUILD == true ]] || build_workspace

  ok "All done. To use the workspace, run:"
  printf '%b\n' "  ${C_BLUE}source /opt/ros/$ROS_DISTRO/setup.bash${C_RESET}"
  printf '%b\n' "  ${C_BLUE}source $VENV_DIR/bin/activate${C_RESET}"
  printf '%b\n' "  ${C_BLUE}source $WORKSPACE_ROOT/install/setup.bash${C_RESET}"
}

main "$@"