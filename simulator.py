# 가짜 로봇(Simulator): 테스트가 검사할 대상(SUT)
class FakeRobot:
    def __init__(self):
        self.state = "OFF"

    def power_on(self):
        self.state = "NORMAL"

    def power_off(self):
        self.state = "OFF"

    def lose_heartbeat(self):
        if self.state == "NORMAL":
            self.state = "COMM_LOST"
