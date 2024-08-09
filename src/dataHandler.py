import pandas as pd
import json
import os
import yaml
from pathlib import Path

import itertools



class dataHandler:

    def WHAPI_GroupMessageTodf(fullPath):
        with open(fullPath, 'r') as file:
            data = json.load(file)
        df = pd.json_normalize(data['messages'])
        # Convert to DataFrame
        return df
    
    def create_subsets(df, column_names):

        """
        Creates subsets of the DataFrame for each distinct value in each of the specified columns.
        Drops columns that are completely NaN in each subset.
        
        Parameters:
        - df: pd.DataFrame - The DataFrame to process.
        - column_names: list of str - The list of column names to base the subsets on.
        
        Returns:
        - dict - A dictionary where keys are tuples of distinct values from the columns and values are DataFrame subsets.
        """
        if not isinstance(column_names, list):
            raise ValueError("column_names should be a list of column names.")
        
        subsets = {}
        
        for column_name in column_names:
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
            
            # Get unique values from the specified column
            unique_values = df[column_name].unique()
            
            for value in unique_values:
                # Create a subset where the column value matches the unique value
                subset = df[df[column_name] == value].copy()
                # Drop columns where all values are NaN
                subset = subset.dropna(axis=1, how='all')
                # Use a tuple of values for each column as the key
                key = (column_name, value)
                subsets[key] = subset
        
        return subsets
    
    def quality_check_and_drop(df_dict, min_rows, min_columns, check_null_percentage):
        """
        Performs quality checks on DataFrames and drops those that don't meet the criteria.
        
        Parameters:
        - df_dict: dict - A dictionary where keys are identifiers and values are DataFrames.
        - min_rows: int - Minimum number of rows required for a DataFrame to pass the check.
        - min_columns: int - Minimum number of columns required for a DataFrame to pass the check.
        - check_null_percentage: float - Maximum allowed percentage of NaN values (0-100) in any DataFrame.
        
        Returns:
        - dict - A dictionary with only the DataFrames that passed the quality checks.
        """
        # Create a new dictionary to store only the DataFrames that pass the checks
        valid_dfs = {}

        for key, df in df_dict.items():
            # Check if the DataFrame meets the minimum row and column requirements
            if df.shape[0] < min_rows or df.shape[1] < min_columns:
                print(f"Dropping {key}: does not meet row/column requirements (min_rows={min_rows}, min_columns={min_columns}).")
                continue
            

            # Calculate the percentage of NaN values
            null_percentage = df.isnull().mean().mean() * 100
            
            # Check if the DataFrame exceeds the allowed NaN percentage
            if null_percentage > check_null_percentage:
                print(f"Dropping {key}: exceeds NaN percentage threshold ({null_percentage:.2f}% > {check_null_percentage}%).")
                continue
            
            # If all checks pass, add the DataFrame to the valid_dfs dictionary
            valid_dfs[key] = df
    
        return valid_dfs
    
    def save_dfs_to_files(df_dict, folderPath_save, fileName_new, formats):
        """
        Saves each DataFrame in the dictionary to files in the specified directory in the given formats.
        
        Parameters:
        - df_dict: dict - A dictionary where keys are filenames and values are DataFrames to save.
        - directory: str - The path to the directory where files will be saved.
        - formats: list - List of file formats to save the DataFrames ('json', 'csv').
        
        Returns:
        - None
        """
        # Ensure the directory exists
        if not os.path.exists(folderPath_save):
            os.makedirs(folderPath_save)
        
        # Iterate over dictionary items and save each DataFrame in the specified formats
        for key, df in df_dict.items():
            for fmt in formats:
                # Create a filename from the key and format
                filename = f"{fileName_new}_{key[1]}.{fmt}"
                filepath = os.path.join(folderPath_save, filename)
                
                # Save DataFrame to the specified format
                if fmt == 'json':
                    df.to_json(filepath, orient='records', lines=True)
                    print(f"Saved DataFrame to {filepath}")
                elif fmt == 'csv':
                    df.to_csv(filepath, index=False)
                    print(f"Saved DataFrame to {filepath}")
                else:
                    print(f"Unsupported format: {fmt}")

    def process_and_concat_csv_files(folder_path, output_folder):
        # Initialize a dictionary to hold DataFrames grouped by the key
        csv_dict = {}

        # Get all CSV files in the folder
        for file in os.listdir(folder_path):
            if file.endswith('.csv'):
                # Extract the last part of the filename before the extension
                key = Path(file).stem.split('_')[-1]
                
                # Read the CSV file into a DataFrame
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)
                
                # Add the DataFrame to the dictionary
                if key in csv_dict:
                    csv_dict[key].append(df)
                else:
                    csv_dict[key] = [df]

        # Concatenate DataFrames and save them
        for key, df_list in csv_dict.items():
            # Concatenate all DataFrames in the list
            concatenated_df = pd.concat(df_list, ignore_index=True)
            
            # Drop duplicate rows
            concatenated_df = concatenated_df.drop_duplicates()

            # Save the concatenated DataFrame to a new CSV file
            output_file_path = os.path.join(output_folder, f"{key}_concatenated.csv")
            concatenated_df.to_csv(output_file_path, index=False)
            print(f"Saved: {output_file_path}")

    def get_csv_files(directory):
        """
        Retrieves all .csv files in the specified directory and stores them in a dictionary.
        
        Parameters:
        directory (str): The path to the directory to search for .csv files.
        
        Returns:
        dict: A dictionary with file names as keys and full paths as values.
        """
        csv_files = {}
        
        # Ensure the directory exists
        if not os.path.isdir(directory):
            raise ValueError(f"The directory {directory} does not exist.")
        
        # Iterate over all files in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                # Strip the .csv extension for the key
                key = filename[:-4]  # Remove the last 4 characters ('.csv')
                file_path = os.path.join(directory, filename)
                
                # Read the CSV file into a DataFrame
                try:
                    df = pd.read_csv(file_path)
                    csv_files[key] = df
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        return csv_files

