from setuptools import find_packages, setup

package_name = 'translation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rik-noorman',
    maintainer_email='kirnor2005@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'test_file = translation.test_file:main',
            'fakelidarnode = translation.fakelidarnode:main',
            'test_file_t = translation.test_file_t:main',
            'fakelidarnode_c = translation.fakelidarnode_c:main',
        ],
    },
)
