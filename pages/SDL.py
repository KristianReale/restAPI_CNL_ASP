import streamlit as st
import requests, json

URL = "http://localhost:5000"
#URL = "https://asp2cnl.pythonanywhere.com/"

sdl_input = None
execution_output = None

def callService(service, sdl_input, sentence, rule):
   user_input = sdl_input.replace(';', ';&')[:-1].split("&")
   print(user_input)
   print(rule)
   jsonS = {"sdl_input": sdl_input}
   response = requests.post(URL + "/" + service, data=json.dumps(jsonS), headers={"Content-Type": "application/json"})

   execution_output = st.text(response.text)

st.title('SDL')
# Forms can be declared using the 'with' syntax
#with st.form(key='my_form'):
#user_input = st.text_input(label='User Input', value="A movie is identified by an id, and has a title, a director, and a year. A director is identified by a name. A topMovie is identified by an id. A scoreAssignment is identified by an id, and by a value. A waiter is identified by a name.")
sdl_input = st.text_area(label='SDL definition', value="""record Node: id: int;
record Edge: first: Node, second: Node;
record Color: value: str;
record Assign: node: Node, color: Color;

guess from Node
	exactly 1 
        Assign
            from Color
                where Assign.node == Node and Assign.color == Color;  

deny from Assign as a1, Assign as a2, Edge
	where a1.node != a2.node and a1.color == a2.color and 
        	Edge.first == a1.node and Edge.second == a2.node;

show Assign;""")
execution_output = st.text('Results')
toResultButton = st.button(label='Execute', on_click=callService("sdl", sdl_input, execution_output, ""))

