import psycopg2
import csv
from config import DB_host, DB_base, DB_user, DB_pass
conn=None
cur=None
try:
    conn = psycopg2.connect(
        host=DB_host,
        database=DB_base,
        user=DB_user,
        password=DB_pass
        )
    command = """CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL
    );"""
    cur= conn.cursor()
    cur.execute(command)
    conn.commit()
except Exception as error:
    print(error)
    exit(1)
try:
    while True:
        print("\n--- PhoneBook ---")
        print("1. Show all contacts")
        print("2. Add contact (console)")
        print("3. Import from CSV")
        print("4. Search")
        print("5. Update phone by name")
        print("6. Update name by phone")
        print("7. Delete by name")
        print("8. Delete by phone")
        print("0. Exit")
        choose=input().strip()
        if choose=="0":
            print("Exiting...")
            break
        elif choose=="1":
            cur.execute("SELECT * FROM phonebook")
            print(cur.fetchall())
        elif choose=="2":
            print("Please, input first name, last name and phone number")
            f_name=input("Input first name: ")
            ph_number=input("Input phone number: ")   
            cur.execute("""INSERT INTO phonebook (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING""", (f_name, ph_number))   
            conn.commit()
        elif choose=="3":
            print("input file name")
            file_name=input()
            with open(file_name, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    first_name, phone = row
                    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING", (first_name, phone))
                    conn.commit()
        elif choose=="4":
            pattern = input("Search: ").strip()
            command = """SELECT * FROM phonebook WHERE name ILIKE %s OR phone ILIKE %s"""
            if not pattern:
                print("  (no contacts)")
                continue
            like_pattern = f"%{pattern}%"
            cur.execute(command, (like_pattern, like_pattern))
            results=cur.fetchall()
            if not results:
                print("  (no contacts found)")
            else:
                for c in results:
                    print(f"  [{c[0]}] {c[1]} - {c[2]}")
        elif choose == "5":
            name = input("Input name to update phone: ").strip()
            new_phone = input("Input new phone: ").strip()

            command = "UPDATE phonebook SET phone = %s WHERE name ILIKE %s"
            cur.execute(command, (new_phone, name))

            conn.commit()

            if cur.rowcount == 0:
                print("No contact found")
            else:
                print(f"Updated {cur.rowcount} row(s)")
        elif choose == "6":
            phone = input("Input phone to find: ").strip()
            new_name = input("Input new name: ").strip()

            command = "UPDATE phonebook SET name = %s WHERE phone = %s"
            cur.execute(command, (new_name, phone))

            conn.commit()

            if cur.rowcount == 0:
                print("No contact found")
            else:
                print(f"Updated {cur.rowcount} row(s)")
        elif choose=="7":
            name=input("Input name for deleting: ")
            command="""DELETE FROM phonebook WHERE name=%s"""
            cur.execute(command, (name,))
            conn.commit()
            print(f"Deleted {cur.rowcount} row(s)")
        elif choose=="8":
            phone=input("Input phone for deleting: ")
            command="""DELETE FROM phonebook WHERE phone=%s """
            cur.execute(command, (phone,))
            conn.commit()
            print(f"Deleted {cur.rowcount} row(s)")
        else:
            print("Invalid syntax")
except KeyboardInterrupt:
    print("\nProgram terminated by user")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
    print("Database connection closed.")
