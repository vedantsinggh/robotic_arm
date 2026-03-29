from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'piper_task'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/piper_task/meshes', glob('meshes/*.stl')),  # ✅ THIS LINE
        ('share/piper_task/models', glob('models/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mirage',
    maintainer_email='vedantsinggh@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'add_objects = piper_task.add_objects:main',
            'move_arm = piper_task.move_arm:main',
        ],
    },
)
