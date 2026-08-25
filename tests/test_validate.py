from src.validate import read_orders, validate_orders

rows = read_orders("data/orders.csv")
valid, rejected = validate_orders(rows)

print(f"Valid rows: {len(valid)}")
for r in valid:
    print(" ", r)

print(f"\nRejected rows: {len(rejected)}")
for r in rejected:
    print(" ", r)