# AR-C2-3 — Manta mobile robot

AR-C2-3 is a differential-drive mobile robot project. The Raspberry Pi runs
ROS 2 Jazzy for robot description, drive control, LiDAR mapping, navigation,
waypoint routing, and the web control interface. An Arduino Mega runs the
motor and encoder firmware and receives wheel-speed commands over serial.

This README is the project map and the main setup/run guide. The installer is
[`install.sh`](./install.sh); its supported platform and options are described
in [Installation](#installation).

## Contents

- [System overview](#system-overview)
- [Repository map](#repository-map)
- [Requirements](#requirements)
- [Installation](#installation)
- [Build and run](#build-and-run)
- [Manual ROS control and diagnostics](#manual-ros-control-and-diagnostics)
- [Configuration and hardware](#configuration-and-hardware)
- [Tests and development](#tests-and-development)
- [Known setup notes](#known-setup-notes)

## System overview

```text
Web UI / Nav2 / gamepad / Traveling salesmen and rviz publish nodes
          │  ROS 2 /cmd_vel
          ▼
Raspberry Pi 5 — manta_bot + manta_hardware (ros2_control)
          │  serial, 115200 baud
          ▼
Arduino Mega — closed-loop wheel speed control
          │
          ▼
Motors, encoders, LiDAR, camera
```

The ROS robot model and drive controller are in the `manta_bot` package.
`manta_hardware` is the C++ ros2_control plugin that sends both wheel targets
as one serial packet. The Mega firmware parses that packet and runs the
closed-loop motor control. LiDAR mapping uses `slam_toolbox`; the navigation
launch adds Nav2 and the project waypoint tools.

## Repository map

| Path | Contents |
| --- | --- |
| [`install.sh`](./install.sh) | Ubuntu 24.04 / ROS 2 Jazzy installer, Python virtual environment setup, and colcon build |
| [`requirements.txt`](./requirements.txt) | Extra Python packages installed into `.venv` |
| [`PI5/src/manta_bot/`](./PI5/src/manta_bot/) | Main ROS 2 Python package, robot model, launch files, parameters, web UI, and perception code |
| [`PI5/src/manta_bot/package.xml`](./PI5/src/manta_bot/package.xml), [`setup.py`](./PI5/src/manta_bot/setup.py), [`setup.cfg`](./PI5/src/manta_bot/setup.cfg) | ROS dependencies, Python package metadata, installed assets, and `ros2 run` commands |
| [`PI5/src/manta_bot/main.js`](./PI5/src/manta_bot/main.js), [`package.json`](./PI5/src/manta_bot/package.json) | Optional Node.js launcher for the camera/detector/stream chain |
| [`PI5/src/manta_bot/manta_bot/Movement/`](./PI5/src/manta_bot/manta_bot/Movement/) | `cmd_vel` tools, gamepad controller, serial helpers, motion handler, and waypoint ordering |
| [`PI5/src/manta_bot/manta_bot/Lidar/`](./PI5/src/manta_bot/manta_bot/Lidar/) | SLAM lifecycle activation helper |
| [`PI5/src/manta_bot/manta_bot/Navigation/`](./PI5/src/manta_bot/manta_bot/Navigation/) | Waypoint collection helper |
| [`PI5/src/manta_bot/manta_bot/Cam/`](./PI5/src/manta_bot/manta_bot/Cam/) | Camera publisher, YOLO detector, MJPEG stream nodes, and model files |
| [`PI5/src/manta_bot/manta_bot/UI/`](./PI5/src/manta_bot/manta_bot/UI/) | Flask web interface (`UI_app.py`), HTML template, and static styles |
| [`PI5/src/manta_bot/launch/`](./PI5/src/manta_bot/launch/) | ROS launch descriptions for drive, SLAM, navigation, and waypoint planning |
| [`PI5/src/manta_bot/config/`](./PI5/src/manta_bot/config/) | Differential-drive, SLAM, and Nav2 parameters |
| [`PI5/src/manta_bot/urdf/`](./PI5/src/manta_bot/urdf/) | Robot links, joints, ros2_control configuration, and serial-port setting |
| [`PI5/src/manta_bot/meshes/`](./PI5/src/manta_bot/meshes/) | STL visual/collision meshes referenced by the URDF |
| [`PI5/src/manta_hardware/`](./PI5/src/manta_hardware/) | C++ ros2_control serial hardware plugin |
| [`Mega/`](./Mega/) | PlatformIO Arduino Mega firmware project |
| [`Mega/src/main.cpp`](./Mega/src/main.cpp) | Serial protocol, command timeout, and periodic closed-loop update |
| [`Mega/src/closed_loop.cpp`](./Mega/src/closed_loop.cpp) | Per-wheel closed-loop speed controller |
| [`Mega/src/motor_control.cpp`](./Mega/src/motor_control.cpp) | Motor driver output and emergency stop |
| [`Mega/src/encoder.cpp`](./Mega/src/encoder.cpp) | Wheel encoder measurement |
| [`Mega/src/pid.cpp`](./Mega/src/pid.cpp) | PID control implementation |
| [`Documentation/`](./Documentation/) | System diagrams and documentation index |
| [`PI5/src/manta_bot/test/`](./PI5/src/manta_bot/test/) | ROS package lint/style tests |

The `manta_bot` Python package also contains simulation helpers under `Sim/`
and experimental translation/test modules under `translation/`.

### ROS launch files

| Launch file | Purpose |
| --- | --- |
| `diff_drive.launch.py` | Loads the robot model, starts ros2_control and robot_state_publisher, and spawns the joint-state and diff-drive controllers |
| `slam.launch.py` | Starts the RPLIDAR driver, SLAM Toolbox, mapping activation helper, and Flask UI |
| `navigation.launch.py` | Includes SLAM, waypoint tools, and Nav2 (Nav2 starts after a short delay) |
| `tsp.launch.py` | Starts waypoint collection and ordering nodes |

### ROS Python entry points

The registered `manta_bot` console scripts are declared in
[`setup.py`](./PI5/src/manta_bot/setup.py). Important ones include:

| Command | Source file | Role |
| --- | --- | --- |
| `ros2 run manta_bot UI_app` | `manta_bot/UI/UI_app.py` | Flask UI and ROS command publisher |
| `ros2 run manta_bot gamepad_controller` | `manta_bot/Movement/controller.py` | Publishes velocity commands from `/dev/input/js0` |
| `ros2 run manta_bot activate_mapping` | `manta_bot/Lidar/activate_mapping.py` | Activates SLAM after receiving LiDAR data |
| `ros2 run manta_bot make_nodes` | `manta_bot/Navigation/make_nodes.py` | Collects clicked map points into a waypoint list |
| `ros2 run manta_bot waypoint_orderer` | `manta_bot/Movement/waypoint_orderer.py` | Orders waypoints and submits them to Nav2; route algorithm is in `tour_planner.py` |
| `ros2 run manta_bot wheel_test` | `manta_bot/Sim/wheel_test.py` | Wheel test helper |
| `ros2 run manta_bot serial_debug` | `manta_bot/Movement/serial_debug.py` | Reads serial output for debugging |

Other useful source files: `manta_bot/Movement/serial_com.py` contains the
Python serial protocol helper; `movement_handler.py` contains the command
monitoring and hardware-interface code; and `cmd_vel_publisher.py` is a
dummy velocity publisher for development.

Camera-related Python modules and the Node launcher are present in the source
tree, but their ROS console-script registrations are currently commented out
in `setup.py`. See [Known setup notes](#known-setup-notes) before relying on
those launch paths.

## Requirements

### For the automated ROS installation

- Ubuntu 24.04 (Noble); the installer targets this release and ROS 2 Jazzy.
- A non-root account with `sudo`.
- Internet access to fetch apt packages and Python packages.
- `curl` for the one-line installer. `git` is installed by the script if
  needed.

The installer installs ROS 2 Jazzy `ros-base`, SLAM Toolbox, Nav2 bringup,
colcon/rosdep, system build tools, and the Python requirements into a project
virtual environment.

The Python requirements from [`requirements.txt`](./requirements.txt) are
NumPy, Flask, pyserial, OpenCV, Pillow, and Ultralytics. ROS package
dependencies are declared in [`package.xml`](./PI5/src/manta_bot/package.xml)
and [`package.xml`](./PI5/src/manta_hardware/package.xml). The robot stack
also relies on ROS packages for ros2_control, RPLIDAR, SLAM Toolbox, and Nav2.

### Hardware/runtime requirements

- Raspberry Pi 5 or another supported Ubuntu 24.04 host with ROS 2 Jazzy.
- Arduino Mega with this project's firmware uploaded.
- A compatible RPLIDAR connected to the configured serial device.
- Robot motors, encoders, and a motor driver wired for the firmware.
- Camera and/or joystick only when using the corresponding optional nodes.

The robot hardware interface defaults to `/dev/ttyAMA0` at 115200 baud.
`slam.launch.py` configures the LiDAR at `/dev/ttyUSB0`. Verify the actual
device names and access permissions on the target machine before running.

## Installation

### Recommended: one-line installer

From Ubuntu 24.04, run:

```bash
curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash
```

When invoked through the pipe, the installer clones the repository into
`$PWD/AR-C2-3` and runs the on-disk copy. To choose a different clone
directory, set `AR_C2_3_DIR`:

```bash
AR_C2_3_DIR="$HOME/robot/AR-C2-3" \
  bash -c 'curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash'
```

The script must not be run as root. It uses `sudo` for apt operations.

### Clone first, then install

```bash
git clone https://github.com/Quinten175/AR-C2-3.git
cd AR-C2-3
./install.sh
```

### Installer options

| Option | Effect |
| --- | --- |
| `--skip-ros` | Do not install ROS 2 packages; ROS 2 Jazzy must already be installed |
| `--skip-venv` | Do not create `.venv` or install `requirements.txt` |
| `--skip-build` | Do not build the colcon workspace |
| `--help` | Print installer usage and supported environment variables |

For example, to use existing ROS and Python setup but build this workspace:

```bash
./install.sh --skip-ros --skip-venv
```

`ROS_DISTRO` can override the installer's default `jazzy`, but Ubuntu 24.04
with Jazzy is the tested/targeted configuration.

### After installation

In each new terminal, source the ROS, Python, and workspace environments:

```bash
cd /path/to/AR-C2-3
source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
source install/setup.bash
```

The Python virtual environment is created at the repository root as `.venv`.
The installer adds ROS Python site-packages to that environment so Python ROS
modules can be imported while the venv is active.

## Build and run

### Build the ROS workspace manually

From the repository root, after sourcing ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --base-paths PI5/src \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

The install script runs the equivalent colcon build automatically.

### Upload the Arduino firmware

Install PlatformIO Core separately if it is not already installed and upload the code to the MCU.

Replace `/dev/ttyACM0` with the port used by the Mega during firmware upload.
The firmware's serial protocol runs at 115200 baud. Do not assume the upload
port is the same as the runtime UART used by the Pi's ros2_control plugin.

### Start the robot

The launches below are separate processes. Run the drive stack first in one
terminal, and then start SLAM or the full navigation stack in another. Source
the environment in each terminal as described above.

1. Start the robot model and drive controller:

   ```bash
   ros2 launch manta_bot diff_drive.launch.py
   ```

2. For SLAM plus Nav2 and waypoint routing, use this instead of launching
   `slam.launch.py` separately:

   ```bash
   ros2 launch manta_bot navigation.launch.py
   ```

   Keep the `diff_drive.launch.py` process running alongside it. Navigation
   parameters are in `config/nav2_params.yaml`; the launch expects a working
   map/odom/base transform tree and LiDAR `/scan` data.

### Manual ROS control and diagnostics

With the environment sourced and the robot drive launch running:

```bash
# List active ROS nodes and topics
ros2 node list
ros2 topic list

# Watch velocity commands and LiDAR scans
ros2 topic echo /cmd_vel
ros2 topic echo /scan

# Drive from a gamepad at /dev/input/js0
# NOTE: skip this if you want to use the traveling salesmen problem. That is used with RVIZ publish points and the trigger command below
ros2 run manta_bot gamepad_controller 

# Clear the collected waypoint points
ros2 service call /tsp/clear_nodes std_srvs/srv/Trigger {}
```

The waypoint flow collects map points from `/clicked_point`, publishes the
list on `/tsp/nodes`, and waits for `/tsp/trigger` before sending its route to
Nav2. The UI's waypoint action publishes that trigger.

## Configuration and hardware

- **Robot shape and ros2_control binding:** [`robotassembly.urdf`](./PI5/src/manta_bot/urdf/robotassembly.urdf).
- **Drive-controller wheel names, dimensions, timeout, and frames:** [`diff_drive_controller.yaml`](./PI5/src/manta_bot/config/diff_drive_controller.yaml).
- **SLAM frames, scan topic, and mapping parameters:** [`slam_config.yaml`](./PI5/src/manta_bot/config/slam_config.yaml).
- **Nav2, costmaps, velocity smoothing, and collision monitoring:** [`nav2_params.yaml`](./PI5/src/manta_bot/config/nav2_params.yaml).
- **Hardware serial device default:** `/dev/ttyAMA0` in the URDF/hardware plugin; change the URDF hardware parameter if the actual Pi connection differs.
- **LiDAR serial device:** `/dev/ttyUSB0` in [`slam.launch.py`](./PI5/src/manta_bot/launch/slam.launch.py).
- **Motor serial protocol:** `V:<left-rpm>,<right-rpm>` updates both wheel targets together; `VS` stops; firmware also retains legacy `M1F`, `M1R`, `M2F`, `M2R`, and emergency-stop commands.
- **Safety behavior:** Mega firmware stops closed-loop motion if commands are not received for 500 ms. Test with the wheels raised and an accessible power cutoff before putting the robot on the ground.

The ROS mapping, navigation, and robot-model diagrams are in
[`Documentation/`](./Documentation/):

- [`architecture_diagram.svg`](./Documentation/architecture_diagram.svg)
- [`information_flow_diagram.svg`](./Documentation/information_flow_diagram.svg)
- [`responsibility_division_diagram.svg`](./Documentation/responsibility_division_diagram.svg)
- [`tf_tree.svg`](./Documentation/tf_tree.svg)

## Tests and development

The ROS Python package includes copyright, flake8, and PEP 257 checks. With
the workspace built and environment sourced:

```bash
colcon test --base-paths PI5/src
colcon test-result --verbose
```

Build only the relevant ROS package when iterating:

```bash
colcon build --symlink-install --base-paths PI5/src --packages-select manta_bot manta_hardware
```

Build the Mega firmware without uploading it:

```bash
pio run -d Mega
```

## Known setup notes

- The ROS installer and default commands target Ubuntu 24.04 / ROS 2 Jazzy.
- The `manta_bot` manifest declares a dependency on `manta_bot_interfaces`,
  but that package is not present under `PI5/src` in this repository. Ensure
  the dependency is available in the ROS environment (or add its source
  package) if colcon reports it as missing.
- Camera modules are in the source tree, but `camera_publisher`, `yolo_detector`,
  and `stream` console-script registrations are commented out in `setup.py`.
  The Node launcher (`PI5/src/manta_bot/main.js`) expects those commands to
  exist and also expects `ngrok`; it is not part of the standard installation
  workflow.
- Some generated model files are large and the YOLO runtime may require
  additional dependencies or model compatibility work on the target hardware.
- Confirm both serial devices, permissions, and UART wiring before launching
  the robot. A serial port open by another process cannot be used at the same
  time by the ROS hardware plugin.
