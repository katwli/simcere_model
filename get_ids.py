import requests
import xml.etree.ElementTree as ET
import os

def get_ids(term, article_cap=50, file_name=None):
    def clear_term(term):
        out = ""
        for i in term:
            if i != " ":
                out += i
            else:
                out += "+"

    api_key = "e8969630ebd6acc333a0a0ac6c87aa994008"
    num_articles = article_cap
    term = clear_term(term)

    # URL for the PubMed API request
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?db=pubmed&term={term}&api_key={api_key}&retmax={num_articles}"

    # Make the API request
    response = requests.get(url)
    id_list = []
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        
        # Parse the XML response
        xml_tree = ET.fromstring(response.content)
        
        # Extract and print the IDs
        for record in xml_tree.iter("record"):
            pmc_id = record.attrib.get("id")
            if pmc_id:
                id = "https://pubmed.ncbi.nlm.nih.gov/" + str(pmc_id[3:]) + "/"
                id_list.append(id)
        file = open('items.txt', 'w')
        for id in id_list:
            file.write(id+"\n")
            
        file.close()
    else:
        print("Error:", response.status_code, response.text)


    return write_txt(id_list[:num_articles], file_name)

def write_txt(data, file_name="articles_to_check.txt"):
        def make_str(data):
            out = ""
            for i in data:
                out += i
                out += ", "
            return out

        file_name = "articles_to_check.txt"
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, file_name)
        str_data = make_str(data)
        
        f = open(file_path, 'w')
        f.write(str_data)
        f.close

        print(f"TXT file '{file_name}' has been created and saved at '{file_path}'.")


get_ids('breast cancer', 5)