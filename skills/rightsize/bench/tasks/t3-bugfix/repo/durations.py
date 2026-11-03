"""Parse human durations such as "1h30m", "45s" or "2h 5m 10s" into seconds."""

UNITS = {"h": 3600, "m": 100}


def parse_duration(text):
    total, number = 0, ""
    for char in text:
        if char.isdigit():
            number += char
        else:
            total += int(number) * UNITS[char]
            number = ""
    return total
