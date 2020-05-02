
import fetch from 'node-fetch';

const proxyApiUrl = "http://localhost:3001/proxy"

export const fetchProxies = async (numProxies = 1) => {
    if(isNaN(numProxies)){
        throw new Error('numProxies must be a number')
    }
    let result;
    try {
        result= await fetch(`${proxyApiUrl}/${numProxies}`)
        .then(res => res.json())
    }catch(e){
        console.log(e);
    }
    return result;
}
