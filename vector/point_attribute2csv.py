from dbfread import DBF
import os
import argparse
import pandas as pd
import re
import statistics

def get_attribute_value(dbf_path, field_name):

    values = []
    try:
        table = DBF(dbf_path)
        field_values = [record[field_name] for record in table]
        return field_values
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_shp(directory):

    shp_files = []
    for root, directories, files in os.walk(directory):
        for file in files:
            if file.endswith(".dbf"):
                shp_files.append(os.path.join(root, file))

    return shp_files


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Extract an attribute related statistics.')
    parser.add_argument('input', type=str, help='Directory containing shapefiles or a single dbf file.')
    parser.add_argument('field_name', type=str, help='Field name you wanted to extract statistics.')
    parser.add_argument('csv_path', type=str, help='Output csv location.')
    args = parser.parse_args()

    all_shp = []
    if os.path.isdir(args.input):
        all_shp = get_shp(args.input)
    elif os.path.isfile(args.input) and args.input.endswith('.dbf'):
        all_shp.append(args.input)
    else:
        print("Invalid input. Please provide a valid directory or dbf file.")
        exit()

    if os.path.isfile(args.csv_path):
        print(f"{args.csv_path} will overwrite.")

    data = {}
    monthly_avg = []
    # data["Month"] = [x for x in range(1,13)]
    for shp in all_shp:
        values = get_attribute_value(shp, args.field_name)
        f_name = os.path.splitext(os.path.basename(shp))[0]
        _, year, month = re.findall(r'(CCS_1m)(\d\d\d\d)(\d\d)', shp)[0]
        
        average = statistics.mean(values)
        print(f" > {year} {month} {average}")
        monthly_avg.append(average)

        if len(monthly_avg) == 12:
            data[year] = monthly_avg
            monthly_avg = []

    
    df = pd.DataFrame(data)
    df.to_csv(args.csv_path, index=False)