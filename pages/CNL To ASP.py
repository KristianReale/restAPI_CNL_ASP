import streamlit as st
import requests, json

#URL = "http://localhost:5000"
URL = "https://asp2cnl.pythonanywhere.com/asp2cnl/"

asp_input = None
cnl_output = None

def callService(service, user_input, sentence, rule): 
   user_input = user_input.replace('.', '.&')[:-1].split("&")   
   print(user_input)
   print(rule)
   jsonS = {"user_input": user_input,"cnl": sentence,"asp": rule}      
   response = requests.post(URL + "/" + service, data=json.dumps(jsonS), headers={"Content-Type": "application/json"})
   
   if (service == "cnl2asp"):
      asp_output = st.text(response.text)
   else:
      cnl_output = st.text(response.text)

st.title('CNL2ASP')
# Forms can be declared using the 'with' syntax
#with st.form(key='my_form'):
user_input = st.text_input(label='User Input', value="A movie is identified by an id, and has a title, a director, and a year. A director is identified by a name. A topMovie is identified by an id. A scoreAssignment is identified by an id, and by a value. A waiter is identified by a name.")
cnl_input = st.text_input(label='Cnl Sentence', value="Whenever there is a director with name X different from spielberg then we can have at most 1 topmovie with id I such that there is a movie with director X, and with id I.")
asp_output = st.text('ASP Output Rule')
toAspButton = st.button(label='Translate to ASP', on_click=callService("cnl2asp", user_input, cnl_input, ""))

