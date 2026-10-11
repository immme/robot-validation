from simulator import FakeRobot


class FakeClock:
    # 테스트가 직접 조작하는 가짜 시계: 실제로 기다리지 않고 시간을 앞으로 보낸다
    def __init__(self):
        self._seconds = 0.0

    def now(self):
        return self._seconds

    def advance(self, seconds):
        self._seconds += seconds


def test_heartbeat_loss():
    # TC-COM-001 Heartbeat Loss (REQ-COM-001)
    robot = FakeRobot()
    robot.power_on()  # 준비: 켜져 있는 정상 로봇(NORMAL)
    robot.lose_heartbeat()  # 행동: heartbeat가 끊긴다
    assert robot.state == "COMM_LOST"  # 기대: 상태가 통신 끊김


def test_no_timeout_just_before_limit():
    # TC-COM-002 Communication Timeout (REQ-COM-002) · 직전: 3초가 되기 전
    clock = FakeClock()
    robot = FakeRobot(clock=clock.now)
    robot.power_on()  # 준비: 켜져 있는 정상 로봇(NORMAL)
    robot.receive_heartbeat()  # 준비: 시각 0초에 heartbeat를 마지막으로 받는다
    clock.advance(2.9)  # 행동: heartbeat 없이 2.9초가 지난다
    assert robot.state == "NORMAL"  # 기대: 아직 정상


def test_timeout_exactly_at_limit():
    # TC-COM-002 Communication Timeout (REQ-COM-002) · 경계: 딱 3초
    clock = FakeClock()
    robot = FakeRobot(clock=clock.now)
    robot.power_on()  # 준비: 켜져 있는 정상 로봇(NORMAL)
    robot.receive_heartbeat()  # 준비: 시각 0초에 heartbeat를 마지막으로 받는다
    clock.advance(3.0)  # 행동: heartbeat 없이 딱 3.0초가 지난다
    assert robot.state == "COMM_LOST"  # 기대: 3초가 되는 순간부터 통신 끊김


def test_timeout_just_after_limit():
    # TC-COM-002 Communication Timeout (REQ-COM-002) · 초과: 3초를 넘김
    clock = FakeClock()
    robot = FakeRobot(clock=clock.now)
    robot.power_on()  # 준비: 켜져 있는 정상 로봇(NORMAL)
    robot.receive_heartbeat()  # 준비: 시각 0초에 heartbeat를 마지막으로 받는다
    clock.advance(3.1)  # 행동: heartbeat 없이 3.1초가 지난다
    assert robot.state == "COMM_LOST"  # 기대: 통신 끊김


def test_heartbeat_resets_timeout():
    # TC-COM-003 Heartbeat Resets Timeout (REQ-COM-002) · 새 heartbeat가 오면 3초를 마지막 수신부터 다시 센다
    clock = FakeClock()
    robot = FakeRobot(clock=clock.now)
    robot.power_on()  # 준비: 켜져 있는 정상 로봇(NORMAL)
    robot.receive_heartbeat()  # 준비: 시각 0초에 heartbeat를 받는다
    clock.advance(2.0)  # 준비: 2초가 지난다
    robot.receive_heartbeat()  # 준비: 시각 2초에 heartbeat를 또 받는다
    clock.advance(2.9)  # 행동: 그 뒤 heartbeat 없이 2.9초가 더 지난다(첫 수신부터는 4.9초)
    assert robot.state == "NORMAL"  # 기대: 마지막 수신(2초)부터 2.9초라서 아직 정상
