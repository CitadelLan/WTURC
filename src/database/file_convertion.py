# Convertion on original unit.csv
import csv
import re

import pandas as pd
from pathlib import Path
from styleframe import StyleFrame, Styler, utils
from src.shared.file_paths import convertion_path

# Convert the unit name into the same as the _shop one
def convert_unit_csv(path):
    print(f'Converting units.csv to unify localization names in {convertion_path}...')
    convertion_data = []

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')  # 使用分号作为分隔符

        header = next(reader)
        new_line = []

        for i in range(0, len(header)):
            new_line.append(header[i])
        convertion_data.append(new_line)

        # Convert the unit name localizations into the same as the _0 one
        full_localizations = []
        unit_hash_name = ""
        for row in reader:
            new_line = []
            hash_name = row[0]
            new_line.append(hash_name)
            if hash_name.endswith("_0"):
                full_localizations = []
                unit_hash_name = hash_name[:-2]
                for i in range(1, len(row)):
                    new_line.append(row[i])
                    full_localizations.append(row[i])
            elif (hash_name.endswith("_1") or hash_name.endswith("_2")) and hash_name[:-2] == unit_hash_name:
                for i in range(1, len(row)):
                    new_line.append(full_localizations[i - 1])
            else:
                for i in range(1, len(row)):
                    new_line.append(row[i])
            convertion_data.append(new_line)

    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(convertion_data)




# Simplify unit.csv into only hash names
def export_simplified_unit_csv(path):
    simplified_data = []

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')  # 使用分号作为分隔符

        # Read the header to find all available languages in the localization file
        header = next(reader)
        new_line = [header[0]]
        for i in range(1, len(header)):
            new_line.append(header[i][1:-1].upper())  # Only keep the part between < and >
        simplified_data.append(new_line)

        # Removing all lines without "_shop" postfix in the first cell
        for row in reader:
            new_line = []
            hash_name = row[0]
            if hash_name.endswith("_shop"):
                new_line.append(hash_name.split("_shop")[0])  # Only keep the part before "_shop"
                for i in range(1, len(row)):
                    new_line.append(row[i])
                simplified_data.append(new_line)

    export_path = Path(convertion_path)
    if not export_path.exists():
        export_path.mkdir(parents=True, exist_ok=True)

    # Write the simplified CSV file
    with open(convertion_path+'units_simplified.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(simplified_data)

    print("Exported units_simplified.csv to " + str(convertion_path+'units_simplified.csv'))

    return

def export_pretty_unit_xlsx():
    csv = pd.read_csv(convertion_path+'units_simplified.csv', encoding='utf-8')

    style = Styler(shrink_to_fit=True)
    sf = StyleFrame(csv, styler_obj=style)
    sf.set_column_width_dict({col.value: 16 for col in sf.columns})
    header_style = Styler(
        bg_color="#2785bc",
        bold=True,
        font_size=12,
        horizontal_alignment=utils.horizontal_alignments.center,
        vertical_alignment=utils.vertical_alignments.center,
    )
    content_style = Styler(
        shrink_to_fit=True,
        font_size=8,
        horizontal_alignment=utils.horizontal_alignments.left,
    )
    sf.apply_column_style(sf.columns, content_style)
    sf.apply_headers_style(header_style)
    row_style = Styler(
        bg_color="#87bbda",
        shrink_to_fit=True,
        font_size=8,
        horizontal_alignment=utils.horizontal_alignments.left,
    )
    # 计算要设置背景色的行索引
    indexes = list(range(1, len(sf), 2))
    sf.apply_style_by_indexes(indexes, styler_obj=row_style)

    writer = sf.to_excel(convertion_path+'units_beautified.xlsx')
    writer.close()

    print("Exported units_beautified.xlsx to " + str(convertion_path+'units_beautified.xlsx'))

    return