import csv
import json
from connect import connect


def run_sql_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

    print(f"{filename} executed successfully.")


def create_schema():
    run_sql_file("schema.sql")


def create_procedures():
    run_sql_file("procedure.sql")


def get_group_id(cur, group_name):
    if not group_name:  # Checks for None or empty string
        return None
    
    # Existing logic to find or create the group
    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    return cur.fetchone()[0]


def add_contact():
    name = input("Name: ").strip()
    surname = input("Surname: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD: ").strip()
    group_name = input("Group: ").strip()
    phone = input("Phone: ").strip()
    phone_type = input("Phone type home/work/mobile: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            group_id = get_group_id(cur, group_name)

            cur.execute("""
                INSERT INTO contacts(name, surname, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET
                    surname = EXCLUDED.surname,
                    email = EXCLUDED.email,
                    birthday = EXCLUDED.birthday,
                    group_id = EXCLUDED.group_id
                RETURNING id
            """, (name, surname, email, birthday, group_id))

            contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, phone, phone_type))

        conn.commit()

    print("Contact added successfully.")


def add_phone():
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Phone type home/work/mobile: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()

    print("Phone added.")


def move_to_group():
    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()

    print("Contact moved to group.")


def search_contacts():
    query = input("Search: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()

    print_rows(rows)


def search_by_email():
    email = input("Email search: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                WHERE c.email ILIKE %s
            """, (f"%{email}%",))
            rows = cur.fetchall()

    print_rows(rows)


def filter_by_group():
    group_name = input("Group name: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                WHERE g.name ILIKE %s
            """, (group_name,))
            rows = cur.fetchall()

    print_rows(rows)


def sort_contacts():
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")

    choice = input("Choose: ").strip()

    if choice == "1":
        order_by = "c.name"
    elif choice == "2":
        order_by = "c.birthday"
    elif choice == "3":
        order_by = "c.date_added"
    else:
        print("Invalid choice.")
        return

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name, c.date_added
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY {order_by}
            """)
            rows = cur.fetchall()

    print_rows(rows)


def paginated_navigation():
    limit = int(input("Page size: "))
    offset = 0

    while True:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_paginated(%s, %s)",
                    (limit, offset)
                )
                rows = cur.fetchall()

        print_rows(rows)

        command = input("next / prev / quit: ").strip().lower()

        if command == "next":
            offset += limit
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break
        else:
            print("Wrong command.")


def import_csv():
    filename = input("CSV filename: ").strip()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        with connect() as conn:
            with conn.cursor() as cur:
                for row in reader:
                    group_id = get_group_id(cur, row["group"])

                    cur.execute("""
                        INSERT INTO contacts(name, surname, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (name)
                        DO UPDATE SET
                            surname = EXCLUDED.surname,
                            email = EXCLUDED.email,
                            birthday = EXCLUDED.birthday,
                            group_id = EXCLUDED.group_id
                        RETURNING id
                    """, (
                        row["name"],
                        row["surname"],
                        row["email"],
                        row["birthday"],
                        group_id
                    ))

                    contact_id = cur.fetchone()[0]

                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                    """, (
                        contact_id,
                        row["phone"],
                        row["type"]
                    ))

            conn.commit()

    print("CSV imported.")


def export_json():
    filename = input("JSON filename: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.id
            """)
            contacts = cur.fetchall()

            data = []

            for contact in contacts:
                contact_id = contact[0]

                cur.execute("""
                    SELECT phone, type
                    FROM phones
                    WHERE contact_id = %s
                """, (contact_id,))

                phones = cur.fetchall()

                data.append({
                    "name": contact[1],
                    "surname": contact[2],
                    "email": contact[3],
                    "birthday": str(contact[4]) if contact[4] else None,
                    "group": contact[5],
                    "phones": [
                        {"phone": p[0], "type": p[1]}
                        for p in phones
                    ]
                })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("JSON exported.")


def import_json():
    filename = input("JSON filename: ").strip()

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    with connect() as conn:
        with conn.cursor() as cur:
            for item in data:
                name = item["name"]

                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                exists = cur.fetchone()

                if exists:
                    action = input(f"{name} exists. skip/overwrite: ").strip().lower()

                    if action == "skip":
                        continue

                    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))

                group_id = get_group_id(cur, item["group"])

                cur.execute("""
                    INSERT INTO contacts(name, surname, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    item["name"],
                    item["surname"],
                    item["email"],
                    item["birthday"],
                    group_id
                ))

                contact_id = cur.fetchone()[0]

                for phone in item["phones"]:
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                    """, (
                        contact_id,
                        phone["phone"],
                        phone["type"]
                    ))

        conn.commit()

    print("JSON imported.")


def show_all_contacts():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.id
            """)
            rows = cur.fetchall()

    print_rows(rows)


def print_rows(rows):
    if not rows:
        print("No data found.")
        return

    print("\nResults:")
    for row in rows:
        print(row)


def menu():
    while True:
        print("\n=== TSIS1 PHONEBOOK ===")
        print("1. Create schema")
        print("2. Create procedures/functions")
        print("3. Add contact")
        print("4. Add phone")
        print("5. Move contact to group")
        print("6. Search contacts")
        print("7. Search by email")
        print("8. Filter by group")
        print("9. Sort contacts")
        print("10. Paginated navigation")
        print("11. Import CSV")
        print("12. Export JSON")
        print("13. Import JSON")
        print("14. Show all contacts")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            create_schema()
        elif choice == "2":
            create_procedures()
        elif choice == "3":
            add_contact()
        elif choice == "4":
            add_phone()
        elif choice == "5":
            move_to_group()
        elif choice == "6":
            search_contacts()
        elif choice == "7":
            search_by_email()
        elif choice == "8":
            filter_by_group()
        elif choice == "9":
            sort_contacts()
        elif choice == "10":
            paginated_navigation()
        elif choice == "11":
            import_csv()
        elif choice == "12":
            export_json()
        elif choice == "13":
            import_json()
        elif choice == "14":
            show_all_contacts()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()