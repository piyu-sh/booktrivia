import requests

def getHtmlUsingProxies(url:str, proxyApiUrl:str, retries:int=3):    
    proxies = get_proxies(proxyApiUrl, retries)
    timeout=2#     for proxyObj in proxiesStore:
    proxiesList = list(proxies)
    for x in range(0, len(proxiesList)):
        # proxyObj = proxiesList[x]
        proxy = proxiesList[x]
        # proxy = str(proxyObj.host)+':'+str(proxyObj.port)
        try:
            print(proxy)
            print('fetching '+url+ ' using proxy '+proxy)
            # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=timeout)
            if(response.status_code == requests.codes['ok']): #pylint: disable=no-member
                print('fetched')
                return response.text
            else:
                print('Skipping. status code '+ str(response.status_code))
        except requests.exceptions.Timeout:
            x -= 1
            if( x < (len(proxiesList) - 1)):
                timeout *= 2
                print("timed out increasing timeout, timeout now is: "+ str(timeout) )
        except Exception as e:
            #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
            #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
            print("Skipping. Connnection error " + str(e))
    print("can't fetch this doc")
    return ''

def get_proxies(proxyApiUrl:str, num:int=1):
    return requests.get(proxyApiUrl+'/'+ str(num)).json()
