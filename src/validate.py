import csv
from datetime import datetime


def read_orders(csv_path):
    """Reads raw rows from a CSV file into a list of dicts."""
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_orders(rows):
    """Splits rows into valid and rejected, with a reason for each rejection."""
    valid = []
    rejected = []

    for row in rows:
        errors = []

        if not row.get("customer", "").strip():
            errors.append("missing customer")

        try:
            amount = float(row.get("amount", ""))
            if amount < 0:
                errors.append("negative amount")
        except ValueError:
            errors.append("amount is not a number")

        try:
            datetime.strptime(row.get("date", ""), "%Y-%m-%d")
        except ValueError:
            errors.append("invalid date format")

        if errors:
            row["_errors"] = "; ".join(errors)
            rejected.append(row)
        else:
            valid.append(row)

    return valid, rejected