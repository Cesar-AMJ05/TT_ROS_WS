# launch/taulidar_with_tf.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Nodo TauLidar
        Node(
            package='nav_autonoma',
            executable='test_taulidar_node',
            name='taulidar_node',
            parameters=[{
                'serial_port': 'None',
                'publish_rate': 30.0,
                'pointcloud_publish_rate': 10.0,  # Nueva tasa para pointcloud
                'publish_pointcloud': True,
                'use_compressed': True
            }]
        ),
        
        # Static Transform Publisher
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='taulidar_tf_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'taulidar_link']
        )
    ])