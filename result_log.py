import json
import os
import subprocess
from collections import Counter
from pathlib import Path

# 테스트 결과 파일(JSON)을 만들고, 반복 실행 결과에서 불안정한 테스트를 찾는다.
# pytest와의 연결은 conftest.py가 맡는다.

PROJECT_DIR = Path(__file__).parent
RESULTS_DIR = PROJECT_DIR / "results"


def _git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout.strip()


def get_git_info():
    # 어느 코드로 실행했는지: 현재 commit 해시와 commit하지 않은 변경이 있는지
    # git을 쓸 수 없는 환경이면 (None, None)을 돌려준다
    try:
        commit = _git("rev-parse", "--short", "HEAD")
        uncommitted_changes = _git("status", "--porcelain") != ""
    except (OSError, subprocess.CalledProcessError):
        return None, None
    return commit, uncommitted_changes


def build_record(tests, started_at, commit, uncommitted_changes):
    # tests: 테스트마다 {"test": 이름, "result": "PASS"/"FAIL"/"SKIP", "reason": 실패 이유(없으면 None)}
    counts = Counter(t["result"] for t in tests)
    return {
        "run_at": started_at.isoformat(timespec="seconds"),  # 실행 시각(시간대 포함)
        "commit": commit,  # 실행한 코드의 commit
        "uncommitted_changes": uncommitted_changes,  # commit하지 않은 변경이 있었는지
        "summary": {
            "total": len(tests),
            "passed": counts["PASS"],
            "failed": counts["FAIL"],
            "skipped": counts["SKIP"],
        },
        "tests": tests,
    }


def get_results_dir():
    # 결과 파일을 저장할 폴더. 환경 변수 VALIDATION_RESULTS_DIR가 있으면 그 폴더, 없으면 results/를 쓴다.
    # repeat_runs.py가 한 번의 반복에서 나온 파일을 한 폴더에 모을 때 이 환경 변수를 쓴다
    return Path(os.environ.get("VALIDATION_RESULTS_DIR", RESULTS_DIR))


def write_record(record, started_at, results_dir=None):
    results_dir = results_dir or get_results_dir()
    results_dir.mkdir(parents=True, exist_ok=True)
    # 파일 이름은 실행 시각이다. 반복 실행은 1초 안에 여러 번 끝날 수 있어서 마이크로초(%f)까지 넣는다
    path = results_dir / (started_at.strftime("%Y%m%d-%H%M%S-%f") + ".json")
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def find_unstable(runs):
    # runs: 실행마다 {테스트 이름: 결과}를 모은 목록. 예) [{"t1": "PASS"}, {"t1": "FAIL"}]
    # 실행마다 결과가 하나라도 다른 테스트를 {이름: [실행별 결과]}로 돌려준다(없으면 빈 dict).
    # 어떤 실행에 그 테스트 결과가 없으면 "MISSING"으로 기록한다.
    # 매번 FAIL인 테스트는 결과가 일관되므로 불안정으로 보지 않는다(결함이지만 흔들림은 아니다).
    names = sorted({name for run in runs for name in run})
    unstable = {}
    for name in names:
        results = [run.get(name, "MISSING") for run in runs]
        if len(set(results)) > 1:
            unstable[name] = results
    return unstable
