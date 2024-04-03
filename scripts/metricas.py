import csv
import shutil
import subprocess
import zipfile
import os
from tqdm import tqdm
from git import Repo
import getRepo

CSV_FILE_PATH = './scripts/dataset/csv/s2.csv'
CK_JAR_PATH = "C:/Users/tarci/Desktop/Lab02_Caracteristicas-de-Qualidade-de-Sistemas-Java/scripts/dataset/ck/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"
DATASET_PATH = "./scripts/dataset/"
DOWNLOAD_PATH = "./scripts/"

def get_repos(csv_file):
    getRepo.main()
    urls = []
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            repo_url = row[0].split(',')[0]
            urls.append(repo_url)
    return urls

def download_repo(repo_url, target_dir):
    try:
        Repo.clone_from(repo_url, target_dir)
        print("Repository cloned successfully!")
    except Exception as e:
        print(f"Error cloning repository: {e}")

def analyze(repo_partial_url):
    dir_address = repo_partial_url.replace('/', '-')
    repo_url = "https://github.com/" + repo_partial_url
    target_dir = os.path.join(DOWNLOAD_PATH, dir_address)  # Construct target directory

    download_repo(repo_url, target_dir)
    analyze_path = target_dir  
    os.makedirs(analyze_path, exist_ok=True)
    print(analyze_path)
    print(DATASET_PATH)

    try:
        subprocess.run(["java", "-jar", CK_JAR_PATH, analyze_path, "true", "0", "false", DATASET_PATH + dir_address])
        # print("Analysis completed successfully!")
    except Exception as e:
        print(f"Error analyzing repository: {e}")

    try:
        shutil.rmtree(analyze_path, ignore_errors=True)
        # print("Repository directory deleted successfully!")
    except Exception as e:
        print(f"Error deleting repository directory: {e}")

urls = get_repos(CSV_FILE_PATH)
for x in tqdm(urls, desc="Processing repositories", unit="repo"):
    analyze(x)

# analyze('yangchong211/YCAppTool')

# compress_dataset(DATASET_PATH)