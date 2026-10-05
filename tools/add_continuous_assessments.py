from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re

CALENDAR = Path("calendar/UoM_Robotics_2026-27.ics")

DATES = [
    (2, "2026-09-28"),
    (3, "2026-10-05"),
    (4, "2026-10-12"),
    (5, "2026-10-19"),
    (6, "2026-10-26"),
    (7, "2026-11-02"),
    (8, "2026-11-09"),
    (9, "2026-11-16"),
    (10, "2026-11-23"),
    (11, "2026-11-30"),
]

LOCATION = "Nancy Rothwell_BLENDED Th1 (GA 056)"


def utc_stamp(local_date: str, hour: int, minute: int) -> str:
    local = datetime.strptime(local_date, "%Y-%m-%d").replace(
        hour=hour, minute=minute, tzinfo=ZoneInfo("Europe/London")
    )
    return local.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def fold(line: str, limit: int = 73) -> str:
    if len(line) <= limit:
        return line
    parts = [line[:limit]]
    rest = line[limit:]
    while rest:
        parts.append(" " + rest[: limit - 1])
        rest = rest[limit - 1 :]
    return "\r\n".join(parts)


text = CALENDAR.read_text(encoding="utf-8")
text = text.replace("\r\n", "\n").replace("\r", "\n")

# Idempotent: remove copies created by this script before adding the current set.
text = re.sub(
    r"BEGIN:VEVENT\nUID:continuous-assessment-week-\d+-2026@uom-clean\n[\s\S]*?END:VEVENT\n?",
    "",
    text,
)

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
blocks = []
for week, date in DATES:
    lines = [
        "BEGIN:VEVENT",
        f"UID:continuous-assessment-week-{week}-2026@uom-clean",
        f"DTSTAMP:{stamp}",
        f"DTSTART:{utc_stamp(date, 12, 5)}",
        f"DTEND:{utc_stamp(date, 13, 10)}",
        f"SUMMARY:Continuous Assessment (Week {week})",
        f"LOCATION:{LOCATION}",
        (
            "DESCRIPTION:Assessment: Continuous Assessment\\n"
            f"Week: {week}\\nLocation: {LOCATION}\\n"
            "Time: 12:05-13:10 (UK local time)"
        ),
        "END:VEVENT",
    ]
    blocks.append("\r\n".join(fold(line) for line in lines))

payload = "\r\n".join(blocks) + "\r\n"
text = text.replace("\nEND:VCALENDAR", "\n" + payload.replace("\r\n", "\n") + "END:VCALENDAR", 1)
text = text.replace("\n", "\r\n")
CALENDAR.write_text(text, encoding="utf-8", newline="")

assert text.count("UID:continuous-assessment-week-") == 10
assert text.count(f"LOCATION:{LOCATION}") == 10
print("Updated Week 2-11 continuous assessments: Mondays 12:05-13:10, Nancy Rothwell_BLENDED Th1 (GA 056)")
