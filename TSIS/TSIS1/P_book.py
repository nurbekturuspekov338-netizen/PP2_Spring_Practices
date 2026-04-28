import csv
import json
import os
import psycopg2
from connect import get_connection


# ──────────────────────────────────────────────
# DB initialisation
# ──────────────────────────────────────────────

def init_schema(cur):
    """Apply schema.sql and procedures.sql if they exist next to this file."""
    base = os.path.dirname(os.path.abspath(__file__))
    for fname in ("schema.sql", "procedures.sql"):
        path = os.path.join(base, fname)
        if os.path.exists(path):
            with open(path, "r") as f:
                cur.execute(f.read())
    print("Schema and procedures applied.")


# ──────────────────────────────────────────────
# Helper: pretty-print a contact row
# ──────────────────────────────────────────────

def print_contact(row, headers=("ID", "Name", "Email", "Birthday", "Group", "Phones")):
    for h, v in zip(headers, row):
        print(f"  {h:<10}: {v}")
    print()


# ──────────────────────────────────────────────
# 3.2  Advanced Console Search & Filter
# ──────────────────────────────────────────────

def menu_filter_by_group(cur):
    cur.execute("SELECT id, name FROM groups ORDER BY name;")
    groups = cur.fetchall()
    if not groups:
        print("No groups found.")
        return

    print("\nAvailable groups:")
    for gid, gname in groups:
        print(f"  {gid}. {gname}")

    try:
        choice = int(input("Enter group ID: "))
    except ValueError:
        print("Invalid input.")
        return

    sort_col = choose_sort()
    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
               STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE c.group_id = %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY {sort_col};
    """, (choice,))
    rows = cur.fetchall()
    if not rows:
        print("No contacts in this group.")
    else:
        for row in rows:
            print_contact(row)


def menu_search_by_email(cur):
    pattern = input("Enter email pattern: ").strip()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
               STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE c.email ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name;
    """, (f"%{pattern}%",))
    rows = cur.fetchall()
    if not rows:
        print("No contacts found.")
    else:
        for row in rows:
            print_contact(row)


def choose_sort():
    print("Sort by: (1) Name  (2) Birthday  (3) Date added")
    s = input("Choice [1]: ").strip()
    return {"1": "c.name", "2": "c.birthday NULLS LAST", "3": "c.created_at"}.get(s, "c.name")


def menu_search_all(cur):
    """Uses the search_contacts DB function (covers name, email, all phones)."""
    query = input("Enter search query: ").strip()
    cur.execute("SELECT * FROM search_contacts(%s);", (query,))
    rows = cur.fetchall()
    if not rows:
        print("Nothing found.")
    else:
        for row in rows:
            print_contact(row)


# ──────────────────────────────────────────────
# 3.2  Paginated navigation (console loop)
# ──────────────────────────────────────────────

