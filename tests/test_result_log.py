from result_log import find_unstable

# 반복 실행에서 "실행마다 결과가 다른 테스트"를 찾아내는 함수 확인.
# pytest를 여러 번 돌리지 않고, 실행별 결과를 직접 만들어 넣는다.


def test_same_result_every_run_is_stable():
    # 준비: 3번 모두 똑같이 통과
    runs = [{"t1": "PASS", "t2": "PASS"}] * 3

    # 행동
    unstable = find_unstable(runs)

    # 기대: 불안정한 테스트 없음
    assert unstable == {}


def test_test_that_changes_result_is_unstable():
    # 준비: t1이 세 번째 실행에서만 실패
    runs = [
        {"t1": "PASS", "t2": "PASS"},
        {"t1": "PASS", "t2": "PASS"},
        {"t1": "FAIL", "t2": "PASS"},
    ]

    # 행동
    unstable = find_unstable(runs)

    # 기대: t1만 불안정하고, 실행별 결과가 그대로 보인다
    assert unstable == {"t1": ["PASS", "PASS", "FAIL"]}


def test_always_failing_test_is_not_unstable():
    # 준비: 3번 모두 똑같이 실패 (고장이지만 결과는 일관됨)
    runs = [{"t1": "FAIL"}] * 3

    # 행동
    unstable = find_unstable(runs)

    # 기대: 불안정으로 보지 않는다
    assert unstable == {}


def test_test_missing_in_one_run_is_unstable():
    # 준비: 두 번째 실행에는 t1 결과가 없다
    runs = [{"t1": "PASS"}, {}, {"t1": "PASS"}]

    # 행동
    unstable = find_unstable(runs)

    # 기대: 없던 실행은 MISSING으로 보여 주고 불안정으로 본다
    assert unstable == {"t1": ["PASS", "MISSING", "PASS"]}
