#!/usr/bin/env python3

import os
import base64
import requests
import re
import sys


class Github():
    def __init__(self, api_key):
        self.__api_key = api_key
        self.all_repos_api = "https://api.github.com/user/repos"
        self._owner_api = "https://api.github.com/user"
        self.headers =  {'Authorization': f'token {self.__api_key}'}
        self.owner_name = self.get_owner().get("login")
        self.def_branch = "master"
        self.def_ignores = ["node_modules", ".git", "__pycache__", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*", "pnpm-debug.log*", "lerna-debug.log*" ]
        self.repo_api = f"https://api.github.com/repos/{self.owner_name}"
    
    def get_owner(self):
        _owner = requests.get(self._owner_api, headers=self.headers)
        return _owner.json()
    
    def list_repos(self):
        pub_repos =[]
        response = requests.get(self.all_repos_api,headers=self.headers).json()
        for repos in response:
            pub_repos.append(repos["name"])
        return pub_repos
    
    def get_repo(self, repo, filtered=None):
        if filtered == None: filtered = False
        response = requests.get(f"{self.repo_api}/{repo}", headers=self.headers)
        return response.json()
    
    def new_repo(self, repo_name, desc=None, pvt=None, auto_init=None , branch=None):
        if not desc: desc = '''  '''
        if not pvt: pvt = False
        if not auto_init: auto_init = True
        if not branch:branch = self.def_branch
        
        repo_setup = {
            'name': repo_name,
            'description': desc,
            'private': pvt,
            'auto_init': auto_init, # Automatically create an initial README file
            'branch': branch
        }
        
        response = requests.post(self.all_repos_api, headers=self.headers, json=repo_setup)
        if response.status_code == 201:
            print(f"Repo: {repo_name} created Successfully for {self.owner_name} at branch: {branch}")
            return True
        else:
            print("Repo creation failed",response.json())
            return False
            
    def delete_repo(self, repo):
        response = requests.delete(f"{self.repo_api}/{repo}",headers=self.headers)
        if response.status_code == 204:
            print(f"Successfully deleted repository: {repo}")
            return True
        else:
            print(f"Failed to delete repository: {response.json()}")
            return False
    
    def clone_repo(self, repo, save_path=None):
        pass
    
    
    def set_path(self, path, parent=None):
        if not parent:
            path = os.path.basename(path)
        else:
            path = f"{parent}{path.split(parent, 1)[-1]}"
        return path
    
    def check_content(self,filepath, repo, branch=None):
        if not branch:branch= self.def_branch
        check_url = f'https://api.github.com/repos/{self.owner_name}/{repo}/contents/{filepath}?ref={branch}'
        response = requests.get(check_url, headers=self.headers)

        if response.status_code == 200:
            sha = response.json().get("sha")
        else:
            sha = None
        return sha
    
    def list_contents(self, repo,branch=None):
        repo_paths = []
        response=requests.get(f"{self.repo_api}/{repo}/contents/", headers=self.headers)
        for paths in response:
            print(repo_paths.append(paths['path'], paths['type'], paths['sha']))
        
    
    def push_dir(self, path,repo, include_parent=False, commit_msg="added via upload", ignore_files = None , branch = None ):
            #initite ignore patterns set to default used patterns if nothing specified
            if branch == None:
                branch = 'master'
            
            if ignore_files == None:
                ignore_pattern  =  r'\/(' + '|'.join(re.escape(ignore_path) for ignore_path in self.def_ignores) + r')\/'
            else: 
                ignore_pattern = r'\/(' + '|'.join(re.escape(ignore_path) for ignore_path in ignore_files ) + r')\/'
            
            #parent path of given path
            base_path = os.path.basename(path)
        
            for directory, sub_dirs ,filenames in os.walk(path):
                #loop through all files and checks for ignore files
                for files in filenames:
                    filepath = os.path.join(directory, files)
                    ignore_match = re.search(ignore_pattern, filepath)
                    if ignore_match:
                        print("Ignored Upload", filepath)
                
                    else:
                    
                        filepath = os.path.join(directory, files)
                        #filepath = filepath.split(parent_path)[-1]
                        
                        with open(filepath, 'rb') as file:
                            content = file.read()
                            encoded_content = base64.b64encode(content).decode('utf-8')
                        
                        if include_parent:
                            filepath = filepath.split(base_path, 1)[-1]
                            filepath = str(base_path)+str(filepath)
                            
                        else:
                            filepath = filepath.split(base_path, 1)[-1][1:]
                        
                        check_url = f'https://api.github.com/repos/{self.owner_name}/{repo}/contents/{filepath}?ref={branch}'
                        response = requests.get(check_url, headers=self.headers)
                
                        if response.status_code == 200:
                            sha = response.json().get("sha")
                        else:
                            sha = None  # File does not exist, so we'll create a new one
        
                        
                        api_url = f'https://api.github.com/repos/{self.owner_name}/{repo}/contents/{filepath}'
                        data = {
                            'message': commit_msg,
                            'content': encoded_content,
                            'branch' : branch
                        }
                        if sha:
                            data['sha'] = sha
                            
                        response = requests.put(api_url, headers=self.headers, json=data)
    
                        if response.status_code in [200, 201]:
                            action = "updated" if sha else "uploaded"
                            print(f'Successfully {action} {filepath} to branch {branch} in repository: {repo}')
                        else:
                            print(f'Failed to upload {filepath} to branch {branch}: {response.json()}')
    
        
        
        
g = Github("API TOKEN")
#g.new_repo("GithubApi")
g.push_dir("/data/data/com.termux/files/home/projects/github_api", "GithubApi")
print(g.list_repos())
