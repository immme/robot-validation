import os
import signal
import time

from helpers import sleep_until, wait_until

# TC-COM-005 Node Kill Then Timeout (REQ-COM-004): 실제로 실행하는 heartbeat 노드가 예고 없이 사라지면(kill -9),
# 마지막 heartbeat를 받은 뒤 2.5초 시점은 정상이고 3.5초 시점은 통신 끊김이다.
# 딱 3.0초 경계는 TC-COM-006이 가짜 시계로 확인한다. 기대값은 요구사항에서 정했고 monitor 코드에서 가져오지 않는다.
BEFORE_LIMIT = 2.5  # 마지막 수신 뒤 이 시간(초)에는 아직 정상
AFTER_LIMIT = 3.5  # 마지막 수신 뒤 이 시간(초)에는 통신 끊김
FIRST_HEARTBEAT_TIMEOUT = 10.0  # 노드가 뜨고 서로 찾을 때까지 기다리는 최대 시간(초)
RUNNING_SECONDS = 1.0  # 죽이기 전에 heartbeat를 받으며 정상으로 도는 시간(초)


def test_node_kill_then_timeout(listener, publisher, monitor):
    # 준비: 노드가 떠서 heartbeat가 오기 시작할 때까지 기다리고, 잠시 정상으로 도는 것을 확인한다
    first_received = wait_until(lambda: monitor.state != "WAITING", FIRST_HEARTBEAT_TIMEOUT)
    assert first_received, f"{FIRST_HEARTBEAT_TIMEOUT}초 안에 첫 heartbeat를 받지 못했다 (노드 종료 코드: {publisher.poll()})"
    time.sleep(RUNNING_SECONDS)
    assert monitor.state == "NORMAL"  # 죽이기 전에 정상이어야 끊김으로 바뀌는 것을 구별할 수 있다
    # 행동: 노드를 kill -9로 죽인다(정리할 기회 없이 사라짐). ros2 run이 띄운 자식까지 프로세스 그룹째 죽인다.
    os.killpg(publisher.pid, signal.SIGKILL)
    last_received = monitor.last_arrival  # 마지막 heartbeat가 도착한 시각
    # 기대 1: 마지막 수신 뒤 2.5초에는 아직 정상
    sleep_until(last_received + BEFORE_LIMIT)
    assert monitor.state == "NORMAL"
    # 기대 2: 마지막 수신 뒤 3.5초에는 통신 끊김 (정상을 먼저 읽고 나중에 읽는다: 끊김으로 굳은 뒤에는 정상으로 돌아오지 않는다)
    sleep_until(last_received + AFTER_LIMIT)
    assert monitor.state == "COMM_LOST"
