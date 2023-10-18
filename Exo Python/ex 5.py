year = float(input("Year: "))
if year % 100 and not year % 4 or not year % 400:
    print("Leap year")
else:
    print("Not leap year")
