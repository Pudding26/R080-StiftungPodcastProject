from dotenv import load_dotenv
import pandas as pd
import os
import itertools
load_dotenv()




from src.whatsAppWrapper import WHAPIClient
from src.dataHandler import dataHandler, Mapper, Anomyzer
from src.helper import Helper
from src.backend import WhatsappScraper, DataProcesser
from src.MemeParser import MemeParser


if __name__ == "__main__":
    
    mapper = Mapper(r"config/mapper.yaml")


    groupNames = ["MemeGroup"]
    #WhatsappScraper.initialWhatsappScrape(mapper = mapper, groupNames = groupNames)



    #DataProcesser.preprocessData(mapper = mapper)


    #DataProcesser.concatData(mapper=mapper)


    #filterForMemes = "filterForMemes"


    DataProcesser.anonIsDa(mapper=mapper)

    memeDataRaw = pd.read_csv("data/annomyzed_data/image_anon.csv")

    colsForLLM = ["id", "image.link", "from"]

    memeDataFiltered = memeDataRaw[colsForLLM]
    memeDataFiltered.rename(columns={"from": "from_name", "image.link" : "image_link"})

    meme_parser = MemeParser()

    
    with open("prompts/Memeparser.mkd", "r") as prompt_file:
        prompt_text = prompt_file.read()


    #dataText = memeDataFiltered.to_json(orient="split")

    system_prompt = "You are a well versed expert on Memes. Furthermore you are an expert on the Studienstiftung des deutschen Volkes. You are here to help me analyze the quality of the memes of the sholars of an education academy. Respond with JSON."



    GPT_Answer = meme_parser.gptPrompt_analyzeAllMemes(prompt = prompt_text, system_prompt=system_prompt, csv_file=memeDataFiltered)

    data = pd.DataFrame()
    # Extract the content from each dictionary
    for i in range(len(GPT_Answer["responses"])):

        row = []
        data_row = GPT_Answer["responses"][i]
        data_row = data_row["content"]

        row.append(data_row.caption)
        row.append(data_row.category)
        row.append(data_row.description)
        row.append(data_row.from_name)
        row.append(data_row.id)
        row.append(data_row.image_link)
        row.append(data_row.stiftiWorthy)
        row.append(data_row.stiftyRating)
        
        
        row = pd.DataFrame(row) 
        # Convert the list of content dictionaries to a DataFrame
        
        data = pd.concat([data, row])
        

        # Display the DataFrame
        print(data)


        #print(f"Messages from group {group_id} have been saved to {file_name}.")    file_name = "test.json"

        print("done")
