import requests
import xml.etree.ElementTree as ET

def get_ids(term):
    api_key = "e8969630ebd6acc333a0a0ac6c87aa994008"
    num_articles = 5
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


    return id_list[:num_articles]

print(get_ids('breast+cancer'))