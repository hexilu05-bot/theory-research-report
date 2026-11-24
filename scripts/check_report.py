"""Check the default structure of a UTF-8 Markdown research report."""

import argparse
from pathlib import Path
import re


REQUIRED_SECTIONS = ("研究问题", "概念界定", "理论比较", "结论", "参考文献")
SECTION_HEADING = re.compile(r"^ {0,3}##[ \t]+(.+?)\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
PLACEHOLDER = re.compile(r"【待填写[^】]*】|(?<![\w])(?:TODO|TBD)(?![\w])")


def check_report(report: str) -> list[str]:
    sections = []
    placeholders = []
    open_fence = ""
    for line_number, line in enumerate(report.splitlines(), start=1):
        fence = FENCE.match(line)
        if open_fence:
            if (
                fence
                and fence[1].startswith(open_fence)
                and not fence[2].strip()
            ):
                open_fence = ""
            continue
        if fence:
            open_fence = fence[1]
            continue

        heading = SECTION_HEADING.match(line)
        if heading:
            title = re.sub(r"[ \t]+#+$", "", heading[1]).strip()
            if title in REQUIRED_SECTIONS:
                sections.append(title)
        if PLACEHOLDER.search(line):
            placeholders.append(f"第 {line_number} 行有未填写的占位符。")

    issues = []
    missing = [title for title in REQUIRED_SECTIONS if title not in sections]
    if missing:
        issues.append("缺少二级章节：" + "、".join(missing))
    expected_order = [title for title in REQUIRED_SECTIONS if title in sections]
    if list(dict.fromkeys(sections)) != expected_order:
        issues.append("章节顺序应为：" + " → ".join(REQUIRED_SECTIONS))
    if len(sections) != len(set(sections)):
        issues.append("默认章节出现重复标题。")
    return issues + placeholders


def main() -> int:
    parser = argparse.ArgumentParser(description="检查中文 Markdown 报告的默认结构。")
    parser.add_argument("report", type=Path, help="UTF-8 Markdown 报告路径")
    args = parser.parse_args()
    try:
        report = args.report.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"无法读取报告：{error}\n")

    issues = check_report(report)
    if issues:
        print("\n".join(issues))
        return 1
    print("默认章节顺序正确，未发现模板占位符。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
