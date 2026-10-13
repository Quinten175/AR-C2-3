cmake_minimum_required(VERSION 3.8)
project(manta_hardware)

find_package(ament_cmake REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)

add_library(manta_hardware SHARED src/manta_hardware.cpp)

target_include_directories(manta_hardware PRIVATE include)

ament_target_dependencies(manta_hardware
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
)

pluginlib_export_plugin_description_file(hardware_interface manta_hardware.xml)

install(TARGETS manta_hardware
  DESTINATION lib
)

install(DIRECTORY include/
  DESTINATION include
)

ament_package()
