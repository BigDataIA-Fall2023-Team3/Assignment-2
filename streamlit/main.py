import streamlit as st
import requests
import PyPDF2
import os
import subprocess
import spacy
import re
import time

import openai
openai.api_key = 'api_key'


st.title("PDF Analyzer")



# def get_answers(context, question):
#     # Separate the context and question with a line break to make it clear to the model
#     prompt = f"{context}\nQuestion: {question}\nAnswer:"

#     response = openai.Completion.create(
#         model="gpt-3.5-turbo",
#         prompt=prompt,
#         temperature=0,
#         top_p=1,
#     )

#     # Parse the response to extract the answer
#     response_text = response.choices[0].text
#     return response_text

def get_answers(context, question):
    # Separate the context and question with a line break to make it clear to the model
    prompt = f"{context}\nQuestion: {question}\nAnswer:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the response to extract the answer
    response_text = response['choices'][0]['message']['content']
    return response_text



def download_pdf(pdf_url, save_path):
    response = requests.get(pdf_url)
    with open(save_path, 'wb') as file:
        file.write(response.content)


def pypdf_extract(pdf_path):
    text = ''
    pdf_file = open(pdf_path, "rb")
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        text += page.extract_text()
    
    pdf_file.close()
    return text


def nougat_extract(pdf_path):
    path = pdf_path
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    print(pdf_name)

    with st.spinner("Processing..."):
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # Use CPU if GPU not available
        subprocess.run(['nougat', '--markdown', 'pdf', path, '--out', '.'], check=True)
        st.success("Process completed!")
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        file_contents = f'{pdf_name}.mmd'
        file = open(file_contents, 'r')
        return file.read()
 

def display(package, text_string):
    title = package
    st.markdown(f'<h3>{title}</h3>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="white-space: pre-wrap; border:1px solid #ccc; padding:10px; overflow-y:scroll; width:100%; max-height:500px;">'
        f'{text_string}'
        f'</div>', 
        unsafe_allow_html=True
    )

def display_answers(answer):
    # st.markdown(f'<h3>{title}</h3>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="white-space: pre-wrap; border:1px solid #ccc; padding:10px; overflow-y:scroll; width:100%; max-height:500px;">'
        f'{answer}'
        f'</div>', 
        unsafe_allow_html=True
    )


def summary(text):
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        sentences = list(doc.sents)
        urls = [token.text for token in doc if token.like_url]
        numbers = re.findall(r'\b\d+\b', text)
        num_numbers = len(numbers)  
        num_links = len(urls)
        num_sentences = len(sentences)
        num_words = len(doc)
        return [num_words, num_sentences, num_numbers, num_links]
    except:
        st.error("Error with summary()")
        

def disp_summary(title, l, t):
    if len(l)!=0:
        st.subheader(title)
        st.write(f"Words - {l[0]}")
        st.write(f"Sentences - {l[1]}")
        st.write(f"Number - {l[2]}")
        st.write(f"Links - {l[3]}")
        st.write(f"Execution Time - {t:.2f} seconds")


def generate_summary_text(l, t):
    summary_text = (
        f"Words - {l[0]}\n"
        f"Sentences - {l[1]}\n"
        f"Number - {l[2]}\n"
        f"Links - {l[3]}\n"
        f"Execution Time - {t:.2f} seconds"
    )
    return summary_text


def get_sentences(text):
    s = ''
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    for i in sentences:
        t = i.text
        s = s+"-->"+t.strip()+"\n"
    return s


def get_words(text):
    s = ''
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    for token in doc:
        t = token.text
        s = s+"-->"+t.strip()+"\n"
    return s



# Input for the PDF link
pdf_link = st.text_input("Enter the PDF link:")

questions = st.text_input("Enter question")

#Choose the extraction method
extractor_choice = st.selectbox(
    "Choose an extraction method:",
    ["PyPdf", "Nougat"]
)

analyze_button = st.button("Analyze")



if pdf_link and analyze_button:
    file_name = pdf_link.split("/")[-1]
    download_pdf(pdf_link, file_name)


    if extractor_choice == 'PyPdf':
        start = time.time()
        pypdf_text = pypdf_extract(file_name)
        end = time.time()
        p_exec = end - start
        display("PyPDF", pypdf_text)
        p_summary = summary(pypdf_text)
        disp_summary('PyPDF Summary', p_summary, p_exec)
        response = get_answers(pypdf_text, questions)
        display_answers(response)
        
    elif extractor_choice == 'Nougat':
        start = time.time()
        nougat_text = nougat_extract(file_name)
        end = time.time()
        n_exec = end - start
        display("Nougat", nougat_text)
        n_summary = summary(nougat_text)
        disp_summary('Nougat Summary', n_summary, n_exec)
        response = get_answers(nougat_text, questions)
        display_answers("Nougat",response)














