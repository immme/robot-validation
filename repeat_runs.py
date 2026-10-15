import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime

import result_log

# 같은 테스트를 여러 번 실행해 두 가지를 확인한다.
#  ① 실행마다 결과가 달라지는 테스트(불안정한 테스트)가 있는지
#  ② 전부 통과했는지: FAIL뿐 아니라 SKIP(검증을 하지 않음)이나 테스트가 하나도 실행되지 않은 경우도 통과로 보지 않는다
# pytest가 정상적으로 실행되지 못한 반복(수집 오류 등)이 있으면 ERROR로 알린다.
# 사용법: python repeat_runs.py [반복 횟수]   (생략하면 10회)

DEFAULT_REPEATS = 10

VERDICT_TEXT = {
    "STABLE": "매번 같은 결과",
    "UNSTABLE": "실행마다 결과가 다른 테스트가 있음",
    "ERROR": "pytest가 정상적으로 실행되지 못한 반복이 있음",
}

# 정상 범위(0, 1)를 벗어난 pytest 종료코드의 뜻
EXIT_CODE_TEXT = {
    2: "중단 또는 수집 오류",
    3: "pytest 내부 오류",
    4: "pytest 사용법 오류",
    5: "실행된 테스트 없음",
}


def run_pytest_once(results_dir):
    # pytest를 새 프로세스로 한 번 실행하고 종료코드를 돌려준다.
    # 결과 파일은 results_dir에 저장되고 화면 출력은 표시하지 않는다
    env = {**os.environ, "VALIDATION_RESULTS_DIR": str(results_dir)}
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=result_log.PROJECT_DIR,
        env=env,
        capture_output=True,
    )
    return completed.returncode


def load_runs(results_dir):
    # 폴더 안의 결과 파일을 실행 순서(파일 이름의 시각 순서)대로 읽어 실행마다 {테스트 이름: 결과}로 만든다
    runs = []
    for path in sorted(results_dir.glob("[0-9]*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        runs.append({t["test"]: t["result"] for t in record["tests"]})
    return runs


def main():
    try:
        repeats = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REPEATS
    except ValueError:
        repeats = 0
    if repeats < 1:
        print("반복 횟수는 1 이상의 정수로 입력하세요. 예) python repeat_runs.py 10")
        return 2

    started_at = datetime.now().astimezone()
    results_dir = result_log.RESULTS_DIR / ("repeat-" + started_at.strftime("%Y%m%d-%H%M%S"))
    results_dir.mkdir(parents=True)

    exit_codes = []
    for _ in range(repeats):
        exit_codes.append(run_pytest_once(results_dir))

    runs = load_runs(results_dir)
    unstable = result_log.find_unstable(runs)
    bad_exit_codes = result_log.find_bad_exit_codes(exit_codes)
    all_passed = result_log.is_all_passed(runs)

    if len(runs) != repeats or bad_exit_codes:
        # 결과 파일 수가 반복 횟수와 다르거나(pytest가 중간에 비정상 종료한 경우 등),
        # pytest 종료코드가 정상 범위(0, 1)를 벗어났다(수집 오류·실행된 테스트 없음 등)
        verdict = "ERROR"
    elif unstable:
        verdict = "UNSTABLE"
    else:
        verdict = "STABLE"

    summary = {
        "run_at": started_at.isoformat(timespec="seconds"),
        "repeats": repeats,
        "result_files": len(runs),
        "exit_codes": exit_codes,
        "verdict": verdict,
        "all_passed": all_passed,
        "unstable_tests": unstable,
    }
    summary_path = results_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # 판정(STABLE·UNSTABLE·ERROR)과 통과 여부(PASS·FAIL)는 따로 보여 준다: 매번 똑같이 SKIP이면 STABLE이지만 통과가 아니라서 FAIL이다
    pass_text = "PASS" if all_passed else "FAIL"
    counts = Counter(result for run in runs for result in run.values())
    count_text = " · ".join(f"{name} {counts[name]}" for name in ("PASS", "FAIL", "SKIP") if counts[name]) or "테스트 없음"
    print(f"반복 {repeats}회 결과")
    print(f"  판정: {verdict} ({VERDICT_TEXT[verdict]})")
    for name, results in unstable.items():
        print(f"    - 불안정한 테스트: {name} → {', '.join(results)}")
    for number, code in bad_exit_codes.items():
        print(f"    - {number}번째 반복: pytest 종료코드 {code} ({EXIT_CODE_TEXT.get(code, '알 수 없음')})")
    print(f"  통과 여부: {pass_text}")
    print(f"  결과 합계: {count_text}")
    print(f"요약 파일: {summary_path}")
    return 0 if verdict == "STABLE" and all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
