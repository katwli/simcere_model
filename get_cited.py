from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
import sys
import csv
import os

driver = webdriver.Chrome()

def get_referenced_by(input, out_type='date_ID_list', make_csv='False'):
    """
    Takes a Pubmed url (ex: 'https://pubmed.ncbi.nlm.nih.gov/33705880/'), or just the PMid (ex: '33705880') and returns a specified output type.
    Output types are:
    'count': returns an int of how many other articles referenced the given article
    'PMid': returns a list of PMid's of other articles that referenced the given article
    'dates': returns a sorted list of publication dates (month/year) of other articles that referenced the given article
    'titles': returns a list of titles of other articles that referenced the given article
    'date_title_list': returns a list of tuples (date, [titles]) sorted chronologically of other articles that referenced the given article
    'date_ID_list': returns a list of tuples (date, [Ids]) sorted chronologically of other articles that referenced the given article
    """
    try:
        int(input)
        PMID = input
    except:
        PMID = None
        url = input

    if out_type not in ['count', 'PMid', 'dates', 'titles', 'date_title_list', 'date_ID_list']:
        print("Invalid output type. Valid output types include 'count', 'PMid', 'dates', 'titles', 'date_title_list', 'date_ID_list'.")
        return None
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id="
    
    def get_PMID(url):
        PMID = ""
        num_check = 0
        for i in url:
            if i == "/":
                num_check += 1
            elif num_check == 3:
                PMID += i
        return PMID
    if PMID == None:
        PMID = get_PMID(url)
    resource_url = base_url + PMID
    
    def get_text_elements_from_website(url, PMID):
        def clean_id_list(list, PMID):
            nums = [str(i) for i in range(10)]
            out_list = []
            for i in list:
                if i != PMID:
                    if i[0] in nums:
                        out_list.append(i)
            return out_list
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                text_elements = [element.get_text() for element in soup.find_all(string=True)]
                text_elements = [text.strip() for text in text_elements if text.strip()]
                return clean_id_list(text_elements, PMID)
            else:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []
        
    id_list = get_text_elements_from_website(resource_url, PMID)
    if out_type == 'count':
        return len(id_list)
    elif out_type == 'PMid':
        return id_list
    if id_list == []:
        if make_csv == "False":
            return []
    
    searcher = "https://pubmed.ncbi.nlm.nih.gov/"

    def get_dates(id_list):
        def custom_date_sort(date_string):
            year = date_string[:4]
            month_abbrev = date_string[5:]
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
            }
            return (int(year), month_map[month_abbrev])
        
        date_strings = []
        for PMid in id_list:
            try:
                driver.get(searcher + PMid + "/")
                citation = driver.find_element(By.CLASS_NAME, "cit").text
                if citation[4] == " ":
                    citation_date = citation[:8]
                else:
                    try:
                        second_date = driver.find_element(By.CLASS_NAME, "secondary-date").text
                        if second_date[0] == "E":
                            citation_date = second_date[5:13]
                    except:
                        citation_date = citation[:4] = " Jan"
                date_strings.append(citation_date)
            except:
                pass

        return sorted(date_strings, key=custom_date_sort)

    def get_titles(id_list):
        title_strings = []
        for PMid in id_list:
            driver.get(searcher + PMid + "/")
            title_strings.append(driver.find_element(By.CLASS_NAME, "heading-title").text)
        return title_strings

    def get_date_title(id_list):
        def custom_date_sort(date_string):
            year = date_string[:4]
            month_abbrev = date_string[5:]
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
            }
            return (int(year), month_map[month_abbrev])
        
        if id_list == []:
            return []
    
        date_dict = {}
        for PMid in id_list:
            try:
                driver.get(searcher + PMid + "/")
                citation = driver.find_element(By.CLASS_NAME, "cit").text
                if citation[4] == " ":
                    citation_date = citation[:8]
                else:
                    try:
                        second_date = driver.find_element(By.CLASS_NAME, "secondary-date").text
                        if second_date[0] == "E":
                            citation_date = second_date[5:13]
                    except:
                        citation_date = citation[:4] + " Jan"
                title = driver.find_element(By.CLASS_NAME, "heading-title").text
                if citation_date in date_dict:
                    date_dict[citation_date].append(title)
                else:
                    date_dict[citation_date] = [title]
            except:
                pass
        
        date_strings = list(date_dict.keys())
        sorted_dates = sorted(date_strings, key=custom_date_sort)
        sorted_date_title_list = [(date, date_dict[date]) for date in sorted_dates]

        return sorted_date_title_list
    
    def get_date_ID(id_list):
        def custom_date_sort(date_string):
            year = date_string[:4]
            month_abbrev = date_string[5:]
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
            }
            return (int(year), month_map[month_abbrev])
        
        if id_list == []:
            return []
    
        date_dict = {}
        for PMid in id_list:
            try:
                driver.get(searcher + PMid + "/")
                citation = driver.find_element(By.CLASS_NAME, "cit").text
                if citation[4] == " ":
                    citation_date = citation[:8]
                else:
                    try:
                        second_date = driver.find_element(By.CLASS_NAME, "secondary-date").text
                        if second_date[0] == "E":
                            citation_date = second_date[5:13]
                    except:
                        citation_date = citation[:4] + " Jan"
                if citation_date in date_dict:
                    date_dict[citation_date].append(PMid)
                else:
                    date_dict[citation_date] = [PMid]
            except:
                pass
        
        date_strings = list(date_dict.keys())
        sorted_dates = sorted(date_strings, key=custom_date_sort)
        sorted_date_ID_list = [(date, date_dict[date]) for date in sorted_dates]

        return sorted_date_ID_list
    
    def write_csv(data, PMID):
        file_name = "articles_referencing_" + PMID + ".csv"
        script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = "output"
        output_folder_path = os.path.join(script_directory, folder_name)
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
            print(f"Created the '{folder_name}' folder at {output_folder_path}")
        file_path = os.path.join(output_folder_path, file_name)

        total_count = 0

        with open(file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Date", "Count", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles", "Articles"])

            for item in data:
                date_str = item[0]
                count = len(item[1])
                total_count += count
                title_list = item[1]

                row = [date_str, str(count)] + title_list
                csv_writer.writerow(row)

            csv_writer.writerow([])
            csv_writer.writerow(['Total count', str(total_count)])
        
        print(f"CSV file '{file_name}' has been created and saved at '{file_path}'.")
    
    if out_type == 'dates':
        return get_dates(id_list)
    elif out_type == 'titles':
        return get_titles(id_list)
    elif out_type == 'date_title_list':
        if make_csv == 'True':
            write_csv(get_date_title(id_list), PMID)
        else:
            return get_date_title(id_list)
    elif out_type == 'date_ID_list':
        if make_csv == 'True':
            write_csv(get_date_ID(id_list), PMID)
        else:
            return get_date_ID(id_list)
    
