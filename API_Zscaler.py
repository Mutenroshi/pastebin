import csv
import requests
import time

# Set the input and output filenames and the Zscaler info filename
input_filename = 'URLS.txt'
output_filename = 'output.csv'
zscaler_filename = 'zscaler-infos.txt'

# Read the input file
with open(input_filename, 'r') as file:
    # Read the lines in the file
    lines = file.readlines()

# Remove the newline characters from the lines
lines = [line.strip() for line in lines]

# Split the lines into chunks of 100 URLs
url_chunks = [lines[i:i+100] for i in range(0, len(lines), 100)]

# Load the Zscaler info from the file
with open(zscaler_filename, 'r') as file:
    # Read the lines in the file
    lines = file.readlines()

# Extract the host, login, password, role and API key from the lines
host = lines[1].split(': ')[1].strip()
login = lines[2].split(': ')[1].strip()
password = lines[3].split(': ')[1].strip()
role = lines[4].split(': ')[1].strip()
api_key = lines[5].split(': ')[1].strip()

# Obfuscate the API key with the current timestamp
timestamp = str(int(time.time() * 1000))
n = timestamp[-6:]
r = str(int(n) >> 1).zfill(6)
obfuscated_key = ""
for i in range(0, len(n), 1):
    obfuscated_key += api_key[int(n[i])]
for j in range(0, len(r), 1):
    obfuscated_key += api_key[int(r[j])+2]

# Authenticate with the API
headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
}
data = {
    'apiKey': obfuscated_key,
    'username': login,
    'password': password,
    'timestamp': timestamp
}
r = requests.post(f'https://{host}/api/v1/authenticatedSession', headers=headers, json=data)

# Check that the request was successful
if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de l'authentification")
    exit()

# Extract the JSESSIONID from the response
jsessionid = r.cookies['JSESSIONID']

# Initialize the list of results
results = []

# Call the Zscaler API for each chunk of URLs
for url_list in url_chunks:
    # Call the Zscaler API with the list of URLs
    headers = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
}
data = {
    'urls': url_list
}
r = requests.post(f'https://{host}/api/v1/urlLookup', headers=headers, json=data, cookies={'JSESSIONID': jsessionid})

# Check that the request was successful
if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de l'appel de l'API")
    exit()

# Extract the URL classification information from the response
url_classification_data = r.json()

# Add the URL classification information to the results
for item in url_classification_data:
    url = item['url']
    categories = ';'.join(item['urlClassifications'])
    results.append((url, categories))

# Write the results to the output file
with open(output_filename, 'w') as file:
    # Write the header row
    file.write('Numéro;URL;Catégories\n')
    # Write the data rows
    for i, result in enumerate(results):
        file.write(f"{i+1};{result[0]};{result[1]}\n")

# Log out of the API
r = requests.delete(f'https://{host}/api/v1/authenticatedSession', cookies={'JSESSIONID': jsessionid})

# Check that the request was successful
if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de la déconnexion")
