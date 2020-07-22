export type ScrapeResults = {
    [keyword: string]: {
        [pageNum: string]: {
            time: string;
            effective_query: string;
            results: {
                link: string;
                title: string;
                date: string;
                snippet: string;
                visible_link: string;
                rank: number;
            }[];
            ads: any[];
        };
    };
};
