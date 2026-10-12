#!/usr/bin/env bash

# Usage:
#   ./install.sh            
#   ./install.sh --skip-ros  
#   ./install.sh --skip-venv 
#   ./install.sh --skip-build 
#   ./install.sh --help

git clone https://github.com/Quinten175/AR-C2-3.git
cd AR-C2-3
set -euo pipefail


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$SCRIPT_DIR"
SRC_DIR="$WORKSPACE_ROOT/src/PI5/src"
VENV_DIR="$WORKSPACE_ROOT/.venv"
ROS_DISTRO="${ROS_DISTRO:-humble}"
ROS2_APT_SOURCE="http://packages.ros.org/ros2/ubuntu"
ROS2_KEYRING="/usr/share/keyrings/ros-archive-keyring.gpg"

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

SKIP_ROS=false
SKIP_VENV=false
SKIP_BUILD=false

usage() {
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
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
  [[ $EUID -eq 0 ]] && die "Do not run as root; the script uses sudo where needed."
  command -v sudo >/dev/null 2>&1 || die "sudo is required"
  command -v apt-get >/dev/null 2>&1 || die "apt-get not found — this script targets Ubuntu 22.04 (ROS 2 Humble)"

  log "Updating apt package lists"
  sudo apt-get update -qq
  sudo apt-get install -y -qq curl ca-certificates gnupg lsb-release git build-essential python3 python3-venv python3-pip >/dev/null
  ok "Base tools present"
}