def menu_paginated_navigation(cur):
    limit = 5
    offset = 0
    while True:
        sort_col = "c.name"   # fixed for pagination simplicity
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
                   STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY {sort_col}
            LIMIT %s OFFSET %s;
        """, (limit, offset))
        rows = cur.fetchall()

        print(f"\n--- Page (offset={offset}, limit={limit}) ---")
        if not rows:
            print("No more contacts.")
        else:
            for row in rows:
                print_contact(row)

        nav = input("[N]ext  [P]rev  [Q]uit: ").strip().lower()
        if nav == "n":
            if len(rows) == limit:
                offset += limit
            else:
                print("Already at last page.")
        elif nav == "p":
            offset = max(0, offset - limit)
        elif nav == "q":
            break
        else:
            print("Unknown command.")


# ──────────────────────────────────────────────
# 3.3  Import / Export
# ──────────────────────────────────────────────

def export_to_json(cur):
    cur.execute("""
        SELECT c.id, c.name, c.email,
               TO_CHAR(c.birthday, 'YYYY-MM-DD') AS birthday,
               g.name AS grp,
               JSON_AGG(
                   JSON_BUILD_OBJECT('phone', ph.phone, 'type', ph.type)
               ) FILTER (WHERE ph.id IS NOT NULL) AS phones
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name;
    """)
    rows = cur.fetchall()
    cols = ["id", "name", "email", "birthday", "group", "phones"]
    data = [dict(zip(cols, row)) for row in rows]

    filename = input("Output filename [contacts.json]: ").strip() or "contacts.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"Exported {len(data)} contacts to '{filename}'.")


def _upsert_contact_from_dict(cur, conn, contact: dict, ask_on_duplicate: bool):
    """Insert one contact; handles duplicate name and populates old 'phone' column."""
    name = contact.get("name", "").strip()
    email = contact.get("email", "")
    birthday = contact.get("birthday") or None
    group_name = contact.get("group", "Other")
    phones_list = contact.get("phones") or []

    if not name:
        print("   Skipping entry with empty name.")
        return

    # 1. Resolve group ID
    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
    row = cur.fetchone()
    if row:
        group_id = row[0]
    else:
        cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group_name,))
        group_id = cur.fetchone()[0]

    # 2. Get the "primary" phone number for the old column
    primary_phone = phones_list[0].get("phone", "") if phones_list else None

    # 3. Check for duplicates
    cur.execute("SELECT id FROM contacts WHERE name = %s;", (name,))
    existing = cur.fetchone()

    if existing:
        if ask_on_duplicate:
            ans = input(f"   Contact '{name}' already exists. [O]verwrite / [S]kip? ").strip().lower()
            if ans != "o":
                print(f"   Skipped '{name}'.")
                return
        
        # UPDATED: Added 'phone' to the SET clause
        cur.execute("""
            UPDATE contacts 
            SET email=%s, birthday=%s, group_id=%s, phone=%s 
            WHERE name=%s;
        """, (email, birthday, group_id, primary_phone, name))
        
        contact_id = existing[0]
        # Clean up phones table to prevent duplicates there
        cur.execute("DELETE FROM phones WHERE contact_id = %s;", (contact_id,))
    else:
        # UPDATED: Added 'phone' to the INSERT clause
        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id, phone)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (name, email, birthday, group_id, primary_phone))
        contact_id = cur.fetchone()[0]

    # 4. Insert all phone numbers into the new relational table
    for ph in phones_list:
        pnum = ph.get("phone", "")
        ptype = ph.get("type", "mobile")
        if pnum:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                (contact_id, pnum, ptype)
            )


def import_from_json(cur, conn):
    filename = input("JSON filename [contacts.json]: ").strip() or "contacts.json"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records from '{filename}'.")
    for contact in data:
        _upsert_contact_from_dict(cur, conn, contact, ask_on_duplicate=True)

    conn.commit()
    print("Import complete.")


def import_from_csv(cur, conn):
    """Extended CSV importer: handles name, email, birthday, group, phone, phone_type."""
    filename = input("CSV filename [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} rows from '{filename}'.")
    for row in rows:
        contact = {
            "name":     row.get("name", "").strip(),
            "email":    row.get("email", "").strip(),
            "birthday": row.get("birthday", "").strip() or None,
            "group":    row.get("group", "Other").strip(),
            "phones": [
                {
                    "phone": row.get("phone", "").strip(),
                    "type":  row.get("phone_type", "mobile").strip()
                }
            ] if row.get("phone", "").strip() else []
        }
        _upsert_contact_from_dict(cur, conn, contact, ask_on_duplicate=True)

    conn.commit()
    print("CSV import complete.")


# ──────────────────────────────────────────────
# 3.4  New Stored Procedures (console wrappers)
# ──────────────────────────────────────────────

def menu_add_phone(cur, conn):
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    print("Type: (1) mobile  (2) home  (3) work")
    t = input("Choice [1]: ").strip()
    ptype = {"1": "mobile", "2": "home", "3": "work"}.get(t, "mobile")

    cur.execute("CALL add_phone(%s, %s, %s);", (name, phone, ptype))
    conn.commit()
    print("Phone added.")


def menu_move_to_group(cur, conn):
    name  = input("Contact name: ").strip()
    group = input("Target group name: ").strip()
    cur.execute("CALL move_to_group(%s, %s);", (name, group))
    conn.commit()
    print("Contact moved to group.")


def menu_add_contact(cur, conn):
    """Quick add a new contact with optional fields."""
    name     = input("Name: ").strip()
    email    = input("Email (optional): ").strip() or None
    birthday = input("Birthday YYYY-MM-DD (optional): ").strip() or None
    group    = input("Group (Family/Work/Friend/Other) [Other]: ").strip() or "Other"
    phone    = input("First phone number: ").strip()
    print("Phone type: (1) mobile  (2) home  (3) work")
    t = input("Choice [1]: ").strip()
    ptype = {"1": "mobile", "2": "home", "3": "work"}.get(t, "mobile")

    contact = {
        "name": name, "email": email, "birthday": birthday,
        "group": group,
        "phones": [{"phone": phone, "type": ptype}] if phone else []
    }
    _upsert_contact_from_dict(cur, conn, contact, ask_on_duplicate=True)
    conn.commit()
    print("Contact saved.")


def menu_delete_contact(cur, conn):
    identifier = input("Enter contact name or phone to delete: ").strip()
    # Delete by name (cascades phones), or find contact_id by phone
    cur.execute("SELECT id FROM contacts WHERE name = %s;", (identifier,))
    row = cur.fetchone()
    if not row:
        cur.execute("SELECT contact_id FROM phones WHERE phone = %s;", (identifier,))
        row = cur.fetchone()
        if row:
            row = (row[0],)

    if row:
        cur.execute("DELETE FROM contacts WHERE id = %s;", (row[0],))
        conn.commit()
        print("Contact deleted.")
    else:
        print("Contact not found.")


# ──────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────

MENU = """
══════════════════════════════════════
       PhoneBook — TSIS 1 Menu
══════════════════════════════════════
 1. Add / update contact
 2. Delete contact
 3. Search (name, email, all phones)
 4. Filter by group
 5. Search by email
 6. Paginated contact browser
 7. Add phone number to contact
 8. Move contact to group
 9. Export contacts to JSON
10. Import contacts from JSON
11. Import contacts from CSV
 0. Exit
══════════════════════════════════════"""


def main():
    conn = get_connection()
    cur  = conn.cursor()

    try:
        init_schema(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Schema init warning: {e}")

    running = True
    while running:
        print(MENU)
        choice = input("Choose option: ").strip()

        try:
            if   choice == "1":  menu_add_contact(cur, conn)
            elif choice == "2":  menu_delete_contact(cur, conn)
            elif choice == "3":  menu_search_all(cur)
            elif choice == "4":  menu_filter_by_group(cur)
            elif choice == "5":  menu_search_by_email(cur)
            elif choice == "6":  menu_paginated_navigation(cur)
            elif choice == "7":  menu_add_phone(cur, conn)
            elif choice == "8":  menu_move_to_group(cur, conn)
            elif choice == "9":  export_to_json(cur)
            elif choice == "10": import_from_json(cur, conn)
            elif choice == "11": import_from_csv(cur, conn)
            elif choice == "0":
                running = False
                print("Goodbye!")
            else:
                print("Invalid choice.")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"DB error: {e.pgerror or e}")
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()