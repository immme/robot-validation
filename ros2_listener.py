from rclpy.node import Node
from std_msgs.msg import Int32

# 보내는 노드(heartbeat_publisher)와 이름·타입이 같아야 연결된다.
HEARTBEAT_TOPIC = "/heartbeat"


class HeartbeatListener(Node):
    # 테스트 도구: /heartbeat를 지켜보다가 메시지가 도착하면 감시자(monitor)에게 "도착했다"고만 알린다.
    # 테스트 대상(heartbeat_publisher)을 불러오지 않는다. 토픽 이름과 메시지 타입만 맞으면 누가 보내든 같다.
    def __init__(self, monitor):
        super().__init__("heartbeat_listener")
        self.monitor = monitor  # 도착을 기록하고 판정하는 감시자(monitor.py)
        # 받는 통로를 만든다(메시지 타입, 토픽 이름, 콜백, 큐 크기 10).
        # 메시지가 올 때 on_message를 불러 달라고 신청만 한다. 실제로 부르는 것은 rclpy의 spin이다.
        self.subscription = self.create_subscription(Int32, HEARTBEAT_TOPIC, self.on_message, 10)

    def on_message(self, msg):
        # 메시지가 한 개 도착할 때마다 spin이 부른다. msg는 도착한 메시지이고 번호는 msg.data에 있다.
        # 여기서는 번호를 쓰지 않고 "도착했다"는 사실만 감시자에게 넘긴다.
        self.monitor.on_heartbeat()
