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

    
    #print(f"Messages from group {group_id} have been saved to {file_name}.")    file_name = "test.json"

    print("done")
