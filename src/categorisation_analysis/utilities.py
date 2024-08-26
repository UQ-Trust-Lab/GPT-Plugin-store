import pandas as pd
import numpy as np


def filter_category(file_path, category, output_file):
    df = pd.read_excel(file_path)

    filtered_data = df[df['category'] == category]
    filtered_data.to_excel(output_file, index=False)


def get_column(file_path, column_name):
    df = pd.read_excel(file_path)
    values = df[column_name].tolist()
    return (values)


def calculate_zscore(scores):
    # Calculate mean and standard deviation
    mean_group = np.mean(scores)
    std_dev_group = np.std(scores)

    # Z-score normalization
    z_scores_group = [(score - mean_group) /
                      std_dev_group for score in scores]
    return z_scores_group


def merge_excel_files(file1_path, file2_path, merge_column, source_column, output_file):
    # Read the Excel files into pandas DataFrames
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)

    # Merge the DataFrames based on the merge column
    merged_df = pd.merge(
        df1, df2[[merge_column, source_column]], on=merge_column, how='left')
    merged_df.to_excel(output_file, index=False)
