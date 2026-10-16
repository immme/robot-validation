import time

# tests/ros2 안의 시험들이 함께 쓰는 기다리기 도구


def wait_until(condition, timeout):
    # condition이 참이 될 때까지 최대 timeout초 기다린다. 참이 되면 True, 시간이 다 되면 False
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return False


def sleep_until(target_time):
    # 진짜 시계(time.monotonic)가 target_time이 될 때까지 기다린다. 이미 지났으면 바로 돌아온다.
    time.sleep(max(0.0, target_time - time.monotonic()))
