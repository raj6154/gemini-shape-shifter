import calendar
import datetime

today = datetime.date.today()
day_of_week = today.strftime("%A")

many = int(input("Enter number of tickets: "))


f_price = 0
for i in range(many):
    price = 0
    age = int(input("Enter the age: "))

    tax = 15.0  # persantage
    dioscount = 20.0  # persantage

    if age >= 60:
        price = 150
    elif age < 12:
        price = 100
    elif age >= 12:
        price = 250
    else:
        print("Invalid age entered.")

    if day_of_week == "Wednesday":
        price += (price * tax) / 100
        price -= (price * dioscount) / 100
    else:
        price += (price * tax) / 100
    print("prise of ticket for age", age, "is :", price)
    f_price += price


print("your ticket price is :", f_price)
