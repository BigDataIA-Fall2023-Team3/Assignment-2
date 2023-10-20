import requests
import streamlit as st

# Streamlit app to input PDF link, method, and question
st.title("API Requests")
pdf_link = st.text_input("Enter PDF Link:")
method = st.selectbox("Select Method:", ["pypdf", "nougat"])
post_button = st.button("Analyze")
question = st.text_input("Enter a Question:")
get_button = st.button("Answers")

# Function to make the API request for PDF processing
def make_pdf_api_request(pdf_url, method):
    api_url = "https://testing-assignment-2-b10953b0ae68.herokuapp.com/process_pdf"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "pdf_url": pdf_url,
        "method": method,
    }

    response = requests.post(api_url, headers=headers, json=payload)

    return response

# Function to make the API request for getting an answer
def make_question_api_request(question):
    api_url = f"https://testing-assignment-2-b10953b0ae68.herokuapp.com/get_answer?question={question}"
    headers = {
        "accept": "application/json",
    }

    response = requests.get(api_url, headers=headers)

    return response

# Handle button clicks to make the API requests
if post_button:
    if pdf_link and method:
        response = make_pdf_api_request(pdf_link, method)
        if response.status_code == 200:
            st.success("POST API Request for PDF Successful")
            st.json(response.json())
        else:
            st.error("POST API Request for PDF Failed")
            st.text(response.text)
    else:
        st.warning("Please enter PDF link and method for POST request.")

elif get_button:
    if question:
        response = make_question_api_request(question)
        if response.status_code == 200:
            st.success("GET API Request for Question Successful")
            st.json(response.json())
        else:
            st.error("GET API Request for Question Failed")
            st.text(response.text)
    else:
        st.warning("Please enter a question for GET request.")


