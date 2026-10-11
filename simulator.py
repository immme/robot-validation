import time

# 가짜 로봇(Simulator): 테스트가 검사할 대상(SUT)

# REQ-COM-002: 마지막 heartbeat를 받은 뒤 이 시간(초) 이상 받지 못하면 통신 끊김으로 본다(3.0초가 되는 순간부터).
HEARTBEAT_TIMEOUT = 3.0


class FakeRobot:
    def __init__(self, clock=time.monotonic):
        # clock: 현재 시각(초)을 돌려주는 함수. 실제 실행에는 진짜 시계(time.monotonic)를,
        # 테스트에는 시간을 직접 조작할 수 있는 가짜 시계를 넣는다.
        self._clock = clock
        self._state = "OFF"
        self._last_heartbeat = None

    @property
    def state(self):
        # 상태를 읽을 때마다 timeout이 지났는지 먼저 확인한다(로봇의 통신 감시 타이머 역할)
        self._check_timeout()
        return self._state

    def power_on(self):
        self._state = "NORMAL"
        self._last_heartbeat = self._clock()  # heartbeat를 아직 받지 않았으면 전원을 켠 시각부터 센다

    def power_off(self):
        self._state = "OFF"

    def receive_heartbeat(self):
        # heartbeat를 받으면 받은 시각을 기록한다.
        # 통신이 이미 끊긴 뒤에는 heartbeat가 와도 복구하지 않는다(복구 조건은 아직 요구사항에 없음).
        self._check_timeout()
        if self._state == "NORMAL":
            self._last_heartbeat = self._clock()

    def lose_heartbeat(self):
        # heartbeat가 끊겼다는 신호를 직접 받는다(TC-COM-001에서 사용)
        self._check_timeout()
        if self._state == "NORMAL":
            self._state = "COMM_LOST"

    def _check_timeout(self):
        # 켜져 있고 마지막 heartbeat 이후 timeout 이상 지났으면 통신 끊김으로 바꾼다
        if self._state == "NORMAL" and self._clock() - self._last_heartbeat >= HEARTBEAT_TIMEOUT:
            self._state = "COMM_LOST"
