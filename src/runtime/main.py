import json
from time import sleep

from src.database.sqlite import connect_to_db, find_unit_hash_name, find_unit_br, find_unit_localized_name
from src.shared.file_paths import database_path, json_path
from src.shared.global_stats import GlobalStats
from src.shared.wt_unit import WtUnitManager, WtUnit
from wt_api import *

# Runtime main function
def main():
    # Get the current language of warthunder
    with open(json_path+'config.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(data['wt_root_dir']+"config.blk", 'r', encoding='utf-8') as f:
        # Continuously read the file until we find the line starting with "language:t="
        for line in f.readlines():
            if line.startswith("language:t="):
                lang_code = line.split('=')[1].strip()[1:-1].upper()    # Remove the surrounding quotes
                break
        print(f'Current language running in war thunder: {lang_code}')

    conn = connect_to_db(database_path+'WTURC.db')
    is_in_match = False
    unit_mgr = WtUnitManager()
    global_stats = GlobalStats()
    player_br = None
    player_unit_hash = ""
    player_unit_name = ""

    while True:
        # Receive the match state
        map_info = get_wt_map_info()
        if map_info is None:
            print("Failed to get match state, retrying...")
            continue
        else:
            is_curr_in_match = map_info['valid']
            # print(f'Is in match? {is_in_match}')
        if is_curr_in_match != is_in_match:
            is_in_match = is_curr_in_match
            if is_in_match:
                print("Match started, awaiting round to end...")
                indicators = get_wt_indicators()
                while indicators is None:
                    print("Failed to get indicators, retrying...")
                    indicators = get_wt_indicators()
                    sleep(1)
                    continue
                # Get only the string after '/' if there is one
                player_unit_hash = indicators['type'].split('/')[-1]
                while player_unit_hash == 'dummy_plane':
                    print("Failed to get player unit, retrying...")
                    indicators = get_wt_indicators()
                    if (indicators is None or 'type' not in indicators
                        or indicators['type'] is None):
                        print("Failed to get indicators, retrying...")
                        sleep(1)
                        continue
                    player_unit_hash = indicators['type'].split('/')[-1]
                    sleep(1)
                    continue
                player_br = find_unit_br(conn, player_unit_hash)
                player_unit_name = find_unit_localized_name(conn, player_unit_hash, lang_code)
                unit = WtUnit(player_unit_hash, player_br['arcade_br'], player_br['realistic_br'],
                              player_br['realistic_ground_br'], player_br['simulator_br'],
                              player_br['simulator_ground_br'])
                unit_mgr.add_player_unit(unit)
            else:
                max_br = player_br
                # Get all available units in the match
                print("Match ended, checking unit br...")
                hudmsg = get_wt_hudmsg()
                while hudmsg is None:
                    print("Failed to get hudmsg, retrying...")
                    hudmsg = get_wt_hudmsg()
                    sleep(1)
                    continue
                for dmg in hudmsg['damage']:
                    msg = dmg['msg']
                    print(msg)
                    # Extract all string encapsuled by () in dmg['msg']
                    while msg.find('(') != -1 and msg.find(')') != -1:
                        start_idx = msg.index('(')
                        end_idx = msg.index(')')
                        unit_name = msg[start_idx:end_idx+1]
                        # print(unit_name)
                        # There can be () in the unit name, so we need to find the last ')'
                        while unit_name.count('(') > unit_name.count(')'):
                            end_idx += 1
                            unit_name = msg[start_idx:end_idx+1]
                        unit_name = unit_name[1:-1]
                        print(unit_name)
                        # Search the hash name of the unit in the database
                        unit_hash = find_unit_hash_name(conn, lang_code, unit_name)
                        # print(unit_hash)
                        if unit_hash is None:
                            print(f'Warning: Unit {unit_name} not found in database, skipping...')
                            print('This can be normal as some AI units have "()" in their names')
                            msg = msg[end_idx + 1:]  # Remove the processed part of the message
                            continue
                        unit_br = find_unit_br(conn, unit_hash)
                        print(unit_br)
                        unit = WtUnit(unit_hash, unit_br['arcade_br'], unit_br['realistic_br'],
                                      unit_br['realistic_ground_br'], unit_br['simulator_br'],
                                      unit_br['simulator_ground_br'])
                        unit_mgr.add_unit(unit)
                        max_br = max(max_br, unit_br, key=lambda x: x['realistic_br'])
                        msg = msg[end_idx + 1:]  # Remove the processed part of the message
                        # print(msg)

                # Check the BR of all units in the match
                br_ofs = max_br['realistic_br'] - player_br['realistic_br']
                print('---------------------- GLOBAL BR STATUS ----------------------')
                print(f'BR offset = {br_ofs}')
                if br_ofs < 0.3:
                    unit_mgr.get_player_unit(player_unit_hash).full_downtier_cnt += 1
                    global_stats.full_downtier_cnt_rt += 1
                    print(f'Full downtier round')
                elif br_ofs < 0.7:
                    unit_mgr.get_player_unit(player_unit_hash).less_downtier_cnt += 1
                    global_stats.less_downtier_cnt_rt += 1
                    print(f'Downtier round')
                elif br_ofs < 1:
                    unit_mgr.get_player_unit(player_unit_hash).less_uptier_cnt += 1
                    global_stats.less_uptier_cnt_rt += 1
                    print(f'Uptier round')
                else:
                    unit_mgr.get_player_unit(player_unit_hash).full_uptier_cnt += 1
                    global_stats.full_uptier_cnt_rt += 1
                    print(f'Full uptier round')
                print(
                      f'Full uptier on runtime: {global_stats.full_uptier_cnt_rt} time(s)\n'
                      f'Less uptier: {global_stats.less_uptier_cnt_rt} time(s)\n'
                      f'Full downtier: {global_stats.full_downtier_cnt_rt} time(s)\n'
                      f'Less downtier: {global_stats.less_downtier_cnt_rt} time(s)'
                      )

                print('---------------------- VEHICLE BR STATUS ----------------------')
                print(f'Player unit: {player_unit_name}:\n'
                      f'Full uptier: {unit_mgr.get_player_unit(player_unit_hash).full_uptier_cnt} time(s)\n'
                      f'Less uptier: {unit_mgr.get_player_unit(player_unit_hash).less_uptier_cnt} time(s)\n'
                      f'Full downtier: {unit_mgr.get_player_unit(player_unit_hash).full_downtier_cnt} time(s)\n'
                      f'Less downtier: {unit_mgr.get_player_unit(player_unit_hash).less_downtier_cnt} time(s)'
                      )

        # Wait 1 second before the next check
        sleep(1)

main()