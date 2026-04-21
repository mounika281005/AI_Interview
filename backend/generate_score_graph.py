import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate interview score trend SVG from SQLite DB.")
    parser.add_argument("--db", default="interview_system.db", help="SQLite DB path")
    parser.add_argument(
        "--out",
        default="score_trend.svg",
        help="Output SVG path (default: score_trend.svg)",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path.resolve()}")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at, CAST(overall_score AS REAL)
        FROM interview_sessions
        WHERE status IN ('completed','evaluated')
          AND overall_score IS NOT NULL
          AND CAST(overall_score AS REAL) > 0
        ORDER BY created_at
        """
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise SystemExit("No scored sessions found.")

    width, height = 1200, 700
    left, right, top, bottom = 90, 50, 70, 90
    plot_w = width - left - right
    plot_h = height - top - bottom

    values = [float(r[2]) for r in rows]
    n = len(values)

    def x_at(i: int) -> float:
        if n == 1:
            return left + plot_w / 2
        return left + (i / (n - 1)) * plot_w

    def y_at(v: float) -> float:
        # 0 at bottom, 100 at top
        return top + (100 - v) / 100 * plot_h

    points = " ".join(f"{x_at(i):.1f},{y_at(v):.1f}" for i, v in enumerate(values))

    # horizontal grid/ticks
    y_ticks = [0, 20, 40, 60, 80, 100]
    grid_lines = []
    for t in y_ticks:
        y = y_at(t)
        grid_lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>'
        )
        grid_lines.append(
            f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="14" fill="#374151">{t}</text>'
        )

    # x labels (first/mid/last date)
    first_date = str(rows[0][1])[:10]
    mid_date = str(rows[n // 2][1])[:10]
    last_date = str(rows[-1][1])[:10]
    x_labels = f"""
    <text x="{x_at(0):.1f}" y="{top+plot_h+30}" text-anchor="middle" font-size="13" fill="#374151">{first_date}</text>
    <text x="{x_at(n//2):.1f}" y="{top+plot_h+30}" text-anchor="middle" font-size="13" fill="#374151">{mid_date}</text>
    <text x="{x_at(n-1):.1f}" y="{top+plot_h+30}" text-anchor="middle" font-size="13" fill="#374151">{last_date}</text>
    """

    # points and labels
    dots = []
    for i, v in enumerate(values):
        x = x_at(i)
        y = y_at(v)
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#2563eb"/>')
        if i in {0, n - 1}:
            dots.append(
                f'<text x="{x:.1f}" y="{y-12:.1f}" text-anchor="middle" font-size="13" fill="#1f2937">{v:.1f}</text>'
            )

    avg = sum(values) / len(values)
    best = max(values)
    latest = values[-1]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{width/2}" y="36" text-anchor="middle" font-size="28" font-family="Arial, sans-serif" fill="#111827" font-weight="700">
    Interview Score Trend (0-100)
  </text>
  <text x="{width/2}" y="58" text-anchor="middle" font-size="14" font-family="Arial, sans-serif" fill="#4b5563">
    Sessions: {n} | Avg: {avg:.2f} | Best: {best:.2f} | Latest: {latest:.2f}
  </text>

  {' '.join(grid_lines)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#111827" stroke-width="2"/>
  <line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#111827" stroke-width="2"/>

  <polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="3"/>
  {''.join(dots)}
  {x_labels}

  <text x="{left+plot_w/2:.1f}" y="{height-22}" text-anchor="middle" font-size="14" fill="#374151">Session timeline</text>
  <text transform="translate(24,{top+plot_h/2:.1f}) rotate(-90)" text-anchor="middle" font-size="14" fill="#374151">Score</text>
</svg>
"""

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = Path.cwd() / out_path
    out_path.write_text(svg, encoding="utf-8")
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
