import csv
import requests
import time

# Set the input and output filenames and the Zscaler info filename
input_filename = 'URLS.txt'
output_filename = 'output.csv'
zscaler_filename = 'zscaler-infos.txt'

# Set the chunk size for the API calls
chunk_size = 100

# Read the input file
with open(input_filename, 'r') as file:
    # Read the lines in the file
    lines = file.readlines()

# Remove the newline characters from the lines
lines = [line.strip() for line in lines]

# Split the lines into chunks of the specified size
url_chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]

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

# Set the headers for the API calls
headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Cookie': f'JSESSIONID={jsessionid}'
}

# Initialize the list of results
results = []

# Loop over the URL chunks
for i, url_chunk in enumerate(url_chunks):
    # Set the data for the API call
    data = {
        'urls': url_chunk
    }

    # Call the API
    r = requests.post(f'https://{host}/api/v1/urlLookup', headers=headers, json=data)

    # Check that the request was successful
    if r.status_code != 200:
        print(f"Erreur {r.status_code} lors de l'appel API")
        exit()

    # Get the response data
    chunk_results = r.json()

    # Append the results to the list
    results += chunk_results

# Open the output file
with open(output_filename, 'w', newline='') as file:
    # Create a CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write the header row
    writer.writerow(['Numéro', 'URL', 'Catégories'])

    # Write the data rows
    for i, result in enumerate(results):
        categories = ', '.join(result['urlClassifications'])
        writer.writerow([i+1, result['url'], categories])

# Log out of the API
r = requests.delete(f'https://{host}/api/v1/authenticatedSession', cookies={'JSESSIONID': jsessionid})

# Check that the request was successful
if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de la déconnexion")

print("Done!")
