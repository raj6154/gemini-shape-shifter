import sqlite3

# 1. Connect to the database file (The Bridge)
# We use the direct name because the file is right next to this script.
connection = sqlite3.connect("company.db")

# 2. Create a "Cursor" (The Messenger)
# The cursor sends your SQL commands to the database.
cursor = connection.cursor()

# 3. Read data from the database
print("--- Current Employees ---")
cursor.execute("SELECT * FROM employees")
rows = cursor.fetchall()  # Fetch all results

for row in rows:
    print(row)

# 4. Ask User for new data
print("\n--- Add New Employee ---")
new_name = input("Enter Name: ")
new_salary = input("Enter Salary: ")

# 5. Insert the data (Using ? is the Safe/Professional way to prevent hacking)
cursor.execute(
    "INSERT INTO employees (name, salary) VALUES (?, ?)", (new_name, new_salary)
)

# 6. Save (Commit) the changes
connection.commit()
print("Saved successfully!")

# 7. Close the connection
connection.close()
