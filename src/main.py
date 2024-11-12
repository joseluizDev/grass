from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchDriverException
import time
import requests
import os
import re
import hashlib
from flask import Flask, jsonify

extension_id = 'ilehaonighjijnmpnagapkhpcdbhclfg'
CRX_URL = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=98.0.4758.102&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

# Configurações de usuário e debug
USER = os.getenv('GRASS_USER', '')
PASSW = os.getenv('GRASS_PASS', '')
ALLOW_DEBUG = os.getenv('ALLOW_DEBUG', 'False').lower() == 'true'

# Verificação de credenciais
if not USER or not PASSW:
    print('Please set GRASS_USER and GRASS_PASS env variables')
    exit(1)

def download_extension(extension_id):
    url = CRX_URL
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, stream=True, headers=headers)
    with open("grass.crx", "wb") as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
    if ALLOW_DEBUG:
        md5 = hashlib.md5(open('grass.crx', 'rb').read()).hexdigest()
        print(f'Extension MD5: {md5}')

def generate_error_report(driver):
    if not ALLOW_DEBUG:
        return
    driver.save_screenshot('error.png')
    logs = driver.get_log('browser')
    with open('error.log', 'w') as f:
        for log in logs:
            f.write(str(log) + '\n')
    print('Error report generated.')

print('Downloading extension...')
download_extension(extension_id)
print('Downloaded! Starting...')

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--no-sandbox')
options.add_extension('grass.crx')

try:
    driver = webdriver.Chrome(options=options)
except (WebDriverException, NoSuchDriverException):
    print('Failed to start WebDriver!')
    exit(1)

# Início do login
print('Logging in...')
driver.get('https://app.getgrass.io/')

try:
    # Espera até que o campo de usuário esteja presente e visível
    user_field = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@name="user"]'))
    )
    password_field = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@name="password"]'))
    )
    submit_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@type="submit"]'))
    )

    # Insere as credenciais
    user_field.send_keys(USER)
    password_field.send_keys(PASSW)
    submit_button.click()
    
except Exception as e:
    print('Failed during login:', str(e))
    generate_error_report(driver)
    driver.quit()
    exit(1)

print('Logged in successfully!')

# Flask API
app = Flask(__name__)

@app.route('/')
def get_status():
    try:
        network_quality = driver.find_element('xpath', '//*[contains(text(), "Network quality")]').text
        network_quality = re.findall(r'\d+', network_quality)[0]
    except Exception:
        network_quality = None
        print('Could not retrieve network quality.')
        generate_error_report(driver)

    try:
        token = driver.find_element('xpath', '//*[@alt="token"]').find_element('xpath', 'following-sibling::div').text
    except Exception:
        token = None
        print('Could not retrieve token information.')
        generate_error_report(driver)

    try:
        badges = driver.find_elements('xpath', '//*[contains(@class, "chakra-badge")]')
        connected = any('Connected' in badge.text for badge in badges)
    except Exception:
        connected = None
        print('Could not retrieve connection status.')
        generate_error_report(driver)

    return jsonify({'connected': connected, 'network_quality': network_quality, 'epoch_earnings': token})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

driver.quit()
