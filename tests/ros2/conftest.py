import os
import signal
import subprocess
import threading

import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor

from monitor import HeartbeatMonitor
from ros2_listener import HeartbeatListener

# 이 폴더의 시험은 ROS2가 켜진 Ubuntu에서만 돈다(루트 conftest.py가 --ros2 없이는 이 폴더를 모으지 않는다).
# 여기에는 시험 앞뒤의 준비·정리를 fixture로 모아 둔다.
# fixture: 시험 함수가 인자에 이름을 적으면 pytest가 준비해서 넘겨 주고,
# 시험이 끝나면 yield 아래의 정리를 실행한다. 준비·정리를 시험마다 반복해서 쓰지 않으려는 장치다.


@pytest.fixture(scope="session")
def ros_context():
    # ROS2 통신은 먼저 켜야 쓸 수 있다(rclpy.init). 시험 전체에서 한 번 켜고 모두 끝나면 끈다.
    rclpy.init()
    yield
    rclpy.try_shutdown()


@pytest.fixture
def monitor():
    # 감시자: 진짜 시계(time.monotonic)로 heartbeat가 도착한 시각을 기록한다. 시험마다 새로 만든다.
    return HeartbeatMonitor()


@pytest.fixture
def listener(ros_context, monitor):
    # /heartbeat를 듣고 도착할 때마다 감시자에게 알리는 노드를 만들어 돌린다.
    node = HeartbeatListener(monitor)
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    # spin은 끝나지 않고 콜백을 계속 불러 준다. 시험 코드(기다리기·assert)와 동시에 돌려야 해서 다른 스레드에서 돌린다.
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    yield node
    executor.shutdown()  # spin을 멈춘다
    thread.join(timeout=5.0)
    node.destroy_node()


@pytest.fixture
def publisher():
    # 시험 대상: 진짜 heartbeat_publisher 노드를 따로 띄운다. (ros2 run은 노드를 자식 프로세스로 다시 띄우므로,
    # 둘을 한꺼번에 끝낼 수 있게 새 프로세스 그룹으로 시작한다.)
    # 이 터미널에서 ROS2와 이 저장소의 ros2_ws를 source한 상태여야 `ros2 run`이 노드를 찾는다.
    process = subprocess.Popen(
        ["ros2", "run", "heartbeat_node", "heartbeat_publisher"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    yield process
    _stop(process)


def _stop(process):
    # 노드를 끝낸다: 먼저 정상 종료(Ctrl+C와 같은 신호)를 요청하고, 안 끝나면 강제로 끝낸다.
    try:
        os.killpg(process.pid, signal.SIGINT)
        process.wait(timeout=5.0)
    except ProcessLookupError:
        pass  # 이미 끝나 있다
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
