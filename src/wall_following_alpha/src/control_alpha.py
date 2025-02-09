#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32

class ControlAlpha(Node):
    def __init__(self):
        super().__init__('control_alpha')

        # Suscribirse al topic donde recibimos la distancia y el ángulo
        self.subscription = self.create_subscription(
            Float32,  # Para la distancia (asumimos que es un valor Float32)
            '/error',  # Topic donde recibimos distancia y ángulo
            self.controller,
            10
        )

        # Publicar en cmd_vel_cmd
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel_ctrl',  # Topic donde enviamos los comandos procesados
            10
        )

        # Parámetros de control
        self.Kp = 0.3  # Constante proporcional
        self.Kd = 0.05  # Constante derivativa
        self.previous_error = 10.0  # Error anterior para calcular la derivada
        self.previous_time = self.get_clock().now()  # Tiempo anterior

        self.get_logger().info("Nodo control_alpha iniciado correctamente.")

    def controller(self, msg):
        # Asumimos que recibimos la distancia en 'msg.data' y el ángulo en un atributo adicional
        error = msg.data  # Suponemos que el primer valor es la distancia

        # Log de los valores recibidos
        self.get_logger().info(f"error {error}")

        # Calcular el tiempo transcurrido
        current_time = self.get_clock().now()
        delta_time = (current_time - self.previous_time).nanoseconds / 1e9  # Convertir a segundos

        # Calcular la derivada del error
        derivative_error = (error - self.previous_error) / delta_time if delta_time > 0 else 0.0

        # Control proporcional y derivativo (PD)
        angular_velocity = self.Kp * error + self.Kd * derivative_error


        # Crear el mensaje Twist con los comandos calculados
        cmd_vel_msg = Twist()
        cmd_vel_msg.linear.x = 0.5  # Velocidad lineal constante (puedes ajustarlo si es necesario)
        cmd_vel_msg.angular.z = angular_velocity  # Enviar el ángulo ajustado

        # Publicar el mensaje en cmd_vel_cmd
        self.publisher.publish(cmd_vel_msg)

        # Log de lo que estamos enviando
        self.get_logger().info(f"Comando enviado: angular={angular_velocity}, lineal={cmd_vel_msg.linear.x}")

        # Actualizar el error y el tiempo anteriores
        self.previous_error = error
        self.previous_time = current_time

def main(args=None):
    rclpy.init(args=args)
    node = ControlAlpha()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
