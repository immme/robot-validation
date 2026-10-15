from result_log import find_bad_exit_codes, find_unstable, is_all_passed

# 반복 실행 결과를 판정하는 함수(find_unstable · is_all_passed · find_bad_exit_codes)를 확인한다.
# pytest를 여러 번 실행하지 않고 실행별 결과와 종료코드를 직접 만들어 넣는다.


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


def test_all_pass_is_passed():
    # 준비: 세 번 모두 통과
    runs = [{"t1": "PASS", "t2": "PASS"}] * 3

    # 행동
    passed = is_all_passed(runs)

    # 기대: 통과
    assert passed is True


def test_fail_is_not_passed():
    # 준비: 두 번째 실행에서 t2가 실패
    runs = [{"t1": "PASS", "t2": "PASS"}, {"t1": "PASS", "t2": "FAIL"}]

    # 행동
    passed = is_all_passed(runs)

    # 기대: 통과가 아니다
    assert passed is False


def test_skip_is_not_passed():
    # 준비: 세 번 모두 t2가 건너뛰어졌다(검증을 하지 않았다)
    runs = [{"t1": "PASS", "t2": "SKIP"}] * 3

    # 행동
    passed = is_all_passed(runs)

    # 기대: SKIP이 하나라도 있으면 통과가 아니다
    assert passed is False


def test_runs_without_any_test_are_not_passed():
    # 준비: 세 번 모두 결과가 비어 있다(테스트 수집 실패나 테스트 없음)
    runs = [{}] * 3

    # 행동
    passed = is_all_passed(runs)

    # 기대: 통과가 아니다
    assert passed is False


def test_no_runs_is_not_passed():
    # 준비: 실행 결과가 하나도 없다
    runs = []

    # 행동
    passed = is_all_passed(runs)

    # 기대: 통과가 아니다
    assert passed is False


def test_exit_codes_other_than_0_and_1_are_bad():
    # 준비: 0(실패 없음)과 1(실패 있음)은 정상, 세 번째는 수집 오류(2), 네 번째는 실행된 테스트 없음(5)
    exit_codes = [0, 1, 2, 5]

    # 행동
    bad = find_bad_exit_codes(exit_codes)

    # 기대: 0·1은 빼고, 비정상 실행만 {실행 번호: 종료코드}로 나온다
    assert bad == {3: 2, 4: 5}
