import sqlite3
import sys


# --- 1. DATABASE CONNECTION ---
def get_connection():
    return sqlite3.connect("company.db")


# --- 2. YOUR ORIGINAL DESIGN ENGINE (Visuals) ---
def design(cursor, table_name):
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

        if not data:
            print(f"\n[!] Table '{table_name}' is empty.")
            return

        # Get headers
        headers = [i[0] for i in cursor.description]

        # Calculate widths
        maxima = []
        for i in range(len(headers)):
            col_max = max([len(str(row[i])) for row in data] + [len(headers[i])])
            maxima.append(col_max)

        # Print Table
        print("\n+", end="")
        for m in maxima:
            print("-" * (m + 2) + "+", end="")
        print()

        print("|", end="")
        for i, h in enumerate(headers):
            print(" " + str(h).center(maxima[i]) + " |", end="")
        print()

        print("+", end="")
        for m in maxima:
            print("-" * (m + 2) + "+", end="")
        print()

        for row in data:
            print("|", end="")
            for i, item in enumerate(row):
                print(" " + str(item).ljust(maxima[i]) + " |", end="")
            print()

        print("+", end="")
        for m in maxima:
            print("-" * (m + 2) + "+", end="")
        print("\n")

    except Exception as e:
        print(f"Error in design: {e}")


# --- 3. ACTION FUNCTIONS ---
def add_employee():
    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- ADD NEW EMPLOYEE ---")
    name = input("Enter Name: ")
    salary = input("Enter Salary: ")

    # Secure Insert
    cursor.execute("INSERT INTO employees (name, salary) VALUES (?, ?)", (name, salary))
    conn.commit()
    print(f"Success! {name} added.")
    conn.close()


def delete_employee():
    conn = get_connection()
    cursor = conn.cursor()

    # Show list first so user knows the ID
    design(cursor, "employees")

    print("\n--- DELETE EMPLOYEE ---")
    target_id = input("Enter ID to delete: ")

    cursor.execute("DELETE FROM employees WHERE id = ?", (target_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"Success! ID {target_id} deleted.")
    else:
        print("Error: ID not found.")
    conn.close()


# --- 4. THE MAIN MENU LOOP ---
def main_menu():
    while True:
        print("\n" + "=" * 30)
        print(" COMPANY MANAGEMENT SYSTEM")
        print("=" * 30)
        print("1. View All Employees")
        print("2. Add New Employee")
        print("3. Delete Employee")
        print("4. Exit")

        choice = input("\nEnter Choice (1-4): ")

        if choice == "1":
            conn = get_connection()
            design(conn.cursor(), "employees")
            conn.close()

        elif choice == "2":
            add_employee()

        elif choice == "3":
            delete_employee()

        elif choice == "4":
            print("Exiting... Goodbye!")
            break  # This stops the infinite loop

        else:
            print("[!] Invalid Choice. Try again.")


# --- 5. START THE PROGRAM ---
if __name__ == "__main__":
    main_menu()
