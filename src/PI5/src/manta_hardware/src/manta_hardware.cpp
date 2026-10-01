#include "manta_hardware/manta_hardware.hpp"

#include <cmath>
#include <cstring>

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

#include "rclcpp/rclcpp.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace manta_hardware
{

// rad/s -> rpm
static double to_rpm(double rad_s) { return rad_s * 60.0 / (2.0 * M_PI); }
static double to_rad_s(double rpm) { return rpm * 2.0 * M_PI / 60.0; }

hardware_interface::CallbackReturn MantaHardware::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) !=
      hardware_interface::CallbackReturn::SUCCESS) {
    return hardware_interface::CallbackReturn::ERROR;
  }

  serial_port_ = "/dev/ttyAMA0";
  if (info_.hardware_parameters.count("serial_port")) {
    serial_port_ = info_.hardware_parameters["serial_port"];
  }

  if (info_.joints.size() != 2) {
    RCLCPP_ERROR(rclcpp::get_logger("MantaHardware"), "expected 2 joints, got %zu",
                 info_.joints.size());
    return hardware_interface::CallbackReturn::ERROR;
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> MantaHardware::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> interfaces;
  for (size_t i = 0; i < 2; i++) {
    interfaces.emplace_back(info_.joints[i].name, "velocity", &state_vel_[i]);
    interfaces.emplace_back(info_.joints[i].name, "position", &state_pos_[i]);
  }
  return interfaces;
}

std::vector<hardware_interface::CommandInterface> MantaHardware::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> interfaces;
  for (size_t i = 0; i < 2; i++) {
    interfaces.emplace_back(info_.joints[i].name, "velocity", &cmd_vel_[i]);
  }
  return interfaces;
}

bool MantaHardware::open_serial()
{
  fd_ = open(serial_port_.c_str(), O_RDWR | O_NOCTTY);
  if (fd_ < 0) {
    RCLCPP_ERROR(rclcpp::get_logger("MantaHardware"), "cant open %s", serial_port_.c_str());
    return false;
  }

  struct termios options;
  tcgetattr(fd_, &options);
  cfmakeraw(&options);
  cfsetispeed(&options, B115200);
  cfsetospeed(&options, B115200);
  options.c_cflag |= (CLOCAL | CREAD);
  options.c_cc[VMIN] = 0;
  options.c_cc[VTIME] = 2;  // 200 ms read timeout
  tcsetattr(fd_, TCSANOW, &options);

  // mega resets when the port opens, wait for it to boot
  sleep(2);
  tcflush(fd_, TCIOFLUSH);
  return true;
}

hardware_interface::CallbackReturn MantaHardware::on_activate(
  const rclcpp_lifecycle::State &)
{
  if (!open_serial()) {
    return hardware_interface::CallbackReturn::ERROR;
  }
  // make sure the wheels dont jump on startup
  ::write(fd_, "VS\n", 3);
  cmd_vel_[0] = cmd_vel_[1] = 0;
  state_vel_[0] = state_vel_[1] = 0;
  state_pos_[0] = state_pos_[1] = 0;
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn MantaHardware::on_deactivate(
  const rclcpp_lifecycle::State &)
{
  if (fd_ >= 0) {
    ::write(fd_, "VS\n", 3);
    close(fd_);
    fd_ = -1;
  }
  return hardware_interface::CallbackReturn::SUCCESS;
}

bool MantaHardware::read_status(double & rpm1, double & rpm2)
{
  // ask for the measured rpm, answer looks like "RPM1: 12.34 RPM2: 56.78"
  if (::write(fd_, "SS\n", 3) < 0) {
    return false;
  }

  std::string line;
  char c;
  // read lines until the rpm answer shows up, skip the echo lines
  for (int tries = 0; tries < 10; tries++) {
    line.clear();
    while (true) {
      int n = ::read(fd_, &c, 1);
      if (n <= 0) break;  // timeout
      if (c == '\n') break;
      if (c != '\r') line += c;
    }
    if (line.rfind("RPM1:", 0) == 0) {
      if (sscanf(line.c_str(), "RPM1: %lf RPM2: %lf", &rpm1, &rpm2) == 2) {
        return true;
      }
    }
    if (line.empty()) return false;  // timed out with nothing
  }
  return false;
}

hardware_interface::return_type MantaHardware::read(
  const rclcpp::Time &, const rclcpp::Duration & period)
{
  double rpm1, rpm2;
  if (!read_status(rpm1, rpm2)) {
    static rclcpp::Clock steady_clock(RCL_STEADY_TIME);
    RCLCPP_WARN_THROTTLE(rclcpp::get_logger("MantaHardware"),
                         steady_clock, 2000,
                         "no rpm answer from mega");
    return hardware_interface::return_type::OK;  // keep last state
  }

  double rpms[2] = {rpm1, rpm2};
  for (int i = 0; i < 2; i++) {
    // encoder only counts magnitude, so direction comes from the last command
    double dir = 0;
    if (last_rpm_[i] > 0) dir = 1;
    else if (last_rpm_[i] < 0) dir = -1;
    state_vel_[i] = to_rad_s(rpms[i]) * dir;
    state_pos_[i] += state_vel_[i] * period.seconds();
  }
  return hardware_interface::return_type::OK;
}

hardware_interface::return_type MantaHardware::write(
  const rclcpp::Time &, const rclcpp::Duration &)
{
  double rpm1 = to_rpm(cmd_vel_[0]);
  double rpm2 = to_rpm(cmd_vel_[1]);

  // both wheel targets in one atomic packet so the mega updates them together
  char buf[64];
  int n = snprintf(buf, sizeof(buf), "V:%.1f,%.1f\n", rpm1, rpm2);
  if (::write(fd_, buf, n) < 0) {
    static rclcpp::Clock steady_clock(RCL_STEADY_TIME);
    RCLCPP_WARN_THROTTLE(rclcpp::get_logger("MantaHardware"),
                         steady_clock, 2000,
                         "serial write failed");
    return hardware_interface::return_type::ERROR;
  }

  last_rpm_[0] = rpm1;
  last_rpm_[1] = rpm2;
  return hardware_interface::return_type::OK;
}

}  // namespace manta_hardware

PLUGINLIB_EXPORT_CLASS(manta_hardware::MantaHardware, hardware_interface::SystemInterface)
