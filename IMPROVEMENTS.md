# AR-C2-3 Improvement Recommendations

## Critical (affect correctness)

### 1. Wheel geometry mismatch between code and controller config

`movement_handler.py:8-9` defines `WHEEL_RADIUS = 0.0295`, `WHEEL_SEPARATION = 0.255`.
`diff_drive_controller.yaml:16-17` has `wheel_radius: 0.040`, `wheel_separation: 0.265`.

The controller will compute different wheel velocities than what the movement handler publishes. Pick one source of truth and align both files. The URDF mesh dimensions suggest ~0.04 m radius (8 cm diameter wheels), so the YAML values may be closer to reality — but verify against the actual hardware.

### 2. No encoder feedback loop from Arduino to ROS 2

`MantaBotHardware.read()` at `movement_handler.py:57-61` just mirrors `_cmd` into `_state`. The Arduino runs closed-loop PID on wheel RPM, but those measured values never make it back to the Pi. The diff_drive_controller has no real odometry source — it's publishing fake velocity state. Add a serial read path that parses `SS` responses and feeds them into `export_state_interfaces()`.

### 3. cmd_vel_publisher.py multiplier mismatch

`movement_handler.py:128-129` applies a `*2` factor in the RPM calculation for the dummy publisher, but `_drive_wheels()` at line 70-72 does not. The dummy node will publish values that are twice what the hardware interface actually sends to the Arduino.

---

## High (affect reliability / maintainability)

### 4. No `.gitignore` at project root

The `build/`, `install/`, and `log/` directories are untracked but there's no `.gitignore`. Add one:
```
build/
install/
log/
*.pyc
__pycache__/
.pio/build/
.vscode/
*.egg-info/
```

### 5. YOLO detector hardcodes class filter to person only

`yolo26_ros2.py:75`: `kwargs = {"verbose": False, "classes": [0]}` — this silently discards all detections except COCO class 0 (person). If the model detects other classes or you want to detect multiple objects, remove this filter or make it a parameter.

### 6. Serial port hardcoded to Pi-specific path

`serial_com.py:9`: `PORT = '/dev/ttyAMA0'`. This is the Pi's UART. On a laptop or different board it'll fail silently (stderr message, no exception). Consider making it a ROS 2 parameter with a fallback like `/dev/ttyUSB0`.

### 7. No license declared

`package.xml:8`: `<license>TODO: License declaration</license>`. Pick one (MIT, Apache-2.0, GPL) and update both the package XML and add a `LICENSE` file to the repo root.

---

## Medium (nice-to-have improvements)

### 8. No launch file for diff_drive_controller / ros2_control

`static_slam.launch.py` starts robot_state_publisher, RPLIDAR, SLAM, UI — but never launches the `diff_drive_controller` or `ros2_control_node`. The hardware interface is registered in `setup.py:79` but nothing activates it. Add a launch file that loads ros2_control and starts both controllers.

### 9. Arduino PID constants are magic numbers

`closed_loop.cpp:7-8`: `PID pid2(0.68, 8.2)` and `pid1(0.71, 7.5)`. No documentation of how these were tuned or what they mean (P gain / D gain? P / I?). Add a header comment with the tuning method and expected units.

### 10. PWM floor is hardcoded

`closed_loop.cpp:19`: `const uint8_t PWM_FLOOR = 80;` — this is the minimum duty cycle to overcome motor stalling. It's sensor-specific (motor brand, supply voltage, load). Consider making it configurable via a serial command or EEPROM.

### 11. No platformio upload configuration

`platformio.ini` has no `upload_port`, `upload_speed`, or `board_build.f_cpu`. Add these for reproducible builds:
```ini
upload_port = /dev/ttyACM0
upload_speed = 115200
build_flags = -O2
```

### 12. YOLO model duplicated across directories

`yolo26n.pt` (5.5 MB) exists in `Cam/models/`, `Cam/pi_stream/`, and is referenced by both the main node and the pi_stream sub-package. Install via setup.py copies it to all locations, but a single source of truth with symlinks or a shared data directory would be cleaner.

### 13. No ROS 2 parameter for slam_config.yaml path

`static_slam.launch.py:14-18` hardcodes the SLAM config path. Make it a launch argument so you can switch between mapping/exploration modes without editing the file.

---

## Low (polish)

### 14. Arduino `handle_line()` echoes every command to serial

Line 39: `Serial.println("Received: " + cmd);` — this adds latency on a 115200 baud link and clutters the debug stream during fast control loops. Consider making it conditional on a parameter or removing it in production.

### 15. No telemetry / health monitoring from Arduino

The firmware has no way to report serial errors, buffer overflows, or encoder saturation back to the Pi. A periodic heartbeat message (e.g., every 1 second) with uptime and error counters would help diagnose issues.

### 16. `setup.cfg` is minimal

At 87 bytes it likely just has `[metadata]`. Add flake8/pep257 config so tests pass consistently across environments:
```ini
[flake8]
max-line-length = 120
exclude = build, install, log, .pio
```
