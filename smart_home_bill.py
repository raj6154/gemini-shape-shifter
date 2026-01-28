# .   smart_home_bill.py


appliance_name = input("appliance name: (ac/heater/wm/tv): ").lower()
hours_used = int(input("enter hours used in a day: "))
days_type = input("enter days type (weekday/weekend): ").lower()
power_rating = 0

if appliance_name == "ac":
    power_rating += 12 * hours_used
elif appliance_name == "heater":
    power_rating += 10 * hours_used
elif appliance_name == "wm":
    power_rating += 8 * hours_used
elif appliance_name == "tv":
    power_rating += 5 * hours_used
else:
    print("invalid appliance name entered.")

if hours_used > 5:
    power_rating -= power_rating * 0.15  # 10% discount for more than 5 hours

if days_type == "weekday":
    power_rating -= power_rating * 0.05  # 10% discount for weekday usage

if power_rating < 1000:
    print("low power consumption")
elif 1000 <= power_rating <= 2000:
    print("medium power consumption")
else:
    print("high power consumption")

print("total power consumption in kw is :", power_rating)
