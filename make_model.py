import csv
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from selenium.webdriver.common.by import By
from selenium import webdriver
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures

driver = webdriver.Chrome()

def make_array(PMID, file_name, folder_name='output'):
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

        return dates[1:-1], int_count
            

    current_file_location = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_file_location, folder_name)
    file_path = os.path.join(folder_path, file_name)

    dates, count = extract_data(file_path)

    date_stuff = fix_dates(PMID, dates)

    new_count = []
    sum = 0
    for i in count:
        sum += i
        new_count.append(sum)

    return (date_stuff[0], new_count, date_stuff[1])

def fix_dates(PMID, dates):
    searcher = "https://pubmed.ncbi.nlm.nih.gov/"
    try:
        driver.get(searcher + PMID + "/")
        date_ele = driver.find_element(By.CLASS_NAME, "cit").text
        if date_ele[4] == " ":
            pub_date = date_ele[:8]
        try:
            second_date = driver.find_element(By.CLASS_NAME, "secondary-date").text
            if second_date[0] == "E":
                pub_date = second_date[5:13]
        except:
            pub_date = date_ele[:4] + " Jan"
    except:
        pass

    month_map = {
                "Jan": '01', "Feb": '02', "Mar": '03', "Apr": '04',
                "May": '05', "Jun": '06', "Jul": '07', "Aug": '08',
                "Sep": '09', "Oct": '10', "Nov": '11', "Dec": '12'
            }
    
    pub_year = int(pub_date[:4])
    pub_month = int(month_map[pub_date[-3:]])

    fix_dates = []
    for item in dates:
        year = int(item[:4])
        month = int(month_map[item[-3:]])
        new_date = 12*(year - pub_year) + (month - pub_month)
        fix_dates.append(new_date)
    
    now = 12*(2023 - pub_year) + (12 - pub_month)

    return (fix_dates, now)

def get_all_arrays(folder_name='output'):
    current_file_location = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_file_location, folder_name)
    files = os.listdir(folder_path)

    all_arrays = {}
    for file in files:
        all_arrays[file[21:-4]] = make_array(file[21:-4], file, folder_name)

    return all_arrays

def model(data, PMID):
    dates = [[i] for i in data[0]]
    X = np.array([[0]] + dates)
    Y = np.array([0] + data[1])

    now = data[2]

    poly_features = PolynomialFeatures(4)
    X_poly = poly_features.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, Y)

    X_plot = np.arange(0, now, 1).reshape(-1, 1)
    X_plot_poly = poly_features.transform(X_plot)
    y_plot_pred = model.predict(X_plot_poly)

    plt.scatter(X, Y, color='black', label='Actual')
    plt.plot(X_plot, y_plot_pred, label=f'Polynomial Regression (Degree {4})', color='red')
    plt.xlabel('X (Months since publication)')
    plt.ylabel('y (Articles citing)')
    plt.title('Regression for ' + PMID)
    plt.legend()
    plt.show() 

def reg_all(data_dict=None):
    if data_dict is None:
        data_dict = get_all_arrays()
    for i in data_dict:
        if data_dict[i][0] == []:
            print(i, "has no citations")
        else:
            model(data_dict[i], i)


def plt_all(data_dict=None):
    if data_dict is None:
        data_dict = get_all_arrays()
    datasets = []
    for i in data_dict:
        datasets.append((data_dict[i][0], data_dict[i][1]))


    for i in data_dict:
        plt.scatter(data_dict[i][0], data_dict[i][1], label=i)
    plt.xlabel('X (Months since Publication)')
    plt.ylabel('y (Times Cited)')
    plt.legend()
    plt.show() 


if __name__ == '__main__':
    args = sys.argv
    if len(args) != 1:
        globals()[args[1]](*args[2:])

