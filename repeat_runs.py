import json
import os
import subprocess
import sys
from datetime import datetime

import result_log

# 같은 테스트를 여러 번 실행해, 실행마다 결과가 달라지는 테스트(불안정한 테스트)가 있는지 확인한다.
# 사용법: python repeat_runs.py [반복 횟수]   (생략하면 10회)

DEFAULT_REPEATS = 10

VERDICT_TEXT = {
    "STABLE": "매번 같은 결과",
    "UNSTABLE": "실행마다 결과가 다른 테스트가 있음",
    "ERROR": "결과 파일 수가 반복 횟수와 다름",
}


def run_pytest_once(results_dir):
    # pytest를 새 프로세스로 한 번 실행한다. 결과 파일은 results_dir에 저장되고 화면 출력은 표시하지 않는다
    env = {**os.environ, "VALIDATION_RESULTS_DIR": str(results_dir)}
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=result_log.PROJECT_DIR,
        env=env,
        capture_output=True,
    )


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

    for _ in range(repeats):
        run_pytest_once(results_dir)

    runs = load_runs(results_dir)
    unstable = result_log.find_unstable(runs)
    all_passed = all("FAIL" not in run.values() for run in runs)

    if len(runs) != repeats:
        verdict = "ERROR"  # 결과 파일 수가 반복 횟수와 다르다(pytest가 중간에 비정상 종료한 경우 등)
    elif unstable:
        verdict = "UNSTABLE"
    else:
        verdict = "STABLE"

    summary = {
        "run_at": started_at.isoformat(timespec="seconds"),
        "repeats": repeats,
        "result_files": len(runs),
        "verdict": verdict,
        "all_passed": all_passed,
        "unstable_tests": unstable,
    }
    summary_path = results_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    failure_text = "실패 없음" if all_passed else "실패 있음"
    print(f"반복 {repeats}회 결과: {verdict}({VERDICT_TEXT[verdict]}) · {failure_text}")
    for name, results in unstable.items():
        print(f"  불안정한 테스트: {name} → {', '.join(results)}")
    print(f"요약 파일: {summary_path}")
    return 0 if verdict == "STABLE" and all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
