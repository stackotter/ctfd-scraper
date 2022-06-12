import requests
import json
import sys
import os
import re

from bs4 import BeautifulSoup
from cleantext import clean

"""
CTFD Challenge Scraper
originally written by: https://github.com/bardiz12
modified by: https://github.com/stackotter
"""
class Scraper():
    def __init__(self,base_url):
        self.user = {
            "username":None,
            "password":None
        }
        self.base_url = base_url[0:-1] if base_url[-1] == "/" else base_url
        self.request = requests.Session()

    def login(self,username,password):
        self.user['username'] = username
        self.user['password'] = password
        token = self.get_login_nonce()
        response = self.post("/login",{"name":username,"password":password,"nonce":token})
        if ("Your username or password is incorrect" in response.text):
            raise Exception('Wrong username/password')

    def get_login_nonce(self):
        page = self.get("/login")
        soup = BeautifulSoup(page.text, 'html.parser')
        nonce = soup.find("input", {"name":"nonce"}).get("value")
        if nonce == None:
            raise Exception("Failed to get login form nonce")
        return nonce

    def get(self,path):
        return self.request.get(self.base_url  + path)

    def post(self,path,data):
        return self.request.post(self.base_url  + path,data)

    def api_get(self,path):
        return self.get("/api/v1" + path)

    def clean_string(self, string):
        cleaned = string.lower()
        cleaned = clean(cleaned, no_emoji=True)
        cleaned = cleaned.strip()
        cleaned = cleaned.replace(" ", "_")
        return cleaned

    def download(self, directory_name, export_json=False):
        if os.path.isdir(directory_name):
            if os.path.isfile(directory_name):
                raise Exception(directory_name + " is not a valid directory")
        else:
            os.mkdir(directory_name)

        json_challs = self.api_get("/challenges").text
        challenges = json.loads(json_challs)
        exported = {}
        for chall in challenges["data"]:
            name = chall["name"]
            category = chall["category"]
            id = chall["id"]
            points = chall["value"]

            cleaned_name = self.clean_string(name)
            cleaned_category = self.clean_string(category)

            print("Downloading %s (%s)" % (name, category))

            # Load challenge details
            chall_info = json.loads(self.api_get("/challenges/%d" % id).text)["data"]
            description = chall_info["description"].replace("\x0d", "")
            files = chall_info["files"]
            connection_info = chall_info["connection_info"]

            # Create challenge directory
            chall_dir = directory_name + "/" + cleaned_category + "/" + cleaned_name
            os.makedirs(chall_dir)

            # Create Readme.md
            with open(chall_dir + "/Readme.md", "w") as output:
                output.write("## %s [%d pts]\n\n" % (name, points))
                output.write(description + "\n")

                if connection_info != None:
                    output.write("\n```\n%s\n```\n" % connection_info)

            # Create Hints.md if hints are available
            hints = []
            for hint in chall_info:
                if "content" in hint:
                    hints.append(hint.content)
            if len(hints) != 0:
                with open(chall_dir + "/Hints.md", "w") as output:
                    output.write("## Hints\n\n")
                    for hint in hints:
                        output.write("- %s\n" % hint)

            # Download attached files
            file_dir = chall_dir + "/files"
            if len(files) > 0:
                os.mkdir(file_dir)
            for file_url in files:
                file_name = file_url.split("?token")[0].split("/")[-1]
                print("    Downloading %s" % file_name)
                file_data = self.get(file_url).content
                file = open(file_dir + "/" + file_name, "wb")
                file.write(file_data)
                file.close()

            # Add to challs.json
            if category not in exported :
                exported[category] = {}
            exported[category][name] = chall_info

        if export_json:
            print("Creating challenges.json")
            with open(directory_name + "/challenges.json", "w") as f:
                json.dump(exported, f, indent=4, sort_keys=True)
