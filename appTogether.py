from restAPI.services import *
from flask import render_template

import streamlit as st

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/streamlit')
def streamlit():
    st.set_page_config(page_title="My Streamlit App")
    st.write("Hello, world!")

if __name__ == "__main__":
   print("* Starting web service...")
   app.run(host='0.0.0.0')