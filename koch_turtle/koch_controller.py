import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose
from koch_turtle.koch_geometry import koch_points


class KochController(Node):
    """Célpontok követése pozíció-visszacsatolással és P-szabályozással."""

    def __init__(self):
        super().__init__('koch_controller')
        self.order = self.declare_parameter('order', 1).value
        self.shape = self.declare_parameter('shape', 'curve').value

        if self.order not in range(4):
            raise ValueError('Az order értéke 0, 1, 2 vagy 3 lehet.')

        self.k_linear = 1.5
        self.k_angular = 4.0
        self.max_linear = 1.5
        self.max_angular = 3.0
        self.position_tolerance = 0.015
        self.heading_tolerance = 0.05  # Radián, körülbelül 2,9 fok.

        self.pose = None
        self.targets = []
        self.target_index = 0
        self.max_endpoint_error = 0.0

        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )
        self.timer = self.create_timer(0.02, self.control_step)

    def pose_callback(self, msg):
        """Az első mért pozícióból tervezzük meg a pályát."""
        if self.pose is None:
            self.targets = self.build_targets(msg.x, msg.y)
            self.get_logger().info(f'Célpontok száma: {len(self.targets)}')

        self.pose = msg

    def build_targets(self, x, y):
        """A nyitott Koch-görbe vagy a zárt Koch-hópehely célpontjai."""
        side = 4.0
        a = (x, y)
        b = (x + side, y)

        if self.shape == 'curve':
           return koch_points(a, b, self.order)[1:]

        if self.shape != 'snowflake':
           raise ValueError("A shape értéke 'curve' vagy 'snowflake' lehet.")

        # A harmadik csúcs az első oldal alatt van.
        height = side * math.sqrt(3.0) / 2.0
        c = (x + side / 2.0, y - height)

        targets = []
        for start, end in [(a, b), (b, c), (c, a)]:
            targets.extend(koch_points(start, end, self.order)[1:])

        return targets

    def control_step(self):
        if self.pose is None:
            return

        target_x, target_y = self.targets[self.target_index]
        dx = target_x - self.pose.x
        dy = target_y - self.pose.y
        distance = math.hypot(dx, dy)

        if distance <= self.position_tolerance:
            self.publisher.publish(Twist())
            self.max_endpoint_error = max(self.max_endpoint_error, distance)
            self.target_index += 1

            if self.target_index == len(self.targets):
                self.timer.cancel()
                self.get_logger().info(
                    f'Rajzolás kész. Elért célpontok: {self.target_index}. '
                    f'Legnagyobb célponteltérés: {self.max_endpoint_error:.4f}.'
                )
            return

        desired_heading = math.atan2(dy, dx)
        angle_error = desired_heading - self.pose.theta

        # A legrövidebb fordulás előjeles szöge a [-pi, pi] tartományban.
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        command = Twist()
        command.angular.z = max(
            -self.max_angular,
            min(self.max_angular, self.k_angular * angle_error)
        )

        if abs(angle_error) <= self.heading_tolerance:
            command.linear.x = min(self.max_linear, self.k_linear * distance)

        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = KochController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
