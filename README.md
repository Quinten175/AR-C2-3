# AR-C2-3

## Installation

One-liner (Ubuntu 24.04, ROS 2 Jazzy):

```bash
curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash
```

The script clones this repository into `./AR-C2-3`, installs ROS 2 Jazzy and its dependencies, creates a Python venv (`.venv`), and builds the workspace with `colcon`.

Pass options through the pipe with `bash -s --`:

```bash
curl -fsSL https://raw.githubusercontent.com/Quinten175/AR-C2-3/main/install.sh | bash -s -- --skip-ros
```

| Option         | Effect                              |
| -------------- | ----------------------------------- |
| `--skip-ros`   | Skip ROS 2 installation             |
| `--skip-venv`  | Skip Python venv + pip requirements |
| `--skip-build` | Skip the colcon build               |

Or clone and run manually:

```bash
git clone https://github.com/Quinten175/AR-C2-3.git
cd AR-C2-3
./install.sh
```

After installing, source the environment in every new shell:

```bash
source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
source install/setup.bash
```

### Build Robot
Pi\
Chassis\
2+Motor\
LiDAR sensor\
Battery

### Basic ROS
Control node connected to /cmd_vel\
LiDAR publishing /Scan\
Odometry /odon\
TfTree

### PWM
### Custom Wheel design
### PID velocity control
