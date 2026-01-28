# .        train ticket calculation program
import calendar
import datetime


distance = int(input("enter distance in km: "))
class_type = input("enter class type (first/second/third/sleeper): ").lower()


if class_type == "first":
    base_fare = 4.5 * distance
elif class_type == "second":
    base_fare = 3.5 * distance
elif class_type == "third":
    base_fare = 2.5 * distance
elif class_type == "sleeper":
    base_fare = 1.5 * distance
else:
    print("invalid class type entered.")


if class_type == "first" or class_type == "second" or class_type == "third":
    discount = 0.20 * base_fare
    base_fare -= discount
elif class_type == "sleeper":
    discount = 0.10 * base_fare
    base_fare -= discount
else:
    discount = 0


if distance >= 500:  # peak distance
    base_fare -= 0.05 * base_fare  # additional 5% discount

print("total fare is :", base_fare)
