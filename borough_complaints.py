import argparse
import csv
import sys
from datetime import datetime
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(
        description="Count complaint types per borough for a given date range."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input CSV file with 311 complaints"
    )
    parser.add_argument(
        "-s", "--start", required=True, help="Start date (MM/DD/YYYY)"
    )
    parser.add_argument(
        "-e", "--end", required=True, help="End date (MM/DD/YYYY)"
    )
    parser.add_argument(
        "-o", "--output", help="Output CSV file (optional, defaults to stdout)"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    try:
        start_date = datetime.strptime(args.start, "%m/%d/%Y")
        end_date = datetime.strptime(args.end, "%m/%d/%Y")
    except ValueError as e:
        print(f"Error parsing dates: {e}", file=sys.stderr)
        sys.exit(1)

    counts = defaultdict(int)

    try:
        with open(args.input, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if "Created Date" not in reader.fieldnames or \
               "Complaint Type" not in reader.fieldnames or \
               "Borough" not in reader.fieldnames:
                print("Error: CSV must contain 'Created Date', 'Complaint Type', and 'Borough' columns.", file=sys.stderr)
                sys.exit(1)

            for row in reader:
                date_str = row["Created Date"].strip()
                try:
                    created = datetime.strptime(date_str.split()[0], "%m/%d/%Y")
                except ValueError:
                    continue

                if start_date <= created <= end_date:
                    key = (row["Complaint Type"].strip(), row["Borough"].strip())
                    counts[key] += 1
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    output_lines = [("complaint type", "borough", "count")]
    for (ctype, borough), count in sorted(counts.items()):
        output_lines.append((ctype, borough, str(count)))

    if args.output:
        try:
            with open(args.output, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(output_lines)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        writer = csv.writer(sys.stdout)
        writer.writerows(output_lines)

if __name__ == "__main__":
    main()