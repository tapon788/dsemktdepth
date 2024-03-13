import scrapy
import json
from prettytable import PrettyTable
import logging
from colorama import init, Fore, Back, Style
logging.getLogger('scrapy').propagate = False
class SpMktdeptSpider(scrapy.Spider):

    name = "sp_mktdept"
    allowed_domains = ["dse.com.bd"]
    watchlist = ['IFIC','AGNISYSL']
    #watchlist = ['IFIC',]

    def start_requests(self):

        # Set the headers here. The important part is "application/json"
        headers =  {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.dse.com.bd',
            'Origin': 'https://www.dse.com.bd',
            'Referer': 'https://www.dse.com.bd/mkt_depth_3.php',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With':'XMLHttpRequest'

        }
        for stock in self.watchlist:
            req = scrapy.FormRequest(
                url = "https://www.dse.com.bd/ajax/load-instrument.php",
                method='POST',
                formdata={'inst':stock},
                headers=headers,
                callback=self.parse,
            )
            yield req


    def parse(self, response):
        maintable = []
        current_stock = response.xpath('//a/text()').get().strip()
        init(wrap=True)
        print(f"Stock:{Fore.LIGHTRED_EX}{Back.BLACK}{Style.BRIGHT}{current_stock}{Style.RESET_ALL}, "
              f"Open{response.xpath('//div/table/tr[3]//tr[2]/td[2]/text()').get()}, "
              f"LTP{Fore.LIGHTCYAN_EX}{Back.BLACK}{Style.BRIGHT}{response.xpath('//div/table/tr[3]//tr[3]/td[2]/text()').get()}{Style.RESET_ALL}, "
              f"Total Vol: {response.xpath('//div/table/tr[3]//tr[6]//td[4]/text()').get()}(mn)"
              )
        for tbl in response.xpath('//div//table//table//table'):
            thistable = []
            for tr in tbl.xpath('.//tr'):
                row = []
                for div in tr.xpath('./td/div/text()'):
                    row.append(div.get())
                thistable.append(row)
            maintable.append(thistable)
        if len(maintable[0]) > len(maintable[1]):
            diff = len(maintable[0]) - len(maintable[1])
            for i in range(diff):
                maintable[1].append(['--','--'])
        else:
            diff = len(maintable[1]) - len(maintable[0])
            for i in range(diff):
                maintable[0].append(['--','--'])
        maintable[0] = maintable[0][2:]
        maintable[1] = maintable[1][2:]
        cnt = 0
        pt = PrettyTable()
        pt.field_names = ['Buy Price', 'Buy Volume', 'Sell Price', 'Sell Volume']
        for r in maintable[0]:
            #
            buy_sell_combined_row = r+maintable[1][cnt]
            if buy_sell_combined_row:
                #print(buy_sell_combined_row)
                pt.add_row(buy_sell_combined_row)
            cnt += 1
        print(pt)