class Anomyzer:


    def aliasGenerator():

        animals = ['Lion', 'Tiger', 'Bear', 'Wolf', 'Fox', 'Eagle', 'Shark', 'Johannes']
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Black', 'White', 'Orange']
        adjectives = ['Small', 'Medium', 'Large']
        combinations = list(itertools.product(adjectives, colors, animals))
        #df_combinations = pd.DataFrame(combinations, columns = ["col1", "col2", "col3"])
        columns = ["col1", "col2", "col3"]
        df_combinations = pd.DataFrame(combinations, columns = columns)
        #df_combinations = pd.DataFrame(combinations)
        #df_shuffled = df_combinations.sample(frac=1).reset_index(drop=True)
        df_combinations["newName"] = df_combinations["col1"] + ' ' + df_combinations["col2"] + ' ' + df_combinations["col3"]
        
        return df_combinations["newName"]
    
    def get_unique_values_from_dfs(csv_files_dict, columns_list):
        """
        Iterates over the DataFrames in the dictionary and retrieves all unique values from the specified columns.
        
        Parameters:
        csv_files_dict (dict): A dictionary with file names as keys and pandas DataFrames as values.
        columns_list (list): A list of column names to retrieve unique values from.
        
        Returns:
        dict: A dictionary where keys are column names and values are lists of unique values across all DataFrames.
        """
        unique_values = {column: set() for column in columns_list}
        
        # Iterate over each DataFrame in the dictionary
        for df in csv_files_dict.values():
            # Iterate over each specified column
            for column in columns_list:
                if column in df.columns:
                    # Update the set of unique values for the column
                    unique_values[column].update(df[column].dropna().unique())
                else:
                    print(f"Column {column} does not exist in one of the DataFrames.")
        
        # Convert sets to lists
        unique_values = {column: list(values) for column, values in unique_values.items()}
        
        return unique_values

    def createMappingTable(mapper):

        save_dataPath = mapper.get("WA_DataConcat")
        load_dataPath = mapper.get("WA_DataConcat")
        dict_toAnomyze = dataHandler.get_csv_files(directory = load_dataPath)
        columnsToAnnomyze = mapper.get("colsToAnnomyze")
        dict_uniqueValues = Anomyzer.get_unique_values_from_dfs(dict_toAnomyze, columns_list = columnsToAnnomyze)
        
        colName = "from"
        

        list_numbers = pd.Series(dict_uniqueValues[colName])
        list_alias = Anomyzer.aliasGenerator()
        list_alias = list_alias[:len(list_numbers)]



        df_1 = pd.DataFrame({
        'oldName': list_numbers,
        'newName': list_alias
        })

        return df_1
        df_1.to_csv(save_dataPath)

    def applyMapping(mapper, mapping_df, column, csv_files_dict):
        
        # Convert the mapping DataFrame to a dictionary
        mapping_dict = dict(zip(mapping_df['oldName'], mapping_df['newName']))

        # Replace the strings in the 'Category' column of the main DataFrame

         # Iterate over each DataFrame in the dictionary
        for df in csv_files_dict:
            # Iterate over each specified column
            
            csv_files_dict[df][column] = csv_files_dict[df][column].replace(mapping_dict)

        
        return csv_files_dict

    def safeAnonym(dict_aferAnon, savePath_data):

        for key in dict_aferAnon:

            filename = key.replace("concatenated", "anon")
            filename = filename + ".csv"
            filepath = os.path.join(savePath_data, filename)
            dict_aferAnon[key].to_csv(filepath, index=False)



class Mapper:
        
    def __init__(self, yaml_file):
        # Load YAML data from the provided file
        with open(yaml_file, 'r') as file:
            self.data = yaml.safe_load(file)

    def get(self, key):
        """Retrieve the value for a specific key, even in nested dictionaries."""
        return self._get_value(self.data, key)

    def _get_value(self, d, key):
        """Helper method to recursively get the value of a specific key."""
        # If the key is in the current dictionary, return its value
        if key in d:
            return d[key]
        # Otherwise, recursively search in nested dictionaries
        for k, v in d.items():
            if isinstance(v, dict):
                result = self._get_value(v, key)
                if result is not None:
                    return result
        return None

    def get_nested(self, *keys):
        """Retrieve the value for a sequence of nested keys."""
        d = self.data
        try:
            for key in keys:
                d = d[key]
            return d
        except KeyError:
            return None