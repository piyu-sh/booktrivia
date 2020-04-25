
import fetch from 'node-fetch';

const proxyApiUrl = "http://localhost:3001"

export const fetchProxies = async (numProxies = 1) => {
    if(isNaN(numProxies)){
        throw new Error('numProxies must be a number')
    }
    return await fetch(`${proxyApiUrl}/${numProxies}`)
    .then(res => res.json())
}
