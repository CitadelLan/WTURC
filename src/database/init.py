from file_convertion import *
from src.database.sqlite import *
import requests
import json
from src.shared.file_paths import json_path, database_path
from src.shared.wt_unit import WtUnit

available_localizations = []

def generate_from_unit_csv():
    with open(json_path+'config.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    convert_unit_csv(data['wt_root_dir']+"lang\\units.csv")
    export_simplified_unit_csv(data['wt_root_dir']+"lang\\units.csv")
    export_pretty_unit_xlsx()

def establish_localization_db(conn):
    print("Checking localization database...")
    with open(convertion_path + 'units_simplified.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        header = next(reader)
        for i in range(1, len(header) - 2):  # omit comment & max_chars
            available_localizations.append(header[i])
            # Create table for each localization if it does not exist
            if not table_exists(conn, 'UNIT_' + header[i]):
                print(f"Table {header[i]} does not exist, creating UNIT_{header[i]}.")
                conn.execute("CREATE TABLE UNIT_{} ("
                             "hash_name TEXT PRIMARY KEY,"
                             "localized_name TEXT)".format(header[i]))

        # Create UNIT_BR table if it does not exist
        if not table_exists(conn, 'UNIT_BR'):
            print(f"Table UNIT_BR does not exist, creating UNIT_BR.")
            conn.execute("CREATE TABLE UNIT_BR ("
                         "hash_name TEXT PRIMARY KEY,"
                         "arcade_br REAL,"
                         "realistic_br REAL,"
                         "realistic_ground_br REAL,"
                         "simulator_br REAL,"
                         "simulator_ground_br REAL)".format(header[i]))

        for line in reader:
            hash_name = line[0]

            for i in range(1, min(len(line), len(available_localizations))):
                # Insert data into the table for each localization(if not exists)
                localized_name = line[i]
                localization = available_localizations[i - 1]
                conn.execute("INSERT OR IGNORE INTO UNIT_{} (hash_name, localized_name)"
                             "VALUES (?, ?)".format(localization),
                             (hash_name, localized_name))
    # conn.commit()

def get_all_units_br(conn):
    print("Checking all units br...")
    page_idx = 0
    while True:
        try:
            url = f"https://www.wtvehiclesapi.sgambe.serv00.net/api/vehicles?page={page_idx}"
            rsp = requests.get(url)
            if rsp.status_code == 200:
                data = rsp.json()
                if not data:
                    print("No more units found, finishing br search.")
                    break
                for unit in data:
                    hash_name = unit['identifier']
                    arcade_br = unit.get('arcade_br', None)
                    realistic_br = unit.get('realistic_br', None)
                    realistic_ground_br = unit.get('realistic_ground_br', None)
                    simulator_br = unit.get('simulator_br', None)
                    simulator_ground_br = unit.get('simulator_ground_br', None)
                    unit = WtUnit(hash_name, arcade_br, realistic_br, realistic_ground_br,
                                  simulator_br, simulator_ground_br)

                    # Insert or update the br values in the database
                    update_unit_br(conn, unit)
                # conn.commit()
                print(f"Processed page {page_idx}")
                page_idx += 1
            else:
                print(f"Failed to fetch data: {rsp.status_code}")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break


def init():
    dp = Path(database_path)
    if not dp.exists():
        dp.mkdir(parents=True, exist_ok=True)
    conn = connect_to_db(database_path+"WTURC.db")
    if conn is not None:
        establish_localization_db(conn)
        get_all_units_br(conn)
        print("Database initialized successfully.")
    else:
        print("Failed to initialize the database.")
        return

# generate_from_unit_csv()
init()