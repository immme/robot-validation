from simulator import FakeRobot


def test_heartbeat_loss():
    # TC-COM-001 Heartbeat Loss (REQ-COM-001)
    robot = FakeRobot()
    robot.power_on()  # 준비: 켜져 있는 정상 로봇(NORMAL)
    robot.lose_heartbeat()  # 행동: heartbeat가 끊긴다
    assert robot.state == "COMM_LOST"  # 기대: 상태가 통신 끊김
