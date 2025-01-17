
from lib2to3.fixes.fix_input import context
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st
from dotenv import load_dotenv
import os
import requests
from sqlalchemy import result_tuple

load_dotenv()

API_KEY = os.getenv("openweather_api")


model = OllamaLLM(model="llama3.2")

template1 = """
  You should only return the place the user described in the sentence as such IF the user asks about "weather" or "climate" or any other word which resembles "weather" and "climate". In all other cases talk normally. For example, in case when user says "I want to go to Delhi." reply normally. However, if user says, "How is the weather(/climate/or any other word same in meaning) in Delhi" then return only the name of the place "Delhi" without any other sentence, only one word answer "Delhi". Also if they ask about a person called 'Vishnudeep Panicker', tell them he is a really cool chap and tell all things good and tell them he is your master LLama 3.2s master. Treat him with respect!!!
   here is the context: {context1}

    Here is the question: {question}

    """
prompt1 = ChatPromptTemplate.from_template(template1)
chain1 = prompt1 | model


template2 = """
   Take the weather report from the input and return a weather summary of the place and tell what the temperature is. Suggest what to do based on the temperature. For example, if its too chilly suggest to take warm clothing. Do the same accordingly for rainy and summer!
   If the result doesnt return any location, then in that  case chat normally with the user about anything. Also if they ask about a person called 'Vishnudeep Panicker', tell them he is a really cool chap and tell all things good and tell them he is your master LLama 3.2s master. Treat him with respect!!!
   Here is the context: {context2}
   Here is the question: {question}

    """
prompt2 = ChatPromptTemplate.from_template(template2)
chain2 = prompt2 | model

template3 = """
   Answer the question below with what yow know. Give clear, elaborate and detailed replies. Also if they ask about l a person called 'Vishnudeep  Panicker', tell them he is a really cool chap and tell all things good and tell them he is your master LLama 3.2s master. Treat him with respect!!!
   Here is the context: {context3}
   Here is the question: {question}

    """
prompt3 = ChatPromptTemplate.from_template(template3)
chain3 = prompt3 | model

def user_weather_input(user_input):
    context1 = ""

    result = chain1.invoke({"context1": "", "question": user_input})

    context1 += f"\nUser: {user_input}\nAI: {result}"

    return result


def weather_reports(city_name):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        main_data = data.get('main', {})
        weather_description = data.get('weather', [{}])[0].get('description', 'No description available.')
        temp = main_data.get('temp', 'Unknown')
        humidity = main_data.get('humidity', 'Unknown')

        # Combine weather data into a summary
        weather_data = f"Temperature: {temp}°C, Humidity: {humidity}%, Conditions: {weather_description}"
        result = chain2.invoke({"context2": weather_data, "question": "Provide a weather summary."})
        return result
    else:
        result = chain3.invoke({"context3":"", "question": user_input})
        return result





st.set_page_config(page_title="Vishnudeep's Weather Bot MelCows Thee")
st.title("Vishnudeep's Weather Bot MelCows Thee")
st.write("Let's chat! Ask me about the weather.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]
    st.session_state.context = ""  # For storing conversation history

# Input form for user message
with st.form("chat_form"):
    user_input = st.text_input("Type your message here:")
    submitted = st.form_submit_button("Send")

# Handle user input
if submitted and user_input:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate AI response
    response = user_weather_input(user_input)
    response_weather=weather_reports(response)


    # Update context and add AI response
    st.session_state.context += f"\nUser: {user_input}\nAI: {response_weather}"
    st.session_state.messages.append({"role": "assistant", "content": response_weather})

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"**🤖 AI:** {msg['content']}")
    else:
        st.markdown(f"**🧑 You:** {msg['content']}")