const se_scraper = require('se-scraper');
import path from 'path';
import {fetchProxies} from './fetch-proxies';

const scraper = async (browser_config:any, scrape_job:any) => {
    
    var scraper = new se_scraper.ScrapeManager(browser_config);
    await scraper.start();

    var results = await scraper.scrape(scrape_job);
    await scraper.quit();
    return results;
};

const search_results = async (keywords: string[], proxy:string, outFile?:string) => {

    const browser_config = {
        debug_level: 1,
        output_file: outFile,
        proxy,
        // log_ip_address: true,
        // use_proxies_only: true,
    };
    
    const scrape_job = {
        search_engine: 'duckduckgo',
        keywords,
        num_pages: 1,
        headless: true
    };

    return await scraper(browser_config, scrape_job);
}

// fetchProxies(1)
// .then(proxy => {
//     console.log('fetched proxy', proxy);
//     search_results(['The Da Vinci Code interesting facts'], proxy).then(res => console.log(res));
// });

export const prllProxyFetch = async (keywords: string[]) => {
    const start  = Date.now();

    // const resultPromise = async (index:number) => {
    //     const proxy = await fetchProxies(1);
    //     await search_results([keywords[index]],proxy, __dirname +`\\..\\prllProxyFetch${index}.json`)
    // }
    // let proxyPromises = [];
    try{

        const resultPomises = keywords.map(async (keyword, index) => {
            const proxy = await fetchProxies(1);
            console.log("prllProxyFetch -> proxy", proxy);
            return proxy && await search_results([keyword],proxy);
        })
        const result = await Promise.all(resultPomises)
        console.log("prllProxyFetch -> end ",Date.now() - start)
        return result;
        // for (let index = 0; index < keywords.length; index++) {
        //     // proxyPromises.push(fetchProxies(1));
        //     const a = Date.now();
        //     console.log("prllProxyFetch -> a", a) 
        //     const result = resultPromise(index)
        //     // const proxy = await fetchProxies(1);
        //     // const serp = await search_results([keywords[index]],proxy, __dirname +`\\..\\prllProxyFetch${index}.json`)
        //     const b = Date.now();
        //     console.log("prllProxyFetch -> b", b)
        //     console.log("prllProxyFetch -> b-a", b-a)
        // }

        // Promise.all(proxyPromises).then(proxies => {
        //     let searchPromises = [];
        //     for (let index = 0; index < keywords.length; index++) {
        //         console.log("prllProxyFetch -> proxies[index]", proxies[index])
        //         searchPromises.push(search_results([keywords[index]],proxies[index], __dirname +`\\..\\prllProxyFetch${index}.json`));
        //     }
        //     Promise.all(searchPromises).then(res => {
        //         console.log(res)
        //         console.log("prllProxyFetch -> end ",Date.now() - start)
        //     })
        // })
    }catch(e){
        console.log(e);
    }
}

export const seqProxyFetch = async (keywords: string[]) => {
    const start  = Date.now();
    const proxies = await fetchProxies(keywords.length);
    let searchPromises = [];
    for (let index = 0; index < keywords.length; index++) {
        searchPromises.push(search_results([keywords[index]],proxies[index]));
    }
    const result = await Promise.all(searchPromises);
    // console.log(res)
    console.log("seqProxyFetch -> end ",Date.now() - start)
    return result;
}

export const oneProxyFetch = async (keywords: string[]) => {
    const start  = Date.now();
    const proxies = await fetchProxies(1);
    let searchPromises = [];
    for (let index = 0; index < keywords.length; index++) {
        searchPromises.push(search_results([keywords[index]],proxies[0]));
    }
    const result = await Promise.all(searchPromises);
    // console.log(res);
    console.log("oneProxyFetch -> end ",Date.now() - start)
    return result;
}


const caller = () => {
    const keywords = ["The Da Vinci Code trivia",
        "The Da Vinci Code interesting trivia",
        "The Da Vinci Code interesting things",
        "The Da Vinci Code interesting facts",
        "The Da Vinci Code shocking facts",
        "The Da Vinci Code things you didn't know"];
    prllProxyFetch(keywords);
    // seqProxyFetch(keywords);
    // oneProxyFetch(keywords)
}

// caller();