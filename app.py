import streamlit as st
from tool import *
from tool import agent_executor
from github import GithubException
import time, base64
from pathlib import Path


st.set_page_config(page_title="GitGather", layout="centered", initial_sidebar_state="collapsed", page_icon=":book:")
# st._config.set_option(f'theme.backgroundColor' ,"white" )
# st._config.set_option(f'theme.base' ,"light" )
# st._config.set_option(f'theme.primaryColor' ,"#5591f5" )
# st._config.set_option(f'theme.secondaryBackgroundColor' ,"#82E1D7" )
# st._config.set_option(f'theme.textColor' ,"#0a1464")


def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("D:/lecture-notes-uploader-using-llm/background.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/jpg;base64,{img}");
    background-size: cover;
}}

</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# st.markdown(f"""
# <style>
# .stApp {{
#     background-image: url("https://img.freepik.com/free-vector/printable-learning-tools-border-frame-template_1308-160299.jpg?size=626&ext=jpg&ga=GA1.1.2008272138.1722384000&semt=ais_hybrid");
#     background-size: 1100px;
#     background-repeat: no-repeat;
# }}
# </style>
# """, unsafe_allow_html=True)


c1, c2 = st.columns((0.9, 0.1))

with c1:
    st.title("GitGather 📚")
    st.write("A guiding tool that helps lecturers upload study materials to a GitHub repo, providing a clear path for students to follow.")
    with st.container(border=True):
        col1, col2 = st.columns((0.8, 0.1))
    with col1:
        task = st.radio("Choose option", ["List Departments", "Upload Materials", "Create Departments"], horizontal=True, index=None)

        if task == "List Departments":
            result_list = agent_executor.invoke({"input": "List the repositories in AIMIT-IT."})
            with st.expander("View Departments"):
                departments = result_list["output"]
                st.markdown(f":blue[{departments}]")
        
        if task=="Create Departments":
            dept_name = st.text_input("Enter the name of the department")
            submit_button = st.button("Submit", type="secondary")

            if submit_button:
                try:
                    result = agent_executor.invoke({"input": f"Create a new repository called {dept_name} in AIMIT-IT organization."})
                    if result['output'] == "Task Completed":
                        st.success("Department Created Successfully!")
                except GithubException as e:
                    if "errors" in e.data:
                        for error in e.data["errors"]:
                            st.error(error["message"])
                    else:
                        st.error("Enter department name and try again")
                    
                    time.sleep(5)
                    st.rerun(scope="fragement")
                    
        
        if task=="Upload Materials":
            st.title("Upload your notes")

            org_name = git_hub.get_organization("AIMIT-IT")
            repos = org_name.get_repos()
            if repos.totalCount==0:
                st.write("No Repositories")
            else:
                department = ", ".join([r.name for r in repos])

            selected_repo = st.selectbox("Choose Department", [department], index=None)
            uploaded_file = st.file_uploader("Upload file", type=['pdf', 'ppt', 'docx', 'jpg', 'jpeg', 'png'])
            
            if uploaded_file is not None:

                file_path = os.path.join(os.getcwd(), uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                file_upload = agent_executor.invoke({"input": f"Upload the file in {selected_repo} repository. The filename is {uploaded_file.name}"})

                if file_upload["output"] == "Task Completed":
                    st.success("File uploaded successfully!")
                    os.remove(file_path)
                else:
                    st.error(file_upload["output"])


        


