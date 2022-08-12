from datetime import datetime
from os.path import exists
from pathlib import Path
from anthology import Anthology

import cleantext
import requests 
import pdftotext
import tqdm
import os

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Check if pdf exists.  If so, extract text and write to text file
    :param pdf_file_path:
    :return: extracted text filepath
    """

    if not exists(pdf_file_path):
        # No point proceeding if we don't have a pdf
        return None
    try:
        with open(pdf_file_path, "rb") as pdf_file:
            pdf = pdftotext.PDF(pdf_file)

        # Save all text to a text file
        extracted_text_file_path = f"{os.path.splitext(pdf_file_path)[0]}.txt"
        with open(extracted_text_file_path, "w") as extracted_text_file:
            extracted_text_file.write("\n\n".join(pdf))
        return extracted_text_file_path
    except Exception as e:
        log.error(f"Error from pdftotext: {e}")
        with open("logs/failed_pdf_extractions_{}.log".format(str(datetime.now())), "a") as logfile:
            logfile.write(f"Could not extract text from: {pdf_file_path} - {e}\n")
        return None

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename


anthology = Anthology(importdir='acl-anthology/data')
with open("file_list.txt","w") as o:
    o.write("link,prompt count,bias count\n")
    for id_,paper in anthology.papers.items():
        abstract = paper.get_abstract('text')
        title = paper.get_title('text')
        model_list = ["language model","BERT","GPT","contextualised word embeddings","XLM-R", "conversational","chatbot","open-domain","open domain","dialogue model"]
        bias_list = ["bias","toxic","stereotype","harm","fair"] 
        if any([model in abstract for model in model_list]):
            if any([bias in abstract for bias in bias_list]):
                try:
                    url = f"https://www.aclanthology.org/{paper.anthology_id}.pdf"
                    file = download_file(url)
                    txt = extract_text_from_pdf(file)
                    os.remove(file)
                    with open(txt,"r") as f:
                        prompt_count = 0 
                        bias_count = 0 
                        text = f.read().split("References",-1)[0]
                        prompt_list = ["prompt","probe","probing","trigger","template","completion"]
                        bias_list_l = ["bias","toxic","stereotype","harm","fair",] 
                        for prompt in prompt_list:
                            if prompt in text:
                                prompt_count +=1
                        for bias in bias_list_l:
                            if bias in text:  
                                bias_count += 1
                    if prompt_count > 1:
                        o.write(f"https://www.aclanthology.org/{paper.anthology_id}.pdf,{prompt_count},{bias_count}\n")
                        o.flush()
                    os.remove(txt)
                except:
                    print(paper.anthology_id)
                    
