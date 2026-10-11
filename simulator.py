import time

# 가짜 로봇(Simulator): 테스트가 검사할 대상(SUT)

# REQ-COM-002: 마지막 heartbeat 이후 이 시간(초) 이상 지나면 통신 끊김. 이 시간이 되는 순간부터 끊김이다.
HEARTBEAT_TIMEOUT = 3.0


class FakeRobot:
    def __init__(self, clock=time.monotonic):
        # clock: "지금 몇 초인지"를 알려 주는 함수. 실제 실행은 진짜 시계(time.monotonic),
        # 테스트는 직접 조작하는 가짜 시계를 넣는다.
        self._clock = clock
        self._state = "OFF"
        self._last_heartbeat = None

    @property
    def state(self):
        # 상태를 물을 때 timeout이 지났는지 먼저 확인한다(로봇의 감시 타이머를 흉내 냄)
        self._check_timeout()
        return self._state

    def power_on(self):
        self._state = "NORMAL"
        self._last_heartbeat = self._clock()  # 전원을 켠 시각부터 센다(heartbeat 이력이 없을 때의 기준)

    def power_off(self):
        self._state = "OFF"

    def receive_heartbeat(self):
        # heartbeat를 받으면 받은 시각을 적어 둔다. 이미 끊긴 통신의 복구는 아직 정하지 않았다.
        self._check_timeout()
        if self._state == "NORMAL":
            self._last_heartbeat = self._clock()

    def lose_heartbeat(self):
        self._check_timeout()
        if self._state == "NORMAL":
            self._state = "COMM_LOST"

    def _check_timeout(self):
        # 켜져 있는데 마지막 heartbeat 이후 timeout을 넘겼으면 통신 끊김으로 바꾼다
        if self._state == "NORMAL" and self._clock() - self._last_heartbeat >= HEARTBEAT_TIMEOUT:
            self._state = "COMM_LOST"
