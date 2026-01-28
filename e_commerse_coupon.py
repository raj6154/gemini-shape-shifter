# .    e_commerse_coupon.py


purchase_amount = int(input("Enter the purchase amount: "))
is_first_purchase = input("Enter y/n for 1st purchase: ").lower()
payment_method = input("payment method (card/cash/upi): ").lower()

discount = 0

if is_first_purchase == "y":
    discount += 15  # 15% discount for first purchase
elif purchase_amount >= 2000:
    discount += 10  # 10% discount for purchase amount >= 2000
elif purchase_amount >= 1000:
    discount += 5  # 5% discount for purchase amount >= 1000

paku = purchase_amount - (purchase_amount * discount) / 100

if payment_method == "upi":
    upi_discount = 5  # 5% discount for upi payment
else:
    upi_discount = 0  # 0% discount for card payment

double_discount = paku - (paku * upi_discount) / 100
print("Final amount to be paid is:", double_discount)
