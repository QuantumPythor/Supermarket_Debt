"""
🛒 Supermarket Debt Splitter
---------------------------------
A simple and fun Python script to calculate who owes what after a shared grocery purchase.

👤 Participants: A, M, S
- 'For 3' → everyone pays one third (A, M, S)
- 'For 2' → only A and M share half each
- The buyer pays upfront and others reimburse accordingly.
"""

# --- Input section ---
buyer = input("🧾 Who paid for the groceries? (A, M, S): ").upper()
total = float(input("💰 Total cost (€): "))
for_3 = float(input("🥦 Amount shared by 3 (€): "))
for_2 = float(input("🍞 Amount shared by 2 (€): "))

# --- Sanity check ---
if for_3 + for_2 > total:
    print("❌ Error: the sum of 'for 3' and 'for 2' exceeds the total.")
    raise SystemExit

# --- Debt calculation ---
share_3 = for_3 / 3
share_2 = for_2 / 2

debt_A = debt_M = debt_S = 0

if buyer == "A":
    debt_M = share_3 + share_2
    debt_S = share_3
elif buyer == "M":
    debt_A = share_3 + share_2
    debt_S = share_3
elif buyer == "S":
    debt_A = share_3
    debt_M = share_3
else:
    print("❌ Invalid name.")
    raise SystemExit

# --- Results ---
print("\n📊 Payment summary:")
print(f"A owes: €{debt_A:.2f}")
print(f"M owes: €{debt_M:.2f}")
print(f"S owes: €{debt_S:.2f}")
print(f"\n💡 Buyer {buyer} will be reimbursed by the others accordingly!")

# - You can easily adjust the participants' names
# - If your group has different rules, modify the logic in the “Debt calculation” section
# - Works purely with Python’s standard library — no external dependencies