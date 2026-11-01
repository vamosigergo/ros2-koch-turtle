from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    order_argument = DeclareLaunchArgument(
        'order',
        default_value='1',
        choices=['0', '1', '2', '3'],
        description='A Koch-görbe rendje.',
    )

    order = ParameterValue(LaunchConfiguration('order'), value_type=int)

    return LaunchDescription([
        order_argument,
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        Node(
            package='koch_turtle',
            executable='koch_controller',
            name='koch_controller',
            output='screen',
            parameters=[{'order': order}],
        ),
    ])
