import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


FUNCTION_RE = re.compile(r"^(.*?) \((.*\.py):(\d+)\)$")


def parse_function(event):
    """
    VizTracer function names look roughly like:

        assistant_message (/path/to/app/api/routes.py:87)
    """
    name = event.get("name", "")
    match = FUNCTION_RE.match(name)

    if not match:
        return None

    function_name, filename, line = match.groups()

    return {
        "function": function_name,
        "filename": Path(filename),
        "line": int(line),
    }


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def relative_name(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def main():
    parser = argparse.ArgumentParser(
        description="Print application function calls from a VizTracer trace."
    )

    parser.add_argument("trace_file")

    parser.add_argument(
        "--app-root",
        default="app",
        help="Only show Python calls inside this directory.",
    )

    parser.add_argument(
        "--contains",
        help="Only show functions/paths containing this text.",
    )

    args = parser.parse_args()

    trace_path = Path(args.trace_file)
    repo_root = Path.cwd()
    app_root = (repo_root / args.app_root).resolve()

    with trace_path.open() as f:
        trace = json.load(f)

    events_by_thread = defaultdict(list)

    for event in trace.get("traceEvents", []):

        # "X" = complete duration event, which is what VizTracer uses
        # for ordinary Python function executions.
        if event.get("ph") != "X":
            continue

        parsed = parse_function(event)

        if not parsed:
            continue

        filename = parsed["filename"]

        if not is_inside(filename, app_root):
            continue

        parsed.update(
            {
                "ts": event.get("ts", 0),
                "duration": event.get("dur", 0),
                "pid": event.get("pid"),
                "tid": event.get("tid"),
            }
        )

        if args.contains:
            searchable = (
                parsed["function"] + " " + str(parsed["filename"])
            ).lower()

            if args.contains.lower() not in searchable:
                continue

        events_by_thread[(parsed["pid"], parsed["tid"])].append(parsed)

    if not events_by_thread:
        print("No application functions found.")
        return

    for (pid, tid), events in events_by_thread.items():

        events.sort(
            key=lambda event: (
                event["ts"],
                -event["duration"],
            )
        )

        print()
        print("=" * 80)
        print(f"PROCESS {pid} / THREAD {tid}")
        print("=" * 80)

        stack = []

        for event in events:

            start = event["ts"]
            end = start + event["duration"]

            # Remove functions that have already finished
            while stack and start >= stack[-1]["end"]:
                stack.pop()

            # Handle overlapping async/thread events that are not
            # actually parent-child calls.
            while stack and end > stack[-1]["end"]:
                stack.pop()

            indent = "    " * len(stack)

            location = relative_name(
                event["filename"],
                repo_root,
            )

            duration_ms = event["duration"] / 1000

            print(
                f"{indent}→ {event['function']}"
                f"  [{location}:{event['line']}]"
                f"  ({duration_ms:.3f} ms)"
            )

            stack.append(
                {
                    "end": end,
                }
            )


if __name__ == "__main__":
    main()