import re

timezones = set()
relations = []

with open("zone1970.tab", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = re.split(r"\s+", line, maxsplit=3)

        country_codes = parts[0].split(",")
        timezone_name = parts[2]

        timezones.add(timezone_name)

        for cc in country_codes:
            relations.append((cc, timezone_name))


with open("seed_timezones.sql", "w", encoding="utf-8") as out:

    # --------------------------------------------------
    # 1. Seed TIMEZONES table
    # --------------------------------------------------
    out.write("-- ================================\n")
    out.write("-- Seed timezones (IANA tzdb)\n")
    out.write("-- ================================\n\n")

    for tz in sorted(timezones):
        tz_safe = tz.replace("'", "''")

        out.write(f"""
MERGE INTO timezones AS target
USING (VALUES ('{tz_safe}')) AS source (name)
ON target.name = source.name
WHEN NOT MATCHED THEN
    INSERT (name) VALUES (source.name);
""")

    # --------------------------------------------------
    # 2. Seed COUNTRY_TIMEZONES join table
    # --------------------------------------------------
    out.write("\n-- =========================================\n")
    out.write("-- Seed countryTimezones (ISO ↔ IANA)\n")
    out.write("-- =========================================\n\n")

    for country_code2, tz in relations:
        tz_safe = tz.replace("'", "''")

        out.write(f"""
MERGE INTO countryTimezones AS target
USING (
    SELECT
        '{country_code2}' AS CountryCode2,
        t.id AS TimezoneId
    FROM timezones t
    WHERE t.name = '{tz_safe}'
) AS source
ON target.CountryCode2 = source.CountryCode2
AND target.TimezoneId = source.TimezoneId
WHEN NOT MATCHED THEN
    INSERT (CountryCode2, TimezoneId)
    VALUES (source.CountryCode2, source.TimezoneId);
""")
