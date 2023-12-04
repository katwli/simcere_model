import pandas as pd
from scipy.stats import ttest_ind
healthy_file_path = 'file path'
cancer_file_path = 'file path'
# Read the CSV file into a pandas DataFrame
healthy_data = pd.read_csv(healthy_file_path, index_col=0)  # Assuming the first column contains gene identifiers
cancer_data = pd.read_csv(cancer_file_path, index_col=0)

potential_targets = []

for gene in healthy_data.index:

    healthy_list = []
    cancer_list = []
    #iterate through all the samples in the healthy and cancerous data sets
    for col in healthy_data.columns:
        healthy_list.append(healthy_data.loc[gene, col])
    for col1 in cancer_data.columns:
        cancer_list.append(cancer_data.loc[gene, col1])

    #run statistical tests on two lists of gene expression levels 
    t_stat, p_value = ttest_ind(healthy_list, cancer_list)

    # Check if p-value is less than significance level (e.g., 0.05)
    alpha = 0.05
    if p_value < alpha:
        potential_targets.append(gene)

#save potential targets as a text file
file = open('location for file to be saved', 'w')
for item in potential_targets:
    file.write(item+', ')
file.close()
