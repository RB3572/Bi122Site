#!/usr/bin/env python3
"""Regenerate the lecture schedule table and the subscribable calendar feed.

Reads schedule.json and writes:
  schedule.ics    an iCalendar feed for Google/Apple/Outlook subscription
  schedule.html   the <tbody> between the SCHEDULE markers

Run from the repository root:  python3 tools/build-schedule.py
"""

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "bi122resources.rishib.com"

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# America/Los_Angeles, sufficient for any year the course runs in.
VTIMEZONE = """BEGIN:VTIMEZONE
TZID:America/Los_Angeles
X-LIC-LOCATION:America/Los_Angeles
BEGIN:DAYLIGHT
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
TZNAME:PST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""


def esc(text):
    """Escape a value for iCalendar (RFC 5545 §3.3.11)."""
    return (text.replace("\\", "\\\\")
                .replace(";", "\\;")
                .replace(",", "\\,")
                .replace("\n", "\\n"))


def fold(line):
    """Fold long lines to 75 octets, continuing with a leading space."""
    out, raw = [], line.encode("utf-8")
    limit = 73
    while len(raw) > limit:
        cut = limit
        while cut > 0 and (raw[cut] & 0xC0) == 0x80:   # never split a UTF-8 char
            cut -= 1
        out.append(raw[:cut].decode("utf-8"))
        raw = raw[cut:]
        limit = 72
    out.append(raw.decode("utf-8"))
    return "\r\n ".join(out)


def build_ics(cfg):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    seq = int(cfg.get("_sequence", 0))
    sh, sm = (int(x) for x in cfg["start"].split(":"))
    eh, em = (int(x) for x in cfg["end"].split(":"))

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Bi 122 Genetics//Course Schedule//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Bi 122 · Genetics ({cfg['term']})",
        f"X-WR-TIMEZONE:{cfg['timezone']}",
        "X-WR-CALDESC:Lecture schedule for Bi 122 Genetics, Caltech. "
        f"Maintained at https://{DOMAIN}/schedule.html",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
        VTIMEZONE,
    ]

    for lec in cfg["lectures"]:
        d = datetime.strptime(lec["date"], "%Y-%m-%d")
        uid = f"bi122-{lec['date']}@{DOMAIN}"
        desc = f"Week {lec['week']}."
        if lec.get("readings") and lec["readings"] != "—":
            desc += f" Reading: {lec['readings']}."
        desc += f" Handouts and syllabus: https://{DOMAIN}/"

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{stamp}")
        lines.append(f"SEQUENCE:{seq}")

        if lec.get("cancelled"):
            # All-day, free-time marker: informative without blocking the slot.
            nxt = (d + timedelta(days=1)).strftime("%Y%m%d")
            lines.append(f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{nxt}")
            lines.append("TRANSP:TRANSPARENT")
            lines.append(f"SUMMARY:{esc('Bi 122 — ' + lec['topic'])}")
        else:
            tz = cfg["timezone"]
            lines.append(f"DTSTART;TZID={tz}:{d.strftime('%Y%m%d')}T{sh:02d}{sm:02d}00")
            lines.append(f"DTEND;TZID={tz}:{d.strftime('%Y%m%d')}T{eh:02d}{em:02d}00")
            lines.append("TRANSP:OPAQUE")
            lines.append(f"SUMMARY:{esc('Bi 122 — ' + lec['topic'])}")
            lines.append(f"LOCATION:{esc(cfg['location'])}")

        lines.append(f"DESCRIPTION:{esc(desc)}")
        lines.append(f"URL:https://{DOMAIN}/schedule.html")
        lines.append("STATUS:CONFIRMED")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    body = "\r\n".join(fold(ln) for line in lines for ln in line.split("\n"))
    return body + "\r\n"


def build_rows(cfg):
    rows, prev_week = [], None
    for lec in cfg["lectures"]:
        d = datetime.strptime(lec["date"], "%Y-%m-%d")
        new_week = lec["week"] != prev_week
        prev_week = lec["week"]
        cls = []
        if new_week and rows:
            cls.append("rule")
        if lec.get("cancelled"):
            cls.append("row-off")
        attr = f' class="{" ".join(cls)}"' if cls else ""
        wk = str(lec["week"]) if new_week else ""
        date = f"{d.month}/{d.day}"
        rows.append(
            f'            <tr{attr}><td class="week">{wk}</td>'
            f'<td class="date">{date}</td>'
            f'<td class="topic">{lec["topic"]}</td>'
            f'<td class="reading">{lec["readings"]}</td></tr>'
        )
    return "\n".join(rows)


def main():
    cfg = json.loads((ROOT / "schedule.json").read_text())

    # Written as bytes so the CRLF line endings RFC 5545 requires survive.
    (ROOT / "schedule.ics").write_bytes(build_ics(cfg).encode("utf-8"))
    print(f"schedule.ics    {len(cfg['lectures'])} events")

    page = (ROOT / "schedule.html").read_text()
    new, n = re.subn(
        r"(<!-- BEGIN schedule -->\n).*?(\n\s*<!-- END schedule -->)",
        lambda m: m.group(1) + build_rows(cfg) + m.group(2),
        page, flags=re.S)
    if n != 1:
        raise SystemExit("schedule.html: could not find the BEGIN/END schedule markers")
    (ROOT / "schedule.html").write_text(new)
    print("schedule.html   table rebuilt")


if __name__ == "__main__":
    main()
