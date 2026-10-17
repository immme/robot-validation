from monitor import HeartbeatMonitor


class FakeClock:
    # 테스트가 직접 조작하는 가짜 시계: 실제로 기다리지 않고 시간을 앞으로 보낸다
    def __init__(self):
        self._seconds = 0.0

    def now(self):
        return self._seconds

    def advance(self, seconds):
        self._seconds += seconds


def test_monitor_normal_just_before_limit():
    # TC-COM-006 Monitor Timeout (REQ-COM-004) · 직전: 3초가 되기 전
    clock = FakeClock()
    monitor = HeartbeatMonitor(clock=clock.now)
    monitor.on_heartbeat()  # 준비: 시각 0초에 heartbeat를 마지막으로 받는다
    clock.advance(2.9)  # 행동: heartbeat 없이 2.9초가 지난다
    assert monitor.state == "NORMAL"  # 기대: 아직 정상


def test_monitor_comm_lost_exactly_at_limit():
    # TC-COM-006 Monitor Timeout (REQ-COM-004) · 경계: 딱 3초
    clock = FakeClock()
    monitor = HeartbeatMonitor(clock=clock.now)
    monitor.on_heartbeat()  # 준비: 시각 0초에 heartbeat를 마지막으로 받는다
    clock.advance(3.0)  # 행동: heartbeat 없이 딱 3.0초가 지난다
    assert monitor.state == "COMM_LOST"  # 기대: 3초가 되는 순간부터 통신 끊김


def test_monitor_comm_lost_just_after_limit():
    # TC-COM-006 Monitor Timeout (REQ-COM-004) · 초과: 3초를 넘김
    clock = FakeClock()
    monitor = HeartbeatMonitor(clock=clock.now)
    monitor.on_heartbeat()  # 준비: 시각 0초에 heartbeat를 마지막으로 받는다
    clock.advance(3.1)  # 행동: heartbeat 없이 3.1초가 지난다
    assert monitor.state == "COMM_LOST"  # 기대: 통신 끊김


def test_monitor_heartbeat_resets_timeout():
    # TC-COM-006 Monitor Timeout (REQ-COM-004) · 새 heartbeat가 오면 3초를 마지막 수신부터 다시 센다
    clock = FakeClock()
    monitor = HeartbeatMonitor(clock=clock.now)
    monitor.on_heartbeat()  # 준비: 시각 0초에 heartbeat를 받는다
    clock.advance(2.0)
    monitor.on_heartbeat()  # 준비: 시각 2초에 heartbeat를 다시 받는다
    clock.advance(2.9)  # 행동: 그 뒤로 2.9초가 더 지난다(처음부터 세면 4.9초)
    assert monitor.state == "NORMAL"  # 기대: 마지막 수신부터 2.9초라서 아직 정상


def test_count_since_first_heartbeat():
    # 감시자 자체 테스트(횟수 세기): 0.5초마다 heartbeat가 오면 첫 도착부터 5초 동안 10번 센다
    clock = FakeClock()
    monitor = HeartbeatMonitor(clock=clock.now)
    monitor.on_heartbeat()  # 준비: 시각 0.0초에 첫 heartbeat
    for _ in range(10):
        clock.advance(0.5)
        monitor.on_heartbeat()  # 준비: 0.5, 1.0, ... 5.0초에 heartbeat
    assert monitor.count_since_first(5.0) == 10  # 기대: 0.0~4.5초에 도착한 10번(5.0초에 온 것은 포함하지 않음)


def test_count_is_zero_before_first_heartbeat():
    # 감시자 자체 테스트(횟수 세기): heartbeat를 하나도 못 받았으면 0번
    monitor = HeartbeatMonitor(clock=FakeClock().now)
    assert monitor.count_since_first(5.0) == 0


def test_last_arrival_is_none_before_first_heartbeat():
    # 감시자 자체 테스트(마지막 수신 시각): heartbeat를 하나도 못 받았으면 None
    monitor = HeartbeatMonitor(clock=FakeClock().now)
    assert monitor.last_arrival is None


def test_last_arrival_is_latest_heartbeat_time():
    # 감시자 자체 테스트(마지막 수신 시각): 가장 마지막에 도착한 시각을 돌려준다
    clock = FakeClock()
    monitor = HeartbeatMonitor(clock=clock.now)
    monitor.on_heartbeat()  # 준비: 시각 0.0초에 heartbeat
    clock.advance(1.5)
    monitor.on_heartbeat()  # 준비: 시각 1.5초에 heartbeat
    clock.advance(1.0)  # 행동: 그 뒤 1.0초가 더 지나도(2.5초) 마지막 수신 시각은 그대로
    assert monitor.last_arrival == 1.5  # 기대: 마지막으로 도착한 1.5초
