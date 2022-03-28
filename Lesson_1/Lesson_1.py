import requests

url = 'https://api.github.com'
user_name = 'dmdudarev'
token = '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'
link_1 = f'{url}/users/{user_name}/repos'
link_2 = f'{url}/user/repos?access_token={token}'


def repos_names_list(data):
    for item in data:
        print(f"repo_name: {item['name']} | private: {item['private']}")


def request(link):
    req = requests.get(link)
    if req.ok:
        data = req.json()
        repos_names_list(data)
    else:
        print(f'error {req.status_code}')


request(link_1)
request(link_2)
