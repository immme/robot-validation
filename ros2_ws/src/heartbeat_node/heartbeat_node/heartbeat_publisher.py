import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32

# REQ-COM-003: heartbeat를 0.5초(2Hz)마다 보낸다.
HEARTBEAT_PERIOD = 0.5  # 초
HEARTBEAT_TOPIC = "/heartbeat"


class HeartbeatPublisher(Node):
    # 테스트 대상: heartbeat를 일정한 주기로 /heartbeat 토픽에 보내는 노드.
    # 받는 쪽이 누구인지 모르고 판정도 하지 않는다. 보내기만 한다.
    def __init__(self):
        super().__init__("heartbeat_publisher")
        # 보내는 통로를 만든다(메시지 타입 Int32, 토픽 이름, 큐 크기 10).
        # 실제로 보내는 줄은 send_heartbeat 안의 publish다.
        self.heartbeat_pub = self.create_publisher(Int32, HEARTBEAT_TOPIC, 10)
        # 0.5초마다 send_heartbeat를 불러 달라고 신청만 한다.
        # 실제로 부르는 것은 main의 rclpy.spin이다.
        self.timer = self.create_timer(HEARTBEAT_PERIOD, self.send_heartbeat)
        self.count = 0  # 보낼 때마다 1씩 늘어나는 번호(0부터 시작)
        self.get_logger().info(f"heartbeat_publisher started: {HEARTBEAT_TOPIC} every {HEARTBEAT_PERIOD} s")

    def send_heartbeat(self):
        # 타이머가 부를 때마다 번호 하나를 /heartbeat로 보내고, 다음 번호로 넘어간다.
        msg = Int32()
        msg.data = self.count
        self.heartbeat_pub.publish(msg)
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = HeartbeatPublisher()
    try:
        # spin이 타이머 콜백을 시간이 될 때마다 불러 준다. 이 줄이 없으면 프로그램이 바로 끝난다.
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass  # Ctrl+C나 종료 신호로 끝내는 것은 정상 종료다.
    finally:
        # 끝날 때 노드와 rclpy를 정리한다.
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
