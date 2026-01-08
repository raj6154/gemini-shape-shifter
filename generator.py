import random

print("Generating 1,000,000 numbers... Please wait.")

# Open a file named 'numbers.txt' in write mode
with open("numbers.txt", "w") as f:
    for _ in range(1000000):
        # Write a random number between 1 and 100
        f.write(f"{random.randint(1, 100)}\n")

print("Done! 'numbers.txt' has been created.")
