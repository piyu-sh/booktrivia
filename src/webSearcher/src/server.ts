import { Response, Request } from "express";
import { oneProxyFetch, oneProxyFetchJhao } from './fetch-results';
const express = require('express');
const app = express();
const port = 3002;


app.get('/getLinks', async function (req: Request, res: Response) {
    const keyword = req.query['keyword'];
    if(!keyword)
    return res.send(400);

    // const search_words = [
    //     'trivia',
    //     'interesting trivia',
    //     'interesting things',
    //     'interesting facts',
    //     'shocking facts',
    //     "things you didn't know"
    // ];

    // const queries = search_words.map(words => `${keyword} ${words}`)
    const data = await oneProxyFetch([keyword as string]);
    return res.json(data);
    // fetch results, ectract links and return for ML
    // res.send('Hello World!')
  })

  app.get('/getLinksJhao', async function (req: Request, res: Response) {
    const keyword = req.query['keyword'];
    if(!keyword)
    return res.send(400);

    // const search_words = [
    //     'trivia',
    //     'interesting trivia',
    //     'interesting things',
    //     'interesting facts',
    //     'shocking facts',
    //     "things you didn't know"
    // ];

    // const queries = search_words.map(words => `${keyword} ${words}`)
    const data = await oneProxyFetchJhao([keyword as string]);
    return res.json(data);
    // fetch results, ectract links and return for ML
    // res.send('Hello World!')
  })

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))