def printer(input, input2='date_ID_list', input3='False'):
    print(get_referenced_by(input, input2, input3))    

def get_mult(input_file='articles_to_check.txt', out_type='date_ID_list', make_csv='True'):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, input_file)
    if input_file[-4:] != ".txt":
        print("Please provide a file of type .txt")
        return None
    elif not os.path.exists(file_path):
        print("File does not exist")
        return None
    
    def read_inputs_from_file(file_path):
        inputs = []

        with open(file_path, 'r') as file:
            file_text = ''
            for line in file:
                clean_line = line.strip()
                file_text += clean_line
            file_text += ","
            
            current_item = ''
            for i in file_text:
                if i != ',':
                    current_item += i
                else:
                    if current_item != '':
                        if current_item not in inputs:
                            inputs.append(current_item)
                            current_item = '' 
        return inputs

    inputs = read_inputs_from_file(file_path)
    if inputs != []:
        for input in inputs:
            try:
                int(input)
                url = "https://pubmed.ncbi.nlm.nih.gov/" + input + "/"
            except:
                url = input
            driver.get(url)
            error_title = driver.find_element(By.CLASS_NAME, "title").text
            if error_title == "":
                get_referenced_by(input, out_type, make_csv)
    else:
        print("No inputs")

if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 2:
        globals()[args[1]](*args[2:])

