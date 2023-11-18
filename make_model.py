import csv
import os

def make_array(file_name, folder_name='output'):
    def extract_data(file_path):
        dates = []
        counts = []

        with open(file_path, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if row:
                    dates.append(row[0])
                    counts.append(row[1])
        
        int_count = []
        for item in counts[1:-1]:
            int_count.append(int(item))

        return int_dates(dates[1:-1]), int_count

    def int_dates(dates):
        month_map = {
                "Jan": '01', "Feb": '02', "Mar": '03', "Apr": '04',
                "May": '05', "Jun": '06', "Jul": '07', "Aug": '08',
                "Sep": '09', "Oct": '10', "Nov": '11', "Dec": '12'
            }
        out = []
        for date in dates:
            current = date[:4] + month_map[date[-3:]]
            out.append(int(current))
        return out
            

    current_file_location = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_file_location, folder_name)
    file_path = os.path.join(folder_path, file_name)

    dates, count = extract_data(file_path)

    return dates, count

def get_all_arrays(folder_name='output'):
    current_file_location = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_file_location, folder_name)
    files = os.listdir(folder_path)

    all_arrays = {}
    for file in files:
        all_arrays[file[21:-4]] = (make_array(file, folder_name))

    return all_arrays
