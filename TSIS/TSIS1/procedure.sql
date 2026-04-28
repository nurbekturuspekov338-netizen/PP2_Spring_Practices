DROP FUNCTION IF EXISTS search_contacts(TEXT);
DROP FUNCTION IF EXISTS get_contacts_paginated(INT, INT);

DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR);
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Contact not found';
        RETURN;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INT;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE name = p_contact_name;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR,
    phone_type VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.surname,
        c.email,
        c.birthday,
        g.name AS group_name,
        p.phone,
        p.type AS phone_type
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE
        c.name ILIKE '%' || p_query || '%'
        OR c.surname ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%'
        OR g.name ILIKE '%' || p_query || '%';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INT,
    p_offset INT
)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.surname,
        c.email,
        c.birthday,
        g.name AS group_name
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;