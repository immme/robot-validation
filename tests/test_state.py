from simulator import FakeRobot


def test_power_on_when_already_on():
    # TC-STATE-001 Power On While Already On (REQ-STATE-001)
    robot = FakeRobot()
    robot.power_on()  # 준비: 이미 켜져 있는 로봇(NORMAL)
    robot.power_on()  # 행동: 전원을 한 번 더 켠다
    assert robot.state == "NORMAL"  # 기대: 상태가 그대로 정상


def test_power_off_when_on():
    # TC-STATE-002 Power Off While On (REQ-STATE-002)
    robot = FakeRobot()
    robot.power_on()  # 준비: 켜져 있는 로봇(NORMAL)
    robot.power_off()  # 행동: 전원을 끈다
    assert robot.state == "OFF"  # 기대: 상태가 꺼짐


def test_power_off_when_already_off():
    # TC-STATE-003 Power Off While Already Off (REQ-STATE-003)
    robot = FakeRobot()  # 준비: 이미 꺼져 있는 로봇(OFF)
    robot.power_off()  # 행동: 전원을 한 번 더 끈다
    assert robot.state == "OFF"  # 기대: 상태가 그대로 꺼짐
