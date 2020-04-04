const se_scraper = require('se-scraper');
const path = require('path');

const browser_config = {
    debug_level: 1,
    output_file: path.join(__dirname, 'results.json'),
    proxy_file: path.join(__dirname,'proxies.txt'), // one proxy per line
    log_ip_address: true,
    use_proxies_only: true,
};

const scrape_job = {
    search_engine: 'google',
    keywords: ['The Da Vinci Code interesting facts'],
    num_pages: 1,
    headless: false,
    // google_settings: {
    //     gl: 'us', // The gl parameter determines the Google country to use for the query.
    //     hl: 'en', // The hl parameter determines the Google UI language to return results.
    // },
};

const scraper = async (browser_config, scrape_job) => {
    
    

    var scraper = new se_scraper.ScrapeManager(browser_config);
    await scraper.start();

    var results = await scraper.scrape(scrape_job);
    // console.dir(results, {depth: null, colors: true});
    await scraper.quit();
};

scraper(browser_config, scrape_job)
.then((val)=>console.log(val))
.catch((reason)=> {
    debugger;
    console.log(reason);
})

