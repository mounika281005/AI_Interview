import argparse
import sqlite3
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def print_table(title: str, headers: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    rows = [list(r) for r in rows]
    print(f"\n=== {title} ===")
    if not rows:
        print("(no rows)")
        return

    widths: List[int] = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(fmt(cell)))

    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * widths[i] for i in range(len(headers)))
    print(header_line)
    print(sep_line)

    for row in rows:
        print(" | ".join(fmt(cell).ljust(widths[i]) for i, cell in enumerate(row)))


def query(conn: sqlite3.Connection, sql: str, params: Tuple = ()) -> list:
    cur = conn.execute(sql, params)
    return cur.fetchall()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print backend interview timing and configuration metrics as tables."
    )
    parser.add_argument(
        "--db",
        default="interview_system.db",
        help="Path to SQLite DB file (default: interview_system.db)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Rows to show for per-session tables (default: 20)",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path.resolve()}")

    conn = sqlite3.connect(str(db_path))
    try:
        # Basic DB info
        tables = query(
            conn,
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
        )
        print_table("Tables", ["name"], tables)

        total_sessions = query(conn, "SELECT COUNT(*) FROM interview_sessions")[0][0]
        print(f"\nTotal interview sessions: {total_sessions}")

        # 1) Config evidence: question count + time limit
        config_rows = query(
            conn,
            """
            SELECT
              id,
              interview_type,
              total_questions,
              time_limit_per_question,
              status,
              created_at
            FROM interview_sessions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (args.limit,),
        )
        print_table(
            "Session Config (Question Count + Time Limit)",
            [
                "id",
                "interview_type",
                "total_questions",
                "time_limit_per_question",
                "status",
                "created_at",
            ],
            config_rows,
        )

        # 2) Per-session timing values
        timing_rows = query(
            conn,
            """
            SELECT
              id,
              interview_type,
              total_questions,
              json_extract(settings, '$.question_generation_ms') AS question_generation_ms,
              json_extract(settings, '$.evaluation_total_ms') AS evaluation_total_ms,
              duration_seconds AS total_interview_seconds,
              created_at
            FROM interview_sessions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (args.limit,),
        )
        print_table(
            "Per-Session Timing Metrics",
            [
                "id",
                "interview_type",
                "total_questions",
                "question_generation_ms",
                "evaluation_total_ms",
                "total_interview_seconds",
                "created_at",
            ],
            timing_rows,
        )

        # 3) Average metrics for review answers
        avg_rows = query(
            conn,
            """
            SELECT
              ROUND(AVG(CAST(json_extract(settings, '$.question_generation_ms') AS REAL)), 2) AS avg_question_generation_ms,
              ROUND(AVG(CAST(json_extract(settings, '$.evaluation_total_ms') AS REAL)), 2) AS avg_evaluation_ms,
              ROUND(AVG(CAST(duration_seconds AS REAL)), 2) AS avg_total_interview_seconds
            FROM interview_sessions
            WHERE status IN ('completed','evaluated')
            """,
        )
        print_table(
            "Average Metrics (Completed/Evaluated Sessions)",
            [
                "avg_question_generation_ms",
                "avg_evaluation_ms",
                "avg_total_interview_seconds",
            ],
            avg_rows,
        )

        # 4) Grouped by question count
        by_q_rows = query(
            conn,
            """
            SELECT
              total_questions AS question_count,
              COUNT(*) AS sessions,
              ROUND(AVG(CAST(json_extract(settings, '$.question_generation_ms') AS REAL)), 2) AS avg_generation_ms,
              ROUND(AVG(CAST(json_extract(settings, '$.evaluation_total_ms') AS REAL)), 2) AS avg_evaluation_ms,
              ROUND(AVG(CAST(duration_seconds AS REAL)), 2) AS avg_total_interview_seconds
            FROM interview_sessions
            WHERE status IN ('completed','evaluated')
            GROUP BY total_questions
            ORDER BY total_questions
            """,
        )
        print_table(
            "Timing by Question Count",
            [
                "question_count",
                "sessions",
                "avg_generation_ms",
                "avg_evaluation_ms",
                "avg_total_interview_seconds",
            ],
            by_q_rows,
        )

        # 5) Min/max question count evidence
        min_max_rows = query(
            conn,
            """
            SELECT
              MIN(total_questions) AS min_questions_used,
              MAX(total_questions) AS max_questions_used
            FROM interview_sessions
            """,
        )
        print_table(
            "Question Count Range Used",
            ["min_questions_used", "max_questions_used"],
            min_max_rows,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()

