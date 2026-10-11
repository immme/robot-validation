from datetime import datetime

import result_log

# pytest는 정해진 때가 되면 이름이 정해진 함수(pytest_로 시작하는 것들)를 이 파일에서 찾아 불러 준다.
# 내가 pytest를 부르는 게 아니라, pytest가 내 함수를 부르는 구조다.
# 이 파일은 "언제 기록할지"만 맡고, 파일에 적는 일은 result_log.py가 한다.

_started_at = None
_tests = []


def pytest_sessionstart(session):
    # 전체 테스트가 시작될 때: 시작 시각을 적어 두고 목록을 비운다
    global _started_at
    _started_at = datetime.now().astimezone()
    _tests.clear()


def pytest_runtest_logreport(report):
    # 테스트 하나의 단계(준비·실행·정리)가 끝날 때마다.
    # 실행(call) 결과는 모두 적고, 준비·정리 단계는 통과가 아닐 때(실패·건너뜀)만 적는다
    if report.when == "call" or not report.passed:
        _tests.append(
            {
                "test": report.nodeid,
                "result": {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}[report.outcome],
                "reason": _reason(report),
            }
        )


def _reason(report):
    # 실패했을 때 pytest가 보여 주던 한 줄 이유(예: AssertionError: assert 'COMM_LOST' == 'NORMAL'). 통과하면 None
    if report.passed:
        return None
    if report.skipped:
        return report.longrepr[2]  # 건너뛴 이유
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash is not None:
        return crash.message.split("\n")[0]
    return str(report.longrepr)


def pytest_sessionfinish(session, exitstatus):
    # 전체 테스트가 끝났을 때: 결과 파일을 만든다
    commit, uncommitted_changes = result_log.get_git_info()
    record = result_log.build_record(_tests, _started_at, commit, uncommitted_changes)
    path = result_log.write_record(record, _started_at)
    print(f"\n결과 파일: {path}")
