# 가짜 로봇(Simulator): 테스트가 검사할 대상(SUT)
class FakeRobot:
    def __init__(self):
        self.state = "OFF"

    def power_on(self):
        self.state = "NORMAL"
