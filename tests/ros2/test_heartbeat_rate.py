import time

from helpers import wait_until

# TC-COM-004 Heartbeat Rate (REQ-COM-003): heartbeat 노드는 0.5초마다 heartbeat를 보낸다.
# 기대값은 요구사항에서 정한다(노드 코드에서 가져오지 않는다): 5초 ÷ 0.5초 = 10번이고, ±1은 정상이라 9~11번.
OBSERVE_SECONDS = 5.0  # 첫 heartbeat를 받은 뒤 이 시간 동안 받은 횟수를 센다
MIN_COUNT = 9
MAX_COUNT = 11
FIRST_HEARTBEAT_TIMEOUT = 10.0  # 노드가 뜨고 서로 찾을 때까지 기다리는 최대 시간(초)


def test_heartbeat_rate(listener, publisher, monitor):
    # 준비: 노드가 떠서 첫 heartbeat가 도착할 때까지 기다린다(세는 것은 첫 도착부터다)
    first_received = wait_until(lambda: monitor.state != "WAITING", FIRST_HEARTBEAT_TIMEOUT)
    assert first_received, f"{FIRST_HEARTBEAT_TIMEOUT}초 안에 첫 heartbeat를 받지 못했다 (노드 종료 코드: {publisher.poll()})"
    # 행동: 첫 도착부터 5초가 지나길 기다린다(0.5초는 5초 끝 무렵에 도착한 것이 기록될 여유)
    time.sleep(OBSERVE_SECONDS + 0.5)
    # 기대: 그 5초 동안 받은 횟수가 9~11번
    assert MIN_COUNT <= monitor.count_since_first(OBSERVE_SECONDS) <= MAX_COUNT