install_ros2() {
  if [[ -f "/opt/ros/$ROS_DISTRO/setup.bash" ]]; then
    ok "ROS 2 $ROS_DISTRO already installed, skipping apt install"
  else
    log "Installing ROS 2 $ROS_DISTRO (this can take a while)"
    sudo install -d -m 0755 /etc/apt/keyrings
    curl -fsSL https://packages.ros.org/ros2.gpg | sudo gpg --dearmor -o "$ROS2_KEYRING"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=$ROS2_KEYRING] $ROS2_APT_SOURCE $(. /etc/os-release && echo "$UBUNTU_CODENAME") main" \
      | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq ros-"$ROS_DISTRO"-ros-base ros-"$ROS_DISTRO"-slam-toolbox ros-"$ROS_DISTRO"-nav2-bringup
    ok "ROS 2 $ROS_DISTRO installed"
  fi

  if ! command -v colcon >/dev/null 2 install_ros2() {
  if [[ -f "/opt/ros/$ROS_DISTRO/setup.bash" ]]; then
    ok "ROS 2 $ROS_DISTRO already installed, skipping apt install"
  else
    log "Installing ROS 2 $ROS_DISTRO (this can take a while)"
    sudo install -d -m 0755 /etc/apt/keyrings
    curl -fsSL https://packages.ros.org/ros2.gpg | sudo gpg --dearmor -o "$ROS2_KEYRING"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=$ROS2_KEYRING] $ROS2_APT_SOURCE $(. /etc/os-release && echo "$UBUNTU_CODENAME") main" \
      | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq ros-"$ROS_DISTRO"-ros-base ros-"$ROS_DISTRO"-slam-toolbox ros-"$ROS_DISTRO"-nav2-bringup
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
  rosdep update --rosdistro="$ROS_DISTRO" >/dev/null
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
  source "$VENV_DIR/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$SCRIPT_DIR"
SRC_DIR="$WORKSPACE_ROOT/src/PI5/src"
VENV_DIR="$WORKSPACE_ROOT/.venv"
ROS_DISTRO="${ROS_DISTRO:-humble}"
ROS_APT_SOURCE="/usr/share/ros/humble/setup.bash"
ROS_APT_SOURCE_FALLBACK="/opt/ros/humble/setup.bash"
ROS2_APT_SOURCE="http://packages.ros.org/ros2/ubuntu"
ROS2_KEYRING="/usr/share/keyrings/ros-archive-keyring.gpg"

if [[ -t 1 ]]; then
  C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'; C_RED='\033[0;31m'; C_BLUE='\033[1;34m'; C_RESET='\033[0m'
else
  CI=true
  C_GREEN=''; C_YELLOW=''; C_RED=''; C_BLUE=''; C_RESET=''

fi
readonly C_GREEN C_YELLOW C_RED C_BLUE C_RESET

log()  { printf '%b\n' "${C_BLUE}[install]${C_RESET} $*"; }
ok()   { printf '%b\n' "${C_GREEN}[  OK  ]${C_RESET} $*"; }
warn() { printf '%b\n' "${C_YELLOW}[ WARN ]${C apt-get update" && sudo apt-get install -y python3-rosdep python3-colcon-common-extensions
  fi
  ok "colcon and rosdep available"
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
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip setuptools wheel

  log "Installing Python dependencies into venv"
  pip install -r "$WORKSPACE_ROOT/requirements.txt"

  local ros_site
  ros_site="/opt/ros/$ROS_DISTRO/lib/python3.10/site-packages"
  if [[ -d "$ros_site" && -n "$(ls -A "$ros_site" 2>/dev/null)" ]]; ROS_DISTRO
    printf '%s\n' "$ros_site" > "$VENV_DIR/lib/python3.10/site-packages/ros2.pth"
    ok "Linked ROS 2 Python packages into venv via .pth"
  else
    warn "Could not find ROS  hardcoded site-packages dir; rclpy may not import in venv"
  hardcode "Could not find ROS 2 site-packages dir; rclpy may not import in venv"
  fi

  ok "venv ready: source $VENV_DIR .venv/bin/activate"
  ok "venv ready: source $VENV_DIR/bin/activate"
  ok "venv requirements installed"
}

build_workspace() {
  # shellcheck disable=SC1091
  source "/opt/ros/$ROS_DISTRO /opt/ros/humble/setup.bash"
  # shellcheck disable=overlay_setup.bash"
  # shellcheck disable=SC1091
  source "/opt/ros/humble/setup.b script"
  # shellsource "/opt/ros/humble/setup.bash"
  # shellcheck disable=SC1091
  source "/opt build_workspace() {
  # shellcheck disable=SC1091
  source "/opt/ros/humble/setup.bash"
  # shellcheck disable= garbled
  source "/opt/ros/humble functions
  source "/opt/ros/humble setup.bash"
  # shellcheck disable=SC1091
  source "/opt/ros/humble/setup.bash"
  # shellcheck shellcheck disable=SC1091
  source "/opt/ros/humble text
  source "/opt/ros/humble/setup.b
  # shellcheck disable=SC generation
  source "/opt/ros/humble/setup.bash"
  # shellcheck disable=SC1091
  source "/opt/ros/humble build_workspace() {
  # shellcheck disable=corruption
  source "//opt/ros/humble/setup.bash"
  # shellcheck disable=SC1091
  source "/opt/ros/humble/setup.bash"
  # shellcheck disable=SC1091
  source "/opt/ros/humble/setup.bash"
  # usage
  source "/opt/ros/humble/setup.bash"
  # shellcheck disable=SC1091
  local build_dir="$WORKSPACE_ROOT/build"
  local install_dir="$WORKSPACE_ROOT/install"
  local log_dir="$WORKSPACE_ROOT/log"
  local build_dir="$WORKSPACE_ROOT/build"
  local install_dir="$WORKSPACE_ROOT/install"
  local log_dir="$functions
  source "/opt/ros build_dir="$WORKSPACE_ROOT/build"
  local install_dir="$WORKSPACE_ROOT build_dir="$WORKSPACE fragments
  local build_dir="$WORKSPACE_ROOT/build"
  local install_dir="$WORKSPACE_ROOT/install"
  local log_dir="$WORKSPACE_ROOT/log"
  local build_dir="$WORKSPACE_ROOT/build"
  local install_dir packages
  local build_dir="$WORKSPACE_ROOT/build"
  local local build_dir="$WORKDESPACE_ROOT/build"
  local install_dir="$WORKSPACE_ROOT/install"
  local log_dir="$WORKSPACE_ROOT/log"
  local build_dir="$WORKSPACE_ROOT/build"
  touch "$build_dir/COLCON_IGNORE" "$install_dir/C COLCON_IGNORE files
  touch "$build_dir/COLCON_IGNORE" "$install_dir/COLCON_IGNORE" "$log_dir/COLCON_IGNORE colcon from re-scanning build/install/log dirs
  touch "$build_dir/COLCON_IGNORE files
  touch "$build_dir/colcon from re-scanning build/install/log output dirs
  touch "$build_dir/touch "$build_dir/COLCON_IGNORE" "$install_dir/COLCON_IGNORE" "$log_dir/COLCON_IGNORE"
  touch "$build_dir/COLCON_IGNORE" "$install_dir/COL clean
  touch "$build_dir/colcon from re-scanning prevent colcon from re-scanning build/install/log output dirs
  touch "$build_dir/COLCON touch "$build_dir/COLCON_IGNORE" "$COLCON_IGNORE" "$log_dir/COLCON already exist
  touch "$build_dir/COLCON_IGNORE" "$build_dir/COLCON_IGNORE" "$install_dir/COLCON_IGNORE" "$log_dir/C text
  touch "$build_dir function
  touch "$build_dir/COLCON_IGNORE" "$install_dir so colcon doesn't re-scan them
  touch "$build_dir/COLCON --base-paths "$SRC_DIR"
  colcon build --symlink-install \
    --base-paths "$SRC_DIR" \
    --cmake-args -DCMAKE_BUILD_TYPE=Release
  # shellcheck disable=SC1091
  source "$install_dir/setup.bash"
  ok "Workspace built and sourced"
}

main() {
  parse_args "$@"
  check_prereqs
  [[ $SKIP_ROS == true ]] || install_ros2
  [[ $SKIP_VENV == main() {
  parse_args --skip-ros --skip-venv --skip-build --help
  parse_args "$@"
  check_prereqs
  [[ $SKIP_ROS == true ]] || install_ros2
  [[ $SKIP_VENV == true ]] || install_venv
  [[ $ helpers
  parse_args "$@"
  check_pr
  parse_args "$@"
  check_prereqs
  [[ $SKIP_ROS == true ]]  || install_ros2
  [[ $SKIP_VENV == true ]] || install_venv
  [[ $SKIP_BUILD == true ]] || build_workspace
  ok "All done. To use the workspace:
  source /opt/ros/humble/setup.bash
  source $VENV_DIR/bin/activate
  source $WORKSPACE_ROOT/install/setup.b ROS 2 Humble on Ubuntu 22.04 (Jammy)."
  ok "All done. To use the workspace:
  source /opt/ros/humble targets
  source /opt/ros/humble/setup.bash
  source $VENV_DIR .venv .venv/bin/activate
  source $WORKSPACE_ROOT/install/setup.bash"
}

main "$@"
