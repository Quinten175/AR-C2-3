#ifndef MANTA_HARDWARE_HPP
#define MANTA_HARDWARE_HPP

#include <string>
#include <vector>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "rclcpp_lifecycle/state.hpp"

namespace manta_hardware
{

class MantaHardware : public hardware_interface::SystemInterface
{
public:
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;
  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;
  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  bool open_serial();
  bool read_status(double & rpm1, double & rpm2);

  int fd_ = -1;
  std::string serial_port_;

  // command and state per wheel, index 0 = left, 1 = right
  double cmd_vel_[2] = {0, 0};    // rad/s
  double state_vel_[2] = {0, 0};  // rad/s
  double state_pos_[2] = {0, 0};  // rad

  // last rpm we sent, the mega only reports rpm magnitude
  // so we take the sign from here
  double last_rpm_[2] = {0, 0};
};

}  // namespace manta_hardware

#endif
