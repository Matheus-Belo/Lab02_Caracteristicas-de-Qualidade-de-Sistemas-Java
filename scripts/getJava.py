import subprocess
import requests
import pandas as pd
import os
import subprocess
import shutil
from dotenv import load_dotenv
import json

caminho = os.getenv("path")
resultado = os.getenv("resultpath")


ROOT_PATH = os.getcwd().split('Lab02_Caracteristicas-de-Qualidade-de-Sistemas-Java')[0].replace('\\', '/')
load_dotenv()
chave = os.getenv("key")
graphQL = 'https://api.github.com/graphql'
headers = {'Authorization': 'Bearer %s' % chave}
allResults = list()

repositories = []

def requisicao(repositorios):
    endCursor = None
    startCursor = None
    hasNextPage = True

    for i in range(int(repositorios/20)):
        variaveis = {
            "endCursor": endCursor,
            "startCursor": startCursor
        }
        query = """
        query ($endCursor: String) {
          search(query: "language: Java stars:>1 fork:false sort:stars-desc", type: REPOSITORY, first:20, after: $endCursor) {
            edges {
              node {
                ... on Repository {
                name
                url
                }
              }
            }
            pageInfo {
              endCursor
              startCursor
              hasNextPage
              hasPreviousPage
            }
          }
        }
        """

        request = requests.post(
            url=graphQL, json={'query': query, 'variables': variaveis}, headers=headers)
        resp = request.json()

        if 'data' in resp:
            allResults.extend(resp['data']['search']['edges'])
            pageInfo = resp['data']['search']['pageInfo']
            hasNextPage = pageInfo['hasNextPage']
            endCursor = pageInfo['endCursor']
            startCursor = pageInfo['startCursor']
        
        if not hasNextPage:
            break

    if request.status_code == 200:
        return allResults
    else:
        raise Exception("Falha na Query {}. {}".format(
            request.status_code, query))
    

repositorios = 1000
res = requisicao(repositorios)

if res:
    # Salvar resultado da consulta em um arquivo JSON
    os.makedirs('scripts/dataset/json', exist_ok=True)
    with open('scripts/dataset/json/resultado_query.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    def run_ck_calculator(repository: str):
        comando_original = ["java", "-jar", r"C:\Users\tarci\Desktop\new\ck\target\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar", f"{caminho}/{name}", "true", "0", "true", "resultado"]
        processo = subprocess.Popen(comando_original, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        saida, erro = processo.communicate()
        # Exibe a saída
        if saida:
            print("Saída:")
            print(saida.decode())
        if erro:
            print("Erro:")
            print(erro.decode())


    
       # base_path = f'{ROOT_PATH}scripts'
       # ck_jar_path = f'{base_path}dataset/ck/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar'
       # repo_path = f'{base_path}/dataset/{repository}'
       # ck_results = f'{ROOT_PATH}/scripts/dataset/{repository}/'
        
       # if not os.path.exists(ck_results):
       #     os.makedirs(ck_results)
            
       # ck_command = f'java -jar {ck_jar_path} {repo_path} true 0 false {ck_results}'
       # os.system(ck_command)
    
    for repo in res:
        name = repo['node']['name']
        url = repo['node']['url'] + '.git'
        directory = f'./scripts/dataset/{name}'
        os.makedirs(directory, exist_ok=True)
        subprocess.run(['git', 'clone', url, directory])
        run_ck_calculator(name)
       # shutil.rmtree(f'./scripts/dataset/{name}')
        break

    



    # Converter os dados JSON para DataFrame do Pandas
    df = pd.json_normalize(res)

    # Salvar o DataFrame em um arquivo CSV
    caminhoCSV = 'scripts/dataset/csv/resultado_query.csv'
    df.to_csv(caminhoCSV, index=False)

    # Verificar se o arquivo CSV foi salvo com sucesso
    if os.path.exists(caminhoCSV):
        print("Resultado da consulta salvo em CSV com sucesso.")
    else:
        print("Falha ao salvar resultado em CSV.")
        print("Verifique se o diretório 'scripts/dataset/csv/' existe e tem permissões adequadas.")
        