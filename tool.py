import os
import json
from github import Github, Auth
from langchain.tools import tool

with open('config.json') as f:
    config = json.load(f)
os.environ["GITHUB_ACCESS_TOKEN"] = config["GITHUB_ACCESS_TOKEN"]

git_hub = Github(login_or_token=os.environ["GITHUB_ACCESS_TOKEN"])
org_name = git_hub.get_organization("AIMIT-IT")

