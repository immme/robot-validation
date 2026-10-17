from datetime import datetime
from pathlib import Path

import result_log

# pytest가 정해진 시점에 부르는 함수(hook)로 테스트 결과를 모아 결과 파일을 만든다.
# 이 파일은 언제 기록할지만 정하고, 파일에 무엇을 어떻게 적을지는 result_log.py가 맡는다.
# 그리고 ROS2가 있어야 도는 테스트(tests/ros2)를 언제 모을지도 정한다.

# ROS2가 켜진 Ubuntu에서만 도는 테스트가 있는 폴더
ROS2_TESTS_DIR = Path(__file__).parent / "tests" / "ros2"

_started_at = None
_tests = []


def pytest_addoption(parser):
    # 실행할 때 붙이는 옵션을 만든다: python -m pytest --ros2
    parser.addoption(
        "--ros2",
        action="store_true",
        default=False,
        help="ROS2가 필요한 테스트(tests/ros2)도 함께 실행한다(ROS2가 켜진 Ubuntu에서만)",
    )


def pytest_ignore_collect(collection_path, config):
    # 테스트를 모으는 중에 파일·폴더마다 불린다. True를 돌려주면 그 경로는 모으지 않는다.
    # --ros2가 없으면 tests/ros2는 아예 모으지 않는다: Windows와 CI에는 ROS2(rclpy)가 없어
    # 모으다가 오류가 나거나 건너뛰기(SKIP)로 표시되기 때문이다.
    if not config.getoption("ros2") and collection_path.is_relative_to(ROS2_TESTS_DIR):
        return True
    return None


def pytest_sessionstart(session):
    # 테스트 실행이 시작될 때: 시작 시각을 기록하고 결과 목록을 비운다
    global _started_at
    _started_at = datetime.now().astimezone()
    _tests.clear()


def pytest_runtest_logreport(report):
    # 테스트마다 준비(setup)·실행(call)·정리(teardown) 단계가 끝날 때 불린다.
    # 실행 단계 결과는 모두 기록하고, 준비·정리 단계는 실패하거나 건너뛴 경우만 기록한다
    if report.when == "call" or not report.passed:
        _tests.append(
            {
                "test": report.nodeid,
                "result": {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}[report.outcome],
                "reason": _reason(report),
            }
        )


def _reason(report):
    # 실패하거나 건너뛴 이유 한 줄(예: AssertionError: assert 'COMM_LOST' == 'NORMAL'). 통과하면 None
    if report.passed:
        return None
    if report.skipped:
        return report.longrepr[2]  # 건너뛴 이유
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash is not None:
        return crash.message.split("\n")[0]
    return str(report.longrepr)


def pytest_sessionfinish(session, exitstatus):
    # 테스트 실행이 끝났을 때: 결과 파일을 만든다
    commit, uncommitted_changes = result_log.get_git_info()
    record = result_log.build_record(_tests, _started_at, commit, uncommitted_changes)
    path = result_log.write_record(record, _started_at)
    print(f"\n결과 파일: {path}")
