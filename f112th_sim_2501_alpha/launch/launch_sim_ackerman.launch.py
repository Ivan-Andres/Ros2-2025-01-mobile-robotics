# library to move between files and folders in the O.S.
import os

from ament_index_python.packages import get_package_share_directory

# libraries to define the Launch file and Function
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='f112th_sim_2501_alpha' #<--- CHANGE ME
    twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')

    ackerman = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','acker.launch.py'
                )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')
    
    joystick = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','joystick.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )
    
    twist_mux_node = Node(package='twist_mux', 
                    executable='twist_mux',
                    parameters=[twist_mux_params,{'use_sim_time': True}],
                    remappings=[('/cmd_vel_out','/cmd_vel')]
    )

    #Agregar tu nodo laser_scan_reader aquí
    laser_scan_reader_node = Node(
        package=package_name,  # Reemplaza 'tu_paquete' con el nombre de tu paquete
        executable='laser_scan_reader',  # Nombre del ejecutable de tu nodo
        output='screen',  # Esto hace que el nodo imprima en la consola
        parameters=[{'use_sim_time': True}]  # Parametro de tiempo de simulación (si es necesario)
    )

    # Launch them all!
    return LaunchDescription([
        ackerman,
        gazebo,
        spawn_entity,
        joystick,
        twist_mux_node,
        laser_scan_reader_node,
    ])