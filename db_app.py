import sqlite3

connection = sqlite3.connect("company.db")
cursor = connection.cursor()

def search_employee():
    print("\n--- Employee Search ---")
    limit = input("Search for salaries higher than: ")
    
    # 1. We use the '?' security feature (Parametrized Query)
    cursor.execute("SELECT * FROM employees WHERE salary > ?", (limit,))
    results = cursor.fetchall()
    
    if len(results) == 0:
        print("No matches found.")
    else:
        print(f"\nFound {len(results)} employees:")
        # 2. Simple loop (We can make this a fancy table later like your project)
        for row in results:
            print(f"ID: {row[0]} | Name: {row[1]} | Salary: {row[2]}")

# Run it
search_employee()
connection.close()