import streamlit as st

def startWebApp():
    st.set_page_config(
        page_title="ASP-CNL Tool",
        page_icon="👋",
    )

    st.write("# Welcome to the Declarative Rewriters! 👋")

    st.sidebar.success("Select a demo above.")

if __name__ == "__main__":    
    startWebApp()

   

