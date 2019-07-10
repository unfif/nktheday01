# -*- coding: utf-8 -*-
import scrapy, re, requests
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from nkc01.items import Nkc01Item
import datetime as dt

# now = dt.datetime.now()
# cYmd = "{0:%Y%m%d}".format(now)
today = dt.date.today()
targetdate = today - dt.timedelta((today.weekday() + 1) % 7)
targetday = "{0:%m%d}".format(targetdate)

baseurl = 'http://race.netkeiba.com/?pid=race_list_sub&id='
starturl = baseurl + 'p' + targetday
try:
    req = requests.get(starturl)
    if len(req.text) < 50: starturl = baseurl + 'c' + targetday
except:
    starturl = baseurl + 'c' + targetday

class NkthedaySpider(CrawlSpider):
    name = 'nktheday'
    allowed_domains = ['race.netkeiba.com']
    # start_urls = ['http://race.netkeiba.com/']

    rules = (
        Rule(LinkExtractor(
            allow = ['race.netkeiba.com/?pid=race&id=', '&mode=top'],#'race.netkeiba.com/?pid=race_list_sub&id=',
            deny = ['db.netkeiba.com/race/movie'],
            restrict_css = ['.race_top_hold_list']
        ),
            callback = 'parse_races', follow = True
        ),
    )

    def __init__(self, date='c'+targetday, *args, **kwargs):
        super(NkthedaySpider, self).__init__(*args, **kwargs)
        # print(starturl, baseurl + date, date)
        self.start_urls = [baseurl + date]
        # print('targetday: ', cdate)

    # def start_requests(self):
    #     url = 'http://race.netkeiba.com/?pid=race_list_sub&id=c' + cdate
    #     yield scrapy.Request(url, callback=self.parse_races)

    def parse_races(self, response):
        item = Nkc01Item()

        raceinfo = response.css('.race_head_inner')
        raceplaceurl = raceinfo.css('ul.race_place a.active::attr(href)').get()
        raceplaceurl = response.request.url
        item['raceid'] = raceplaceurl.split('=')[2][1:].split('&')[0]
        mainracedata = raceinfo.css('.mainrace_data')[0]
        otherdata = mainracedata.css('.race_otherdata')[0].css('p')
        dateweek = otherdata[0].css('::text').get()
        scheduletype = otherdata[1].css('::text').get()
        raceclass = otherdata[2].css('::text').get()
        addedmoney = otherdata[3].css('::text').get()
        item['place'] = re.split('\d', scheduletype.split('回')[1])[0]
        # item['place'] = raceinfo.css('ul.race_place a.active::text').get()
        item['racenum'] = raceinfo.css('div.race_num a.active::text').get().split('R')[0]
        racedata = raceinfo.css('.data_intro dl.racedata')[0]
        item['title'] = racedata.css('h1::text').get().strip()
        racetype = racedata.css('dd p')[0].css('::text').get()
        courcetype = re.split('(\d+)|m', racetype)
        item['courcetype'] = courcetype[0]
        item['distance'] = courcetype[1]
        item['direction'] = re.split('[()]', racetype)[1]#racetype.split('(')[1][0]
        racecondition = racedata.css('dd p')[1].css('::text').get().split('\xa0/\xa0')
        item['weather'] = racecondition[0].split('：')[1]
        item['condition'] = racecondition[1].split('：')[1]
        item['posttime'] = racecondition[2].split('：')[1]
        # # datadetail = raceinfo.css('div.data_intro p.smalltxt')
        # racedetails = raceinfo.css('dl.racedata + p.smalltxt::text').get()
        # racedatejp = racedetails.split()[0]
        # raceyear = racedatejp.split('年')[0]
        # racemonth = racedatejp.split('年')[1].split('月')[0].zfill(2)
        # raceday = racedatejp.split('月')[1].split('日')[0].zfill(2)
        # item['date'] = raceyear + '-' + racemonth + '-' + raceday
        item['date'] = dateweek.split('(')[0].replace('/', '-')
        item['racegrade'] = raceclass.split('\xa0')[0]
        item['starters'] = raceclass.split('\xa0')[1][:-1]
        addedarr = addedmoney.split('：')[1].split('万円')[0].split('、')
        item['raceaddedmoney'] = ','.join([str(int(x) * 1000) for x in addedarr])
        # item['schedule'] = racedetails.split()[1]
        # item['racegrade'] = racedetails.split()[2]
        # item['category'] = racedetails.split()[3]

        for tr in response.css('[summary="レース結果"] tr:not(tr:first-of-type)'):
            item['placenum'] = tr.css('td')[0].css('::text').get()
            item['postnum'] = tr.css('td')[1].css('span::text').get()
            item['horsenum'] = tr.css('td')[2].css('::text').get()
            item['horsename'] = tr.css('td')[3].css('a::text').get()
            item['sex'] = tr.css('td')[4].css('::text').get()[0]
            item['age'] = tr.css('td')[4].css('::text').get()[1:]
            item['weight'] = tr.css('td')[5].css('::text').get()
            item['jockey'] = tr.css('td')[6].css('a::text').get()
            item['time'] = tr.css('td')[7].css('::text').get()
            margin = tr.css('td')[8].css('::text').get()
            item['margin'] = margin if margin is not None else '0'
            item['fav'] = tr.css('td')[9].css('::text').get()
            item['odds'] = tr.css('td')[10].css('::text').get()
            item['last3f'] = tr.css('td')[11].css('::text').get()
            item['position'] = tr.css('td')[12].css('::text').get()
            item['trainer'] = tr.css('td')[13].css('a::text').get()
            item['horseweight'] = tr.css('td')[14].css('::text').get().split('(')[0]
            item['horseweightdiff'] = tr.css('td')[14].css('::text').get().split('(')[1][:-1].replace('+', '')
            item['requrl'] = response.request.url

            yield item
