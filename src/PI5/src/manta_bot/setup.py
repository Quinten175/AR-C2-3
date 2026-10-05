from setuptools import find_packages, setup
import os
from glob import glob
 
package_name = 'manta_bot'

## Recursively collect files under src so nested folders (e.g. the ncnn model
## subdirectory) are installed too, otherwise they are not found after colcon build
def package_files(dest, src):
    out = []
    for root, _, files in os.walk(src):
        if files:
            rel = os.path.relpath(root, src)
            target = dest if rel == '.' else os.path.join(dest, rel)
            out.append((target, [os.path.join(root, f) for f in files]))
    return out

def generate_data_files():
    data_files = [
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'map'), glob('map/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'UI'), glob('manta_bot/UI/*.html')),
        (os.path.join('share', package_name, 'UI', 'static'), glob('manta_bot/UI/static/*')),
    ]
    # YOLO models (yolo26n.pt + yolo26n_ncnn_model/)
    # data_files += package_files(os.path.join('share', package_name, 'models'), 'manta_bot/Cam/models')
    return data_files

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    package_data={
        'manta_bot': [
            'UI/*.html',
            'UI/static/*',
        ],
    },
    data_files=generate_data_files(),

    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='quin',
    maintainer_email='quintenvandervalk@gmail.com',
    description='Manta Bot package with diff-drive controller support',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            f'static_odom_publisher = {package_name}.Lidar.static_odom_publisher:main',
            f'cmd_vel_dummy = {package_name}.Movement.cmd_vel_publisher:main',
            f'activate_mapping = {package_name}.Lidar.activate_mapping:main',
            f'wheel_test = {package_name}.Sim.wheel_test:main',
            f'movement_handler = {package_name}.Movement.movement_handler:main',
            f'gamepad_controller = {package_name}.Movement.controller:main',
            f'UI_app = {package_name}.UI.UI_app:main',
<<<<<<< HEAD
            f'serial_debug = {package_name}.Movement.serial_debug:main',
            # f'person_fusion = {package_name}.translation.test_file:main',
            # f'fake_scan_c = {package_name}.translation.fakelidarnode_c:main',
            # f'fake_scan = {package_name}.translation.fakelidarnode:main',
            # f'camera_publisher = {package_name}.Cam.camera_publisher:main',
            # f'yolo_detector = {package_name}.Cam.yolo26_ros2:main', 
            # f'stream = {package_name}.Cam.stream:main',
            # f'stream_node = {package_name}.Cam.stream_node:main',
=======
            f'person_fusion = {package_name}.translation.test_file:main'
            
>>>>>>> 7575e69 (fix)

            f'make_nodes = {package_name}.Navigation.make_nodes:main',
            f'waypoint_orderer= {package_name}.Movement.waypoint_orderer:main',
        ],
        'ros2_control_systems': [
            f'manta_bot_hardware = {package_name}.Movement.movement_handler:MantaBotHardware',
        ],
    },
)   
 
