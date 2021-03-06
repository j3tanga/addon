# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools
from core import jsontools as json


host = 'https://txxx.com'
url_api = host + "/api/json/videos/86400/str/"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Ultimas" , action="lista", url=url_api + "latest-updates/60/..1.all..day.json"))
    itemlist.append( Item(channel=item.channel, title="Mejor valoradas" , action="lista", url=url_api + "top-rated/60/..1.all..day.json"))
    itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=url_api + "most-popular/60/..1.all..day.json"))
    itemlist.append( Item(channel=item.channel, title="Pornstar" , action="pornstar", url=host + "/api/json/models/86400/str/filt........../most-popular/48/1.json"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "/api/json/channels/86400/str/latest-updates/80/..1.json"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/api/json/categories/14400/str.all.json"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "https://txxx.com/api/videos.php?params=86400/str/relevance/60/search..1.all..day&s=%s" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def pornstar(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for cat in  JSONData["models"]:
        scrapedtitle = cat["title"]
        dir = cat["dir"]
        scrapedthumbnail =  cat["img"]
        num = cat["statistics"]
        n = 'videos'
        num = num.get(n,n)
        thumbnail = scrapedthumbnail.replace("\/", "/")
        scrapedplot = ""
        scrapedurl = url_api + "latest-updates/60/model.%s.1.all..day.json" %dir
        title = "%s (%s)" %(scrapedtitle,num)
        itemlist.append( Item(channel=item.channel, action="lista", title=title , url=scrapedurl , 
                        thumbnail=thumbnail , plot=scrapedplot) )
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'.*?(\d+).json'))
    url_page = scrapertools.find_single_match(item.url,'(.*?)\d+.json')
    next_page = (page+ 1)
    if (page*60) < total:
        next_page = "%s%s.json" %(url_page,next_page)
        itemlist.append(item.clone(action="pornstar", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for cat in  JSONData["channels"]:
        scrapedtitle = cat["title"]
        dir = cat["dir"]
        scrapedthumbnail =  cat["img"]
        num = cat["statistics"]
        n = 'videos'
        num = num.get(n,n)
        thumbnail = scrapedthumbnail.replace("\/", "/")
        scrapedplot = ""
        scrapedurl = url_api + "latest-updates/60/channel.%s.1.all..day.json" %dir
        title = "%s (%s)" %(scrapedtitle,num)
        itemlist.append( Item(channel=item.channel, action="lista", title=title , url=scrapedurl , 
                        thumbnail=thumbnail , plot=scrapedplot) )
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'.*?.(\d+).json'))
    url_page = scrapertools.find_single_match(item.url,'(.*?).\d+.json')
    next_page = (page+ 1)
    if (page*60) < total:
        next_page = "%s.%s.json" %(url_page,next_page)
        itemlist.append(item.clone(action="catalogo", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    JSONData = json.load(data)
    for cat in  JSONData["categories"]:
        scrapedtitle = cat["title"]
        dir = cat["dir"]
        num = cat["total_videos"]
        url = url_api + "latest-updates/60/categories.%s.1.all..day.json" %dir
        thumbnail = ""
        scrapedplot = ""
        title = "%s (%s)" %(scrapedtitle,num)
        itemlist.append( Item(channel=item.channel, action="lista", title=title , url=url , 
                        thumbnail=thumbnail, plot=scrapedplot) )
    return  sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["videos"]:
        video_id = Video["video_id"]
        dir = Video["dir"]
        scrapedtitle = Video["title"]
        duration = Video["duration"]
        scrapedthumbnail =  Video["scr"]
        scrapedhd =  Video["props"]
        scrapedurl = "https://txxx.com/api/videofile.php?video_id=%s&lifetime=8640000" %video_id
        header = "https://txxx.com/videos/%s/%s/" % (video_id,dir)
        if scrapedhd:
            title = "[COLOR yellow]" +duration+ "[/COLOR] " + "[COLOR tomato] HD [/COLOR] "+scrapedtitle
        else:
            title = "[COLOR yellow]" + duration + "[/COLOR] " + scrapedtitle
        thumbnail = scrapedthumbnail.replace("\/", "/")
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play" , title=title , url=scrapedurl, thumbnail=thumbnail, 
                        plot=plot, contentTitle=title, header=header) )
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'(\d+).all..day'))
    url_page = scrapertools.find_single_match(item.url,'(.*?).\d+.all..day')
    post = scrapertools.find_single_match(item.url,'all..day(.*)')
    next_page = (page+ 1)
    if (page*60) < total:
        next_page = "%s.%s.all..day%s" %(url_page,next_page,post)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    headers = {'Referer': item.header}
    data = httptools.downloadpage(item.url, headers=headers).data
    texto = scrapertools.find_single_match(data, '"video_url":"([^"]+)"')
    url = dec_url(texto)
    url = host + url
    item.url = httptools.downloadpage(url, only_headers=True).url
    return [item]


def dec_url(txt):
    #truco del mendrugo
    # txt = txt.replace('\u0410', 'A').replace('\u0412', 'B').replace('\u0421', 'C').replace('\u0415', 'E').replace('\u041c', 'M').replace('~', '=').replace(',','/')
    txt = txt.decode('unicode-escape').encode('utf8')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    import base64
    url = base64.b64decode(txt)
    return url

