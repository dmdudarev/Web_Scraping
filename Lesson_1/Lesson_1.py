import requests

user_name = 'dmdudarev'
token = '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'
url_1 = f'https://api.github.com/users/{user_name}/repos'
url_2 = 'https://api.github.com/user/repos'


def repos_names_list(data):
    for item in data:
        print(f"repo_name: {item['name']} | private: {item['private']}")


def request(url, name, token):
    req = requests.get(url, auth=(name, token))
    if req.ok:
        data = req.json()
        repos_names_list(data)
    else:
        print(f'error {req.status_code}')


request(url_1, user_name, token)
request(url_2, user_name, token)
