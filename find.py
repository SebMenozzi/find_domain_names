import requests
import time
import json
import sys
import os
import unicodedata

def setupQueue(queue):
    queue.append(('dLYx8m4oLWgG_QU5RBF48kyWAcgNv2isKGz', 'KnUE1FzaFFHczBXCoMLaQW'))
    queue.append(('dLYx8m4oLWgG_4bpngpmmU7c7YE8nyuE47z', '3NLLBDfUuQQA3UgKZU6QEX'))
    queue.append(('dLYx8m4oLWgG_Nhw8LL1jugYgr4vTtFJkxB', 'R4cN3FVte4nR43WHNXvCpE'))
    queue.append(('dLYx8m4oLWgG_5o19oetk8mmpgL9VAk7RSz', 'Nc5cE3HZHM4gVAnP9FkGiM'))
    queue.append(('dLYx8m4oLWgG_CDLgPbeib1ZuqbuQw2AVbt', 'DoRHknjssdndVkKyJyRqAR'))

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

def checkDomains(domains, filteredDomains, queue, i=1):
    url = 'https://api.godaddy.com/v1/domains/available'

    (apiKey, secretKey) = queue.pop()
    queue.insert(0, (apiKey, secretKey))
    headers = { 'Authorization' : 'sso-key {}:{}'.format(apiKey, secretKey) }

    availabilityResponse = requests.post(url, json=domains, headers=headers)
    resp = json.loads(availabilityResponse.text)
    domains = resp.get('domains')

    try:
        for domain in domains:
            if domain.get('available'):
                print('\033[0;32;49m{}\033[0;37;49m'.format(domain['domain']))
                filteredDomains.append(domain['domain'])
            else:
                print('\033[0;31;49m{}\033[0;37;49m'.format(domain['domain']))

        time.sleep(30)
    except:
        if domains is None:
            pass

        print('\033[0;31;49mERROR API\033[0;37;49m')
        time.sleep(30)

        if i <= len(queue): # can retry the nb of api key
            checkDomains(domains, filteredDomains, queue, i + 1)

def filterAvailableDomains(domains):
    chunkSize = 500
    domainChunks = list(chunks(domains, chunkSize))
    filteredDomains = []
    queue = []

    setupQueue(queue)

    for domains in domainChunks:
        checkDomains(domains, filteredDomains, queue)

    return filteredDomains

def saveDomains(letter, ext, domains):
    if not os.path.exists('results'):
        os.mkdir('results')

    dir = 'results/{}'.format(ext)

    if not os.path.exists(dir):
        os.mkdir(dir)

    filename = '{}/{}.txt'.format(dir, letter)
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
    domains = filterAvailableDomains(domains)

    saveDomains(letter, ext, domains)

    # reset color terminal
    print('\033[0;37;49m')
