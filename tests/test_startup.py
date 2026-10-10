from simulator import FakeRobot


def test_normal_startup():
    # TC-SYS-001 Normal Startup (REQ-SYS-001)
    robot = FakeRobot()  # 준비: 꺼져 있는 로봇
    robot.power_on()  # 행동: 전원을 켠다
    assert robot.state == "NORMAL"  # 기대: 상태가 정상
