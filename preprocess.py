import argparse
import csv
from datetime import datetime
from collections import defaultdict

def preprocess(input_file, output_file=None):
    response_times = defaultdict(list)

    with open(input_file, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                created = datetime.strptime(row["Created Date"], "%m/%d/%Y %H:%M:%S %p")
                closed = row.get("Closed Date", "").strip()
                if not closed:
                    continue
                closed = datetime.strptime(closed, "%m/%d/%Y %H:%M:%S %p")
            except (ValueError, KeyError):
                continue

            if created.year != 2024:
                continue

            delta_hours = (closed - created).total_seconds() / 3600.0
            year_month = f"{created.year}-{created.month:02d}"
            zipcode = row.get("Incident Zip", "").strip()

            if zipcode:
                response_times[(year_month, zipcode)].append(delta_hours)
            response_times[(year_month, "ALL")].append(delta_hours)

    results = []
    for (year_month, zipcode), times in sorted(response_times.items()):
        avg_hours = sum(times) / len(times)
        results.append([year_month, zipcode, round(avg_hours, 2)])

    if output_file is None:
        output_file = "monthly_avg.csv"

    with open(output_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "zipcode", "avg_response_hours"])
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess 311 complaint data to compute monthly average response times (hours) per zipcode (2024 only)."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input CSV file for 2024 data"
    )
    parser.add_argument(
        "-o", "--output", help="Optional output CSV file (default: monthly_avg.csv)"
    )

    args = parser.parse_args()
    preprocess(args.input, args.output)


if __name__ == "__main__":
    main()