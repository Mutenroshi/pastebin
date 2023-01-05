import csv
import requests
import time

# Obfuscate the API key
def obfuscate_api_key(api_key):
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = ""
    for i in range(0, len(str(n)), 1):
        key += api_key[int(str(n)[i])]
    for j in range(0, len(str(r)), 1):
        key += api_key[int(str(r)[j])+2]
    return key

# Read the information from the text file
with open('zscaler-infos.txt', 'r') as file:
    lines = file.readlines()

# Extract the information from the lines
host = None
login = None
password = None
api_key = None
for line in lines:
    if line.startswith('Host : '):
        host = line[7:].strip()
    elif line.startswith('Login : '):
        login = line[8:].strip()
    elif line.startswith('Password : '):
        password = line[11:].strip()
    elif line.startswith('API Key : '):
        api_key = line[10:].strip()

# Check that all the information was found
if host is None or login is None or password is None or api_key is None:
    print("Les informations du fichier zscaler-infos.txt sont incomplètes")
    exit()

# Obfuscate the API key
obfuscated_api_key = obfuscate_api_key(api_key)

# Authenticate the user
headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
}
data = {
    'apiKey': obfuscated_api_key,
    'username': login,
    'password': password,
    'timestamp': str(int(time.time() * 1000))
}
r = requests.post(f'https://{host}/api/v1/authenticatedSession', headers=headers, json=data)

# Check that the authentication was successful
if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de l'authentification")
    exit()

# Get the JSESSIONID from the response
jsessionid = r.cookies['JSESSIONID']

# Open the text file with the URLs and read each line
with open('URLS.txt', 'r') as file:
    lines = file.readlines()

# Initialize the list of results
results = []

# For each group of 100 URLs
for i in range(0, len(lines), 100):
    # Create the list of URLs for this group
    url_list = lines[i:i+100]

    # Call the Zscaler API with the list of URLs
    headers = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Cookie': f'JSESSIONID={jsessionid}'
    }
    data = url_list
    r = requests.post(f'https://{host}/api/v1/urlLookup', headers=headers, json=data)

    # Check that the request was successful
    if r.status_code != 200:
        print(f"Erreur {r.status_code} lors de l'appel de l'API")
        exit()

    # Add the results to the list
    results += r.json()

# Open the output CSV file
with open('output.csv', 'w', newline='') as file:
    # Create the CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write the header row
    writer.writerow(['Numéro', 'URL', 'Catégories'])

    # Write the rows with the results
    for i, result in enumerate(results):
        categories = ','.join(result['urlClassifications'])
        writer.writerow([i+1, result['url'], categories])

# Log out of the API
headers = {
    'Cache-Control': 'no-cache',
    'Cookie': f'JSESSIONID={jsessionid}'
}
requests.delete(f'https://{host}/api/v1/authenticatedSession', headers=headers)
