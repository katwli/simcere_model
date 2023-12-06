import requests
import xml.etree.ElementTree as ET
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from selenium.webdriver.common.by import By
import sys


def write_txt(data, file_name="articles_to_check.txt"):
        def make_str(data):
            out = ""
            for i in data:
                out += i
                out += ","
            return out

        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, file_name)
        str_data = make_str(data)
        
        f = open(file_path, 'w')
        f.write(str_data)
        f.close

        print(f"TXT file '{file_name}' has been created and saved at '{file_path}'.")

def get_ids(term, article_cap=500, file_name="articles_to_check.txt"):
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmax={article_cap}"
        def clean_id_list(list):
            nums = [str(i) for i in range(10)]
            out_list = []
            for i in list:
                if i[0] in nums:
                    out_list.append(i)
            return out_list[3:]
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                text_elements = [element.get_text() for element in soup.find_all(string=True)]
                text_elements = [text.strip() for text in text_elements if text.strip()]
                return write_txt(clean_id_list(text_elements), file_name)
            else:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []
        
if __name__ == '__main__':
    args = sys.argv
    if len(args) != 1:
        globals()[args[1]](*args[2:])
