from fastapi import FastAPI, HTTPException
import requests
import PyPDF2
import tempfile
import os
import subprocess
import openai


app = FastAPI()

def download_pdf(pdf_url, file_name):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(file_name, "wb") as pdf_file:
            pdf_file.write(response.content)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to download PDF: {e}")
    

def nougat_extract(file_name):
    try:
        pdf_name = os.path.splitext(os.path.basename(file_name))[0]
        print(pdf_name)
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # Use CPU if GPU not available
        subprocess.run(['nougat', '--markdown', 'pdf', file_name, '--out', '.'], check=True)
        
        file_contents = f'{pdf_name}.mmd'
        with open(file_contents, 'r') as file:
            return file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF using Nougat: {e}")
    


def pypdf_extract(file_name):
    try:
        text = ''
        with open(file_name, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_number in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_number]
                text += page.extract_text()
        return text
    except PyPDF2.utils.PdfReadError as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")
    
    
def get_questions(context):
    try:
        response = openai.Completion.create(
            engine="davinci-instruct-beta-v3",
            prompt=f"Write questions based on the text below\n\nText: {context}\n\nQuestions:\n1.",
            temperature=0,
            max_tokens=257,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"]
        )
        return response['choices'][0]['text']
    except:
        return ""
    

@app.post("/process_pdf/")
async def process_pdf(pdf_url: str, method: str = "pypdf"):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_pdf_file:
            temp_file_name = temp_pdf_file.name
        download_pdf(pdf_url, temp_file_name)
        
        if method == "pypdf":
            extracted_text = pypdf_extract(temp_file_name)
        elif method == "nougat":
            extracted_text = nougat_extract(temp_file_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid extraction method. Use 'pypdf' or 'nougat'.")
        
        return {"extracted_text": extracted_text}
    finally:
        if temp_file_name:
            try:
                os.remove(temp_file_name)
            except Exception as e:
                pass