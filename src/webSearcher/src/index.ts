const se_scraper = require('se-scraper');
import path from 'path';
import {fetchProxies} from './fetch-proxies';

const scraper = async (browser_config:any, scrape_job:any) => {
    
    var scraper = new se_scraper.ScrapeManager(browser_config);
    await scraper.start();

    var results = await scraper.scrape(scrape_job);
    await scraper.quit();
};

const search_results = async (keywords: string[], proxy:string, outFile:string = path.join(__dirname +'\\..\\results.json')) => {

    const browser_config = {
        debug_level: 1,
        output_file: outFile,
        proxy,
        log_ip_address: true,
        use_proxies_only: true,
    };
    
    const scrape_job = {
        search_engine: 'duckduckgo',
        keywords,
        num_pages: 1,
        headless: true
    };

    return await scraper(browser_config, scrape_job);
}

fetchProxies(1)
.then(proxy => {
    console.log('fetched proxy', proxy);
    search_results(['The Da Vinci Code interesting facts'], proxy).then(res => console.log(res));
});
