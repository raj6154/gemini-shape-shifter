import math

print("                                ➭PROGRAMME TO DISPLAY TABLE OF A GIVEN NUMBER ")
print("  ☛press ➊ for normal table i.e. up to 10")
print("  ☛press ➋ for table up to your choice")
print("  ☛press ➌ for ∞ table ")
ch, flag = int(input("enter your choice :")), 0
if ch == 2:
    b, a = int(eval(input("enter number up to u wanna :"))), eval(
        input("which table u want:")
    )
elif ch == 1:
    b, a = 10, eval(input("which table u want:"))
elif ch == 3:
    b, a = 99999999999, eval(input("which table u want:"))
else:
    print("        ☠enter valid choise☠")
    print("        ✔only 3 choise is available ")
    flag = 1
if flag == 0:
    if type(a) == float:
        print("       ➣ you entered float number")
        print("  ☛press ➊ for round off value ")
        print("  ☛press ➋ for normal value    ")
        ch2 = int(input("enter your choice : "))
        if ch2 != 1 and ch2 != 2:
            flag = 1
            print("       ☠enter valid choise☠")
            print("        ✔only 2 choise is available ")
if flag == 0:
    for i in range(1, b + 1):
        if a == int(a):  # integer checking
            print(
                int(a),
                "✗",
                "0" * (len(str(b)) - len(str(i))) + str(i),
                "=",
                "-"
                * (len(str(int((int(a)) * i))) - len(str(int(math.fabs((int(a)) * i)))))
                + "0"
                * (len(str(math.fabs(int(a) * b))) - len(str(math.fabs((int(a)) * i))))
                + str(int(math.fabs((int(a)) * i))),
            )
        else:  # float
            if ch2 == 1:
                print(
                    a,
                    "✗",
                    "0" * (len(str(b)) - len(str(i))) + str(i),
                    "≈",
                    "-" * (len(str(int(a * i))) - len(str(int(math.fabs(a * i)))))
                    + "0"
                    * (
                        len(str(math.fabs(int(a * b))))
                        - len(str(math.fabs(int(a * i))))
                    )
                    + (str(math.fabs(a * i)).partition(".")[0])
                    + (str(math.fabs(a * i)).partition(".")[1])
                    + str(str(math.fabs(a * i)).partition(".")[2])[0:2]
                    + "0"
                    * (2 - (len(str(str(math.fabs(a * i)).partition(".")[2])[0:2]))),
                )
            elif ch2 == 2:
                print(
                    a,
                    "✗",
                    "0" * (len(str(b)) - len(str(i))) + str(i),
                    "=",
                    "-" * (len(str(int(a * i))) - len(str(int(math.fabs(a * i)))))
                    + "0"
                    * (
                        len(str(math.fabs(int(a * b))))
                        - len(str(math.fabs(int(a * i))))
                    )
                    + str(math.fabs(a * i))
                    + "0" * (16 - len(str(a * i).partition(".")[2])),
                )
