from setuptools import find_packages, setup

import os
from glob import glob

package_name = 'nav_autonoma'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Incluir archivos de lanzamiento
        (os.path.join('share', package_name, 'launch'), 
         glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='orangepi',
    maintainer_email='orangepi@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # Nodos principales del sistema
            'odometry_node = nav_autonoma.odometry_node:main',
            'motor_controller_node = nav_autonoma.motor_controller_node:main',
            
            # Nodos de prueba individuales
            'test_encoder_node = nav_autonoma.test_encoder_node:main',
            'test_mpu_node = nav_autonoma.test_mpu_node:main',
            'test_sdc40_node = nav_autonoma.test_sdc40_node:main',
            'test_led_node = nav_autonoma.test_led_node:main',
            'test_motor_node = nav_autonoma.test_motor_node:main',
            'test_pwm_node = nav_autonoma.test_pwm_node:main',
            'test_move_node = nav_autonoma.test_move_node:main',
            'test_audio_node = nav_autonoma.test_audio_node:main',
        ],
    },
)
