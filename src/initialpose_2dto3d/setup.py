import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'initialpose_2dto3d'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maintainer',
    maintainer_email='maintainer@example.com',
    description='Relay 2D initial pose to 3D with heightmap compensation',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'initialpose_2dto3d_node = initialpose_2dto3d.initialpose_2dto3d_node:main',
            'generate_heightmap = scripts.generate_heightmap:main',
        ],
    },
)
