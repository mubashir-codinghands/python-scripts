import csv

with open("slim-2.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    with open("countries.sql", "w", encoding="utf-8") as sqlfile:
        for row in reader:
            name = row["name"].replace("'", "''")
            code2 = row["alpha-2"]
            numeric = row["country-code"].zfill(3)

            sqlfile.write(
                f"""
MERGE INTO countries AS target
USING (VALUES ('{code2}', '{name}', '{numeric}'))
       AS source (Code2, Name, NumericCode)
ON target.code2 = source.code2
WHEN NOT MATCHED THEN
    INSERT (code2, name, numericCode)
    VALUES (source.code2, source.name, source.numericCode);
"""
            )
