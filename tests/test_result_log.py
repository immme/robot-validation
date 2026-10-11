from result_log import find_unstable

# 반복 실행 결과에서 불안정한 테스트를 찾는 함수(find_unstable)를 확인한다.
# pytest를 여러 번 실행하지 않고 실행별 결과를 직접 만들어 넣는다.


def test_same_result_every_run_is_stable():
    # 준비: 세 번 모두 통과
    runs = [{"t1": "PASS", "t2": "PASS"}] * 3

    # 행동
    unstable = find_unstable(runs)

    # 기대: 불안정한 테스트 없음
    assert unstable == {}


def test_result_changing_between_runs_is_unstable():
    # 준비: t1이 세 번째 실행에서만 실패
    runs = [
        {"t1": "PASS", "t2": "PASS"},
        {"t1": "PASS", "t2": "PASS"},
        {"t1": "FAIL", "t2": "PASS"},
    ]

    # 행동
    unstable = find_unstable(runs)

    # 기대: t1만 불안정으로 나오고, 실행별 결과가 순서대로 담긴다
    assert unstable == {"t1": ["PASS", "PASS", "FAIL"]}


def test_always_failing_test_is_not_unstable():
    # 준비: 세 번 모두 실패(결함이지만 결과는 일관됨)
    runs = [{"t1": "FAIL"}] * 3

    # 행동
    unstable = find_unstable(runs)

    # 기대: 불안정으로 보지 않는다
    assert unstable == {}


def test_missing_result_in_one_run_is_unstable():
    # 준비: 두 번째 실행에는 t1 결과가 없다
    runs = [{"t1": "PASS"}, {}, {"t1": "PASS"}]

    # 행동
    unstable = find_unstable(runs)

    # 기대: 결과가 없는 실행은 MISSING으로 표시하고 불안정으로 본다
    assert unstable == {"t1": ["PASS", "MISSING", "PASS"]}
