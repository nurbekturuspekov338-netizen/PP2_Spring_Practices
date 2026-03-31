import psycopg2
from config import DB_host, DB_base, DB_user, DB_pass

def create_db_objects(cur):
    cur.execute("""
    CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
    RETURNS TABLE (id INTEGER, name VARCHAR(100), phone VARCHAR(20)) AS $$
    BEGIN
        RETURN QUERY 
        SELECT c.id, c.name, c.phone 
        FROM phonebook c
        WHERE c.name ILIKE '%' || p_pattern || '%'
           OR c.phone ILIKE '%' || p_pattern || '%';
    END;
    $$ LANGUAGE plpgsql;
    """)

    cur.execute("""
    CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR(100), p_phone VARCHAR(20))
    LANGUAGE plpgsql AS $$
    BEGIN
        IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
            UPDATE phonebook 
            SET phone = p_phone 
            WHERE name = p_name;
            RAISE NOTICE 'Contact "%" updated', p_name;
        ELSE
            INSERT INTO phonebook (name, phone) 
            VALUES (p_name, p_phone);
            RAISE NOTICE 'Contact "%" added', p_name;
        END IF;
    END;
    $$;
    """)

    cur.execute("""
    CREATE OR REPLACE PROCEDURE insert_many_contacts(
        p_names TEXT[], 
        p_phones TEXT[],
        OUT invalid_names TEXT[],
        OUT invalid_phones TEXT[],
        OUT invalid_reasons TEXT[]
    )
    LANGUAGE plpgsql AS $$
    DECLARE
        i INTEGER;
        v_name TEXT;
        v_phone TEXT;
        v_reason TEXT;
    BEGIN
        invalid_names := ARRAY[]::TEXT[];
        invalid_phones := ARRAY[]::TEXT[];
        invalid_reasons := ARRAY[]::TEXT[];

        IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
            RAISE EXCEPTION 'Arrays of names and phones must have the same length!';
        END IF;

        FOR i IN 1..array_length(p_names, 1) LOOP
            v_name := p_names[i];
            v_phone := p_phones[i];
            v_reason := NULL;

            -- Phone validation: must start with + and contain only digits
            IF v_phone IS NULL OR v_phone = '' OR v_phone !~ '^\+[0-9]+$' THEN
                v_reason := 'Invalid phone format (must start with + and contain only digits)';
            END IF;

            IF v_reason IS NOT NULL THEN
                invalid_names := array_append(invalid_names, COALESCE(v_name, 'NULL'));
                invalid_phones := array_append(invalid_phones, COALESCE(v_phone, 'NULL'));
                invalid_reasons := array_append(invalid_reasons, v_reason);
            ELSE
                -- Upsert logic
                IF EXISTS (SELECT 1 FROM contacts WHERE name = v_name) THEN
                    UPDATE phonebook SET phone = v_phone WHERE name = v_name;
                ELSE
                    INSERT INTO phonebook (name, phone) VALUES (v_name, v_phone);
                END IF;
            END IF;
        END LOOP;
    END;
    $$;
    """)


    cur.execute("""
    CREATE OR REPLACE FUNCTION get_contacts_paginated(
        p_limit INTEGER DEFAULT 5, 
        p_offset INTEGER DEFAULT 0
    )
    RETURNS TABLE (id INTEGER, name VARCHAR(100), phone VARCHAR(20)) AS $$
    BEGIN
        RETURN QUERY 
        SELECT c.id, c.name, c.phone 
        FROM phonebook c
        ORDER BY c.name
        LIMIT p_limit 
        OFFSET p_offset;
    END;
    $$ LANGUAGE plpgsql;
    """)

    cur.execute("""
    CREATE OR REPLACE PROCEDURE delete_contact_by_identifier(p_identifier TEXT)
    LANGUAGE plpgsql AS $$
    DECLARE
        deleted_count INTEGER;
    BEGIN
        DELETE FROM phonebook 
        WHERE name = p_identifier 
           OR phone = p_identifier;
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        
        RAISE NOTICE 'Deleted % contact(s) with identifier "%"', deleted_count, p_identifier;
    END;
    $$;
    """)

    print("Database objects created/updated successfully.")

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
    conn.autocommit = False  
    cur = conn.cursor()
    cur.execute(command)

    create_db_objects(cur)
    conn.commit()

    running = True
    while running:
        print("\n------ Phone Book Menu ------")
        print("1. Search by pattern")
        print("2. Add/Update single contact (upsert)")
        print("3. Add many contacts with validation")
        print("4. Show contacts with pagination")
        print("5. Delete contact by name or phone")
        print("6. Exit")
        
        choose = input("Choose option (1-6): ").strip()

        try:
            if choose == "1":
                pattern = input("Enter search pattern: ").strip()
                cur.execute("SELECT * FROM get_contacts_by_pattern(%s);", (pattern,))
                rows = cur.fetchall()
                
                print(f"\nSearch results for '{pattern}':")
                if not rows:
                    print("Nothing found.")
                else:
                    for row in rows:
                        print(f"ID: {row[0]:<3} | Name: {row[1]:<25} | Phone: {row[2]}")

            elif choose == "2":
                name = input("Enter name: ").strip()
                phone = input("Enter phone: ").strip()
                if not name or not phone:
                    print("Name and phone cannot be empty.")
                    continue
                
                cur.execute("CALL upsert_contact(%s, %s);", (name, phone))
                conn.commit()
                print("Operation completed.")

            elif choose == "3":
                print("Enter names separated by commas:")
                name_str = input().strip()
                print("Enter phones separated by commas:")
                phone_str = input().strip()
                
                names = [n.strip() for n in name_str.split(',') if n.strip()]
                phones = [p.strip() for p in phone_str.split(',') if p.strip()]
                
                if len(names) != len(phones):
                    print("Error: Number of names and phones must be equal.")
                    continue
                if not names:
                    print("No data entered.")
                    continue

                cur.execute("""
                    CALL insert_many_contacts(%s, %s, NULL, NULL, NULL);
                """, (names, phones))
                
                conn.commit()
                print("Bulk insert completed (check server logs for invalid entries).")

            elif choose == "4":
                try:
                    limit = int(input("Enter limit (records per page): "))
                    offset = int(input("Enter offset (starting from 0): "))
                except ValueError:
                    print("Error: Limit and offset must be numbers.")
                    continue
                
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
                rows = cur.fetchall()
                
                print(f"\nContacts (limit={limit}, offset={offset}):")
                if not rows:
                    print("No contacts found.")
                else:
                    for row in rows:
                        print(f"ID: {row[0]:<3} | Name: {row[1]:<25} | Phone: {row[2]}")

            elif choose == "5":
                identifier = input("Enter name or phone to delete: ").strip()
                if not identifier:
                    print("Identifier cannot be empty.")
                    continue
                    
                cur.execute("CALL delete_contact_by_identifier(%s);", (identifier,))
                conn.commit()
                print("Delete operation completed.")

            elif choose == "6":
                running = False
                print("Goodbye!")

            else:
                print("Wrong choice. Please enter a number from 1 to 6.")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

except psycopg2.Error as e:
    print(f"Connection error: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()