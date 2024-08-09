from src.whatsAppWrapper import WHAPIClient
from src.dataHandler import dataHandler, Mapper, Anomyzer
from src.helper import Helper





class WhatsappScraper:

    def initialWhatsappScrape( mapper, groupNames):

        for groupName in groupNames:

            #client = WHAPIClient(WHAPI_token)
            client = WHAPIClient()
            groupID = mapper.get(key = groupName)
            path= mapper.get(key = "WA_importPath")
            filename = groupName + "_import.json"
            file_name = Helper.create_path(directory= path, filename= filename)
            client.save_messages_to_file(group_id = groupID, file_name = file_name)


class DataProcesser:

    def preprocessData (mapper):
        folderPath_load = mapper.get("WA_importPath")
        folderPath_save = mapper.get("WA_DataProcessed")
        
        filesToProcess = Helper.get_all_files_in_folder(folder_path = folderPath_load)
        colsForSubsets = ["type"]
        
        
        
        for fileName in filesToProcess:
            
            fullPath_load = Helper.create_path(directory=folderPath_load, filename=fileName)

            data_out = dataHandler.WHAPI_GroupMessageTodf(fullPath= fullPath_load)

            dict_subDfs = dataHandler.create_subsets(column_names=colsForSubsets, df=data_out)
            dict_subDfs = dataHandler.quality_check_and_drop(df_dict = dict_subDfs, min_rows = 1, min_columns = 1, check_null_percentage = 100)

            fileName_new = fileName.replace("import", "raw").split(".")[0]
            # Save DataFrames to JSON files
            dataHandler.save_dfs_to_files(df_dict = dict_subDfs, folderPath_save = folderPath_save, fileName_new = fileName_new, formats=['csv'])

    def concatData (mapper):

        folderPath_load = mapper.get("WA_DataProcessed")
        folderPath_save = mapper.get("WA_DataConcat")
    
    
        dataHandler.process_and_concat_csv_files(folderPath_load, folderPath_save)
    

    def anonIsDa (mapper):

        mapping_df = Anomyzer.createMappingTable(mapper)

        colName = "from"
        load_data = mapper.get("WA_DataConcat")
        savePath_data = mapper.get("DataAnonymized")
        
        dict_forAnon = dataHandler.get_csv_files(load_data)
        dict_aferAnon = Anomyzer.applyMapping(mapper = mapper, mapping_df = mapping_df, column = colName, csv_files_dict = dict_forAnon)

        Anomyzer.safeAnonym(dict_aferAnon, savePath_data)
    




