import time

# REQ-COM-004: 마지막 heartbeat를 받은 뒤 이 시간(초) 이상 받지 못하면 통신 끊김으로 판정한다(3.0초가 되는 순간부터).
HEARTBEAT_TIMEOUT = 3.0


class HeartbeatMonitor:
    # 감시자: 시험 대상이 보내는 heartbeat를 밖에서 지켜보는 시험 도구(시험 대상이 아니다).
    # 대상이 누구인지(가짜 로봇이든 ROS2 노드든) 모르고, "heartbeat가 도착했다"는 사실만 받아 기록한다.
    def __init__(self, clock=time.monotonic):
        # clock: 현재 시각(초)을 돌려주는 함수. 실제 실행에는 진짜 시계(time.monotonic)를,
        # 테스트에는 시간을 직접 조작할 수 있는 가짜 시계를 넣는다.
        self._clock = clock
        self._arrivals = []  # heartbeat가 도착한 시각들(도착한 순서대로)
        self._lost = False

    @property
    def state(self):
        # 상태를 읽을 때마다 timeout이 지났는지 먼저 확인한다
        self._check_timeout()
        if self._lost:
            return "COMM_LOST"
        if not self._arrivals:
            return "WAITING"  # 아직 하나도 못 받아서 판정하지 않는다(이 경우는 요구사항에 없음)
        return "NORMAL"

    @property
    def last_arrival(self):
        # 마지막 heartbeat가 도착한 시각(아직 하나도 못 받았으면 None). 시험이 "마지막 수신 뒤 몇 초"를 잴 때 쓴다.
        return self._arrivals[-1] if self._arrivals else None

    def on_heartbeat(self):
        # heartbeat가 도착할 때마다 부른다. 도착한 시각을 기록한다.
        # 도착하기 전에 이미 timeout이 지났다면 먼저 끊김으로 굳힌다(끊긴 뒤 복구는 아직 요구사항에 없음).
        self._check_timeout()
        self._arrivals.append(self._clock())

    def count_since_first(self, seconds):
        # 첫 heartbeat가 도착한 시각부터 seconds초 동안(끝 시각은 포함하지 않음) 도착한 횟수
        if not self._arrivals:
            return 0
        start = self._arrivals[0]
        return sum(1 for t in self._arrivals if start <= t < start + seconds)

    def _check_timeout(self):
        # 마지막 heartbeat 이후 timeout 이상 지났으면 통신 끊김으로 굳힌다
        if self._arrivals and self._clock() - self._arrivals[-1] >= HEARTBEAT_TIMEOUT:
            self._lost = True
