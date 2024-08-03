import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
from github import Github
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor,  create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

with open('config.json') as f:
    config = json.load(f)
os.environ["GITHUB_ACCESS_TOKEN"] = config["GITHUB_ACCESS_TOKEN"]
os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]
username = config['USERNAME']
password = config['PASSWORD']


git_hub = Github(login_or_token=os.environ["GITHUB_ACCESS_TOKEN"])
org_name = git_hub.get_organization("AIMIT-IT")


# @tool
# def get_repo_name(org: str):
#     """This function is used to list the repositories in github organization."""
#     org_name = git_hub.get_organization(org)
#     repos = org_name.get_repos()
#     if repos.totalCount==0:
#         return "No Repositories"
#     else:
#         repositories = ", ".join([r.name for r in repos])
#         return repositories

@tool
def create_repos(org: str, name: str):
    """This function is used to create new repository in speficied github organization."""
    org_name = git_hub.get_organization(org)
    org_name.create_repo(name)
    return "Task Completed"

@tool
def upload_to_repo(repo: str, filename: str):
    """This function is used to upload files in speficied github repository of AIMIT-IT organization"""

    repo = org_name.get_repo(repo)
    
    file_path = os.path.join(os.getcwd(), filename)
    print(file_path)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    # Navigate to GitHub login page
    driver.get("https://github.com/login")

    # Enter GitHub credentials
    username_input = driver.find_element(By.NAME, 'login')
    username_input.send_keys(username)
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)
    login_button = driver.find_element(By.NAME, "commit")
    login_button.click()

    driver.get(f"{repo.html_url}"+"/upload/")

    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(file_path)

    revealed = driver.find_element(By.XPATH, "//div[1]/div[5]/div/main/turbo-frame/div/div/div[4]")
    WebDriverWait(driver, timeout=20).until(lambda d : revealed.is_displayed())

    if (revealed.is_displayed()):
        commit_button = driver.find_element(By.XPATH, "//div[1]/div[5]/div/main/turbo-frame/div/div/form/button")
        commit_button.click()

    return "Task Completed"

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.0, convert_system_message_to_human=True, max_output_tokens=800)

template = """
You are a helpful assistant who have access to github.
You are asked to do some tasks in the specified organization of github.
Begin!
{input}
{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])


agent = create_tool_calling_agent(llm, [upload_to_repo, create_repos], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[upload_to_repo, create_repos], verbose=True, return_intermediate_steps=True)

#agent_executor.invoke({"input": f"Upload the file in I-MSc-DataScience repository. The file name is OCI_GenAI_Professional_Certificate.pdf'"})

# subprocess.run(["git", "clone", repository])
#     subprocess.run(["git", "init"])
#     subprocess.run(["git", "add", filename])
#     subprocess.run(["git", "commit", "-m", "File added"])
#     subprocess.run(["git", "push", "origin", "main"])

