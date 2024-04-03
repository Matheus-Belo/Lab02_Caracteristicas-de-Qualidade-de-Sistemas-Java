import requests
import csv
import os
import tqdm

chave = os.getenv("key")
url = 'https://api.github.com/graphql'
headers = {'Authorization': 'Bearer %s' % chave}

query = """
query($cursor: String, $since: GitTimestamp!) {
  search(query: "language:java stars:>0", type: REPOSITORY, first: 100, after: $cursor) {
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt
        stargazerCount
        defaultBranchRef {
          target {
            ... on Commit {
              history(since: $since) {
                totalCount
              }
            }
          }
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

def get_repositories(cursor=None, since="2023-01-01T00:00:00Z"):
    response = requests.post(url, json={'query': query, 'variables': {'cursor': cursor, 'since': since}}, headers=headers)
    return response.json()

def get_all_repos():
    cursor = None
    repos = []
    while True:
        response_data = get_repositories(cursor)
        
        # Verifica se a solicitação foi bem-sucedida
        if 'errors' in response_data:
            print("Erro na solicitação:", response_data['errors'])
            break
        
        # Verifica se a chave 'data' está presente na resposta
        if 'data' in response_data:
            for node in response_data['data']['search']['nodes']:
                repository_info = {
                    'nameWithOwner': node['nameWithOwner'],
                    'createdAt' : node['createdAt'],
                    'stargazerCount': node['stargazerCount'],
                    'commitCount': node['defaultBranchRef']['target']['history']['totalCount']
                }
                repos.append(repository_info)
            pageInfo = response_data['data']['search']['pageInfo']
            hasNextPage = pageInfo['hasNextPage']
            if not hasNextPage or len(repos) >= 1000:
                break
            cursor = pageInfo['endCursor']
        else:
            print("Resposta inesperada:", response_data)
            break

    return repos

def write_to_csv(repos):
    with open('./scripts/dataset/csv/s2.csv', 'w', newline='') as csvfile:
        fieldnames = ['nameWithOwner', 'createdAt', 'stargazerCount', 'commitCount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repos:
            writer.writerow(repo)

def main():
    repos = get_all_repos()
    write_to_csv(repos)

if __name__ == "__main__":
    main()