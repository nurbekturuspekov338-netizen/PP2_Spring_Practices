-- Procedure: Add phone to existing contact
CREATE OR REPLACE PROCEDURE add_phone(p_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO phones (contact_id, phone, type)
    VALUES ((SELECT id FROM phonebook WHERE name = p_name), p_phone, p_type);
END; $$;

-- Procedure: Move to group (creates group if missing)
CREATE OR REPLACE PROCEDURE move_to_group(p_name VARCHAR, p_group VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    g_id INT;
BEGIN
    INSERT INTO groups (name) VALUES (p_group) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO g_id FROM groups WHERE name = p_group;
    UPDATE phonebook SET group_id = g_id WHERE name = p_name;
END; $$;

-- Function: Multi-field search
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR, birthday DATE, grp VARCHAR, phones TEXT) 
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, c.birthday, g.name,
           STRING_AGG(ph.phone || ' (' || ph.type || ')', ', ')
    FROM phonebook c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR ph.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, g.name;
END; $$;