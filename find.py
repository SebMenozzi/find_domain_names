import sys
import os
import unicodedata
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
from concurrent.futures import ThreadPoolExecutor

def remove_accents(bytes):
    decode = bytes.decode('utf-8')
    nfkd = unicodedata.normalize('NFKD', decode)
    return nfkd.encode('ascii', 'ignore')

def get_domains_dico(dico, maxLength):
    domains = []

    with open(dico, 'rb') as f:
        content = f.read()

        for word in content.splitlines():
            word = remove_accents(word).decode('utf-8')
            length = len(word)
            if length > 0 and length <= maxLength:
                domain = '{}.app'.format(word)
                domains.append(domain)

    return domains

def check_domain(domain):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get('https://pubapi-dot-domain-registry.appspot.com/check?domain={}'.format(domain))
    response_json = json.loads(response.text)

    if response_json['available']:
        print('\033[0;32;49m{}\033[0;37;49m'.format(domain))
        return domain
    else:
        print('\033[0;31;49m{}\033[0;37;49m'.format(domain))
        return None

def check_domains_parallel(dico, max_length):
    domains = get_domains_dico(dico, max_length)

    results = []

    executor = ThreadPoolExecutor(max_workers=100)
    for result in executor.map(check_domain, domains):
        if not result is None:
            results.append(result)

    return results

def save(domains):
    if not os.path.exists('results'):
        os.mkdir('results')

    filename = 'apps.txt'.format(dir)
    file = open(filename, 'w')
    file.truncate(0)

    for domain in domains:
        file.writelines([ domain, '\n' ])

    file.close()

if __name__ == '__main__':
    dico = sys.argv[1]
    max_length = int(sys.argv[2])
    
    results = check_domains_parallel(dico, max_length)

    save(results)

    # reset color terminal
    print('\033[0;37;49m')
