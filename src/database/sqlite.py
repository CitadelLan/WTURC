import sqlite3

def connect_to_db(db_name):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        print(f"Connected to database: {db_name}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,)
    )
    return cursor.fetchone() is not None

def update_unit_br(conn, unit):
    """Update the BR values for a unit in the database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO UNIT_BR (hash_name, arcade_br, realistic_br, "
        "realistic_ground_br, simulator_br, simulator_ground_br) "
        "VALUES (?, ?, ?, ?, ?, ?);",
        (unit.hash_name, unit.arcade_br, unit.realistic_br,
         unit.realistic_ground_br, unit.simulator_br, unit.simulator_ground_br)
    )
    conn.commit()

def add_unit_localization(conn, hash_name, localization, localized_name):
    """Add a new localization table for units."""
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO UNIT_{} (hash_name, localized_name)"
                 "VALUES (?, ?)".format(localization),
                 (hash_name, localized_name))
    conn.commit()

def find_unit_hash_name(conn, localization, localized_name):
    """Find the hash name of a unit by its localized name."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT hash_name FROM UNIT_{} WHERE localized_name=?;".format(localization),
        (localized_name,)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def find_unit_localized_name(conn, hash_name, localization):
    """Find the localized name of a unit by its hash name."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT localized_name FROM UNIT_{} WHERE hash_name=?;".format(localization),
        (hash_name,)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def find_unit_br(conn, hash_name):
    """Find the BR values of a unit by its hash name."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT arcade_br, realistic_br, realistic_ground_br, "
        "simulator_br, simulator_ground_br FROM UNIT_BR WHERE hash_name=?;",
        (hash_name,)
    )
    result = cursor.fetchone()
    if result:
        return {
            'arcade_br': result[0],
            'realistic_br': result[1],
            'realistic_ground_br': result[2],
            'simulator_br': result[3],
            'simulator_ground_br': result[4]
        }
    return None