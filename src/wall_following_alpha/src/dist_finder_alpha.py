#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
import math

class DistFinderAlpha(Node):
    def __init__(self):
        super().__init__('dist_finder_alpha')

        # Suscribirse al topic del LIDAR
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',  # Cambiar este topic si es necesario
            self.getRange,
            10
        )

        # Publicar el mensaje con los resultados (distancia y ángulo)
        self.publisher = self.create_publisher(Float32, 'error', 10)

        # Parámetros de control
        self.setpoint = 1.0  # Setpoint deseado para la distancia al muro, ajustable
        # Parámetro del desplazamiento del vehículo
        self.desplazamiento = 0.2  # En metros

        self.get_logger().info("Nodo dist_finder_alphapy iniciado correctamente.")

    def getRange(self, msg: LaserScan):
        # Asumimos que msg.angle_min y msg.angle_increment están en radianes
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        ranges = msg.ranges

        # Calcular los índices de los ángulos de interés (85 y 90 grados)
        theta = 25  # Diferencia angular entre 85 y 90 grados
        angle_65_deg = math.radians(-65)
        angle_90_deg = math.radians(-90)
        angle_0_deg = math.radians(0)


        index_65 = int((angle_65_deg - angle_min) / angle_increment)
        index_90 = int((angle_90_deg - angle_min) / angle_increment)
        index_0 = int((angle_0_deg - angle_min) / angle_increment)

        # Verificar que los índices estén dentro del rango de las mediciones
        if 0 <= index_65 < len(ranges) and 0 <= index_90 < len(ranges):
            # Obtener las mediciones, usando 12m si hay valores infinitos
            frente = ranges[index_0] if not math.isinf(ranges[index_0]) else 12.0
            a = ranges[index_65] if not math.isinf(ranges[index_65]) else 12.0
            b = ranges[index_90] if not math.isinf(ranges[index_90]) else 12.0

            # Crear el mensaje para publicar (usamos Float32MultiArray)
            msg_out = Float32()

            # Calcular alpha (ángulo de orientación)
            alpha = math.atan2((a * math.cos(math.radians(theta)) - b), (a * math.sin(math.radians(theta))))
            # Calcular distancia al muro
            distancia_muro = b * math.cos(alpha)

            if ((frente < 2.0) & (distancia_muro < 2.0)):
                msg_out.data = 10.0  # Publicamos distancia y ángulo en grados

                # Publicar el mensaje
                self.publisher.publish(msg_out)
            else:
                # Calcular distancia al muro futura
                distancia_muro_2 = distancia_muro + self.desplazamiento * math.sin(alpha)

                # Calcular el error
                error = (self.setpoint - distancia_muro_2)

                msg_out.data = error  # Publicamos distancia y ángulo en grados

                # Publicar el mensaje
                self.publisher.publish(msg_out)

                # Registrar valores calculados
                self.get_logger().info(
                    f"a: {a:.2f}, b: {b:.2f}, alpha: {math.degrees(alpha):.2f} grados, "
                    f"distancia al muro: {distancia_muro:.2f} m, distancia al muro futura: {distancia_muro_2:.2f} m"
                )
        else:
            self.get_logger().warn("Los índices calculados están fuera del rango de medición.")

def main(args=None):
    rclpy.init(args=args)
    node = DistFinderAlpha()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
