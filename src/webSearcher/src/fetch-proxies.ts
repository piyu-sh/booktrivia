
import fetch from 'node-fetch';

const proxyApiUrl = "http://localhost:3001/proxy"
const proxyApiUrlJhao = "http://localhost:5010/get/"

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

export const fetchProxyJhao = async () => {
    let result;
    try {
        result= await fetch(proxyApiUrlJhao)
        .then(res => res.json())
    }catch(e){
        console.log(e);
    }
    return `http://${result.proxy}`;
}
