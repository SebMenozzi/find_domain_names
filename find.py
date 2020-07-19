import requests
import time
import json
import sys
import os
import unicodedata

def remove_accents(bytes):
    decode = bytes.decode('utf-8')
    nfkd = unicodedata.normalize('NFKD', decode)
    return nfkd.encode('ascii', 'ignore')

def getDomainsFromDico(dico, letter, ext, maxLength):
    domains = []

    with open(dico, 'rb') as f:
        content = f.read()

        for word in content.splitlines():
            word = remove_accents(word).decode('utf-8')
            length = len(word)
            if length > 0 and word[0] == letter and length <= maxLength:
                domain = '{}.{}'.format(word, ext)
                domains.append(domain)

    return domains

def chunks(array, size):
   for i in range(0, len(array), size):
      yield array[i:i + size]

def checkDomainsByGoDaddy(domains, filteredDomains, i=0):
    apiKey = 'dLYx8m4oLWgG_QU5RBF48kyWAcgNv2isKGz'
    secretKey = 'KnUE1FzaFFHczBXCoMLaQW'
    url = 'https://api.godaddy.com/v1/domains/available'
    headers = { 'Authorization' : 'sso-key {}:{}'.format(apiKey, secretKey)}

    availabilityResponse = requests.post(url, json=domains, headers=headers)
    resp = json.loads(availabilityResponse.text)
    domains = resp.get('domains')

    try:
        for domain in domains:
            if domain.get('available'):
                print('\033[0;32;49m{}'.format(domain['domain']))
                filteredDomains.append(domain['domain'])
            else:
                print('\033[0;31;49m{}'.format(domain['domain']))

        time.sleep(2)
    except:
        if domains is None:
            print('\033[0;31;49mUNSUPPORTED TLD\033[0;37;49m')
            exit(1)

        print('\033[0;31;49mERROR API')
        time.sleep(2)

        if i <= 1: # can retry twice
            checkDomainsByGoDaddy(domains, filteredDomains, i + 1)

def filterDomainsByGoDaddy(domains):
    chunkSize = 500
    domainChunks = list(chunks(domains, chunkSize))
    filteredDomains = []

    for domains in domainChunks:
        checkDomainsByGoDaddy(domains, filteredDomains)

    return filteredDomains

def saveDomains(letter, ext, domains):
    dir = 'results'
    if not os.path.exists(dir):
        os.mkdir(dir)

    filename = '{}/{}.{}.txt'.format(dir, letter, ext)
    file = open(filename, 'w')
    file.truncate(0)

    for domain in domains:
        file.writelines([ domain, '\n' ])

    file.close()

if __name__ == '__main__':
    dico = sys.argv[1]
    letter = sys.argv[2][0]
    ext = sys.argv[3]
    maxLength = int(sys.argv[4])

    domains = getDomainsFromDico(dico, letter, ext, maxLength)
    godaddyDomains = filterDomainsByGoDaddy(domains)

    saveDomains(letter, ext, godaddyDomains)

    # reset color terminal
    print('\033[0;37;49m')
