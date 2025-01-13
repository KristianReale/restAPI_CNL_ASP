import streamlit as st
import requests, json

URL = "http://localhost:5000"
#URL = "https://asp2cnl.pythonanywhere.com/"

asp_input = None
cnl_output = None

def callService(service, user_input, sentence, rule): 
   user_input = user_input.replace('.', '.&')[:-1].split("&")   
   jsonS = {"user_input": user_input,"cnl": sentence,"asp": rule}      
   response = requests.post(URL + "/" + service, data=json.dumps(jsonS), headers={"Content-Type": "application/json"})
   
   if (service == "cnl2asp"):
      asp_output = st.text(response.text)
   else:
      cnl_output = st.text(response.text)

st.title('ASP2CNL')
# Forms can be declared using the 'with' syntax
#with st.form(key='my_form'):
user_input = st.text_input(label='User Input', value="A movie is identified by an id, and has a title, a director, and a year. A director is identified by a name. A topMovie is identified by an id. A scoreAssignment is identified by an id, and by a value. A waiter is identified by a name.")
asp_input = st.text_input(label='ASP Sentence', value="{topmovie(I):movie(I,_,X,_), waiter(X)} = 1 :- director(X), X != spielberg.")
cnl_output = st.text('CNL Output Sentence')
toCnlButton = st.button(label='Translate to CNL', on_click=callService("asp2cnl", user_input, "", asp_input))

