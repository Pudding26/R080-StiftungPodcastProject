import os
import json
import base64
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from pydantic import BaseModel
from src.dataHandler import dataHandler, Mapper
from PIL import Image
import io
import re
import pandas as pd

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)



class MemeTrainer:
    
    def __init__(self, api_key: str):
        load_dotenv()
        self.client = OpenAI(api_key=api_key)


    def loadMemeDf(mapper):
        path = mapper.get("MemeDataRaw")









class MemeParser:

    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))




    def encode_image(self, image_path: str) -> str:
        """Encodes an image file to a Base64 string."""
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_image

    def load_json_template(self, json_path: str) -> dict:
        """Loads and parses a JSON template from a file."""
        with open(json_path, "r") as json_file:
            json_data = json.load(json_file)
        return json_data


    def MemeParser_TranslateMemeInJson(self, prompt: str, image_url: str, csv_file, context_json: dict) -> dict:
        """Sends a message to GPT and returns the response JSON."""
        # Prepare the messages for the GPT-4 model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type":"text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{image_url}",
                            "detail": "auto"
                        },
                    },
                    {
                        "type":"text",
                        "text": f"Here is the csv file: {csv_file}",
                    },
                ],
            }
        ],
    )
        # Extract the JSON content from the GPT response
        gpt_response = response.choices[0].message.content
        return gpt_response

    
    def gptPrompt_analyzeAllMemes(self, system_prompt, prompt, csv_file):

        class Output_1(BaseModel):
            
            id: str
            #reactions: str
            image_link: str
            from_name: str
            description: str
            category: str
            stiftiWorthy: str

        #class Output_2(BaseModel):

        # Initialize a list to store the parsed GPT responses
        parsed_responses = []

        # Iterate through each row in the DataFrame
        for index, row in csv_file.iterrows():
            # Convert the row to a dictionary to use in the prompt
            row_data = row.to_dict()
            
            # Construct the row-specific prompt (if needed)
            #row_prompt = prompt.format(**row_data)  # Adjust based on your prompt needs
            
            # Prepare the messages for the GPT-4 model
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": f"Here is the CSV data for this row: {row_data}"}
                ],
                max_tokens=500,
                response_format=Output_1
            )   
            
            # Extract the JSON content from the GPT response
            gpt_response = completion.choices[0].message
            if gpt_response.refusal:
                # Handle refusal
                print(f"Refusal for row {index}: {gpt_response.refusal}")
                parsed_responses.append({"row": index, "response": "Refusal", "content": gpt_response.refusal})
            else:
                parsed_responses.append({"row": index, "response": "Parsed", "content": gpt_response.parsed})
                print(f"Parsed response for row {index}: {gpt_response.parsed}")
        
        # Combine the results and return as a dictionary
        return {
            "responses": parsed_responses
        }


    def process_csv_with_gpt(csv_file_path, output_csv_file, prompt_template, system_prompt):
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_path)
        
        # Initialize a list to store GPT responses
        gpt_responses = []
        
        # Loop through each row in the DataFrame
        for index, row in df.iterrows():
            # Convert the row to a dictionary or format as needed
            row_data = row.to_dict()
            
            # Construct the prompt using the row data and the prompt template
            prompt = prompt_template.format(**row_data)
            
            # Send the data to the OpenAI API with a system prompt
            response = openai.Completion.create(
                engine="text-davinci-003",  # or any other model you are using
                prompt=f"{system_prompt}\n\n{prompt}",
                max_tokens=150
            )
            
            # Extract the text response and add it to the list
            gpt_responses.append(response['choices'][0]['text'].strip())
        
        # Add the GPT responses as a new column in the DataFrame
        df['GPT_Responses'] = gpt_responses
        
        # Save the updated DataFrame to a new CSV file
        df.to_csv(output_csv_file, index=False)
        
        print(f"Processed CSV saved as {output_csv_file}")


    def extract_json_from_string(json_string):
        """
        Extract JSON content from a string containing code blocks.

        Args:
            json_string (str): The string containing JSON data inside code blocks.

        Returns:
            dict: The extracted JSON data as a dictionary.
        """
        # Use regular expression to find the JSON content within code blocks
        match = re.search(r'```json\n(.*?)\n```', json_string, re.DOTALL)
        if match:
            json_content = match.group(1)
            return json.loads(json_content)  # Convert JSON string to dictionary
        else:
            raise ValueError("No JSON content found in the string.")

    def save_json_to_file(data, file_path):
        """
        Save JSON data to a file.

        Args:
            data (dict): The JSON data to save.
            file_path (str): The path of the file to save the JSON data to.
        """
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)  # Write JSON data to file with indentation
            print(f"File saved successfully to {file_path}")
        except IOError as e:
            print(f"An error occurred while writing the file: {e}")


# Usage example
if __name__ == "__main__":
    # Initialize the MemeParser with your API key
    meme_parser = MemeParser(api_key=os.environ.get("OPENAI_API_KEY"))
    # Encode the image
    image_url = "https://s3.eu-central-1.wasabisys.com/in-files/4917660378568/jpeg-e00aff6423ccafb65d-92cc01ab9dcd62cf5e07-728039f909.jpeg"
    # Load the JSON template
    json_template = meme_parser.load_json_template("prompts/templates/MemeParserOutput.json")

    # Load the prompt from a file or define it directly
    with open("prompts/Memeparser.mkd", "r") as prompt_file:
        prompt_text = prompt_file.read()

    # Send the message to GPT and get the response JSON
    gpt_json_response = meme_parser.MemeParser_TranslateMemeInJson(prompt=prompt_text, image_url=image_url, json_template=json_template, context_json = json_template)
    json_file =  MemeParser.extract_json_from_string(gpt_json_response)
    # Print the GPT JSON response
    print(gpt_json_response)
    print("a")

