import json
import os
import subprocess
import sys
from datetime import datetime

import result_log

# 같은 테스트를 여러 번 돌려서, 실행마다 결과가 다른 테스트(불안정한 테스트)가 있는지 확인한다.
# 사용법: python repeat_runs.py [반복 횟수]   (횟수를 안 쓰면 10번)

DEFAULT_REPEATS = 10


def run_pytest_once(results_dir):
    # pytest를 새 프로세스로 한 번 돌린다. 결과 파일은 results_dir에 만들어진다(화면 출력은 숨긴다)
    env = {**os.environ, "VALIDATION_RESULTS_DIR": str(results_dir)}
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=result_log.PROJECT_DIR,
        env=env,
        capture_output=True,
    )


def load_runs(results_dir):
    # 폴더 안의 결과 파일을 실행 순서(파일 이름의 시각 순서)대로 읽어, 실행마다 {테스트 이름: 결과}로 만든다
    runs = []
    for path in sorted(results_dir.glob("[0-9]*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        runs.append({t["test"]: t["result"] for t in record["tests"]})
    return runs


def main():
    repeats = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REPEATS
    started_at = datetime.now().astimezone()
    results_dir = result_log.RESULTS_DIR / ("repeat-" + started_at.strftime("%Y%m%d-%H%M%S"))
    results_dir.mkdir(parents=True)

    for _ in range(repeats):
        run_pytest_once(results_dir)

    runs = load_runs(results_dir)
    unstable = result_log.find_unstable(runs)
    all_passed = all("FAIL" not in run.values() for run in runs)

    if len(runs) != repeats:
        verdict = "ERROR"  # 결과 파일 수가 반복 횟수와 다르다(pytest가 중간에 죽은 경우 등)
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

    print(f"{repeats}번 반복 실행 → {verdict} · 매번 전부 통과: {all_passed}")
    for name, results in unstable.items():
        print(f"  불안정: {name} → {', '.join(results)}")
    print(f"요약 파일: {summary_path}")
    return 0 if verdict == "STABLE" and all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
