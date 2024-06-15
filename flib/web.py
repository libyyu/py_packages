# -*- coding: utf-8 -*-
#提供操作浏览器接口
import sys, os
from gzip import GzipFile
import re
import zlib
import json
#解决python版本兼容问题
from sys import version_info
if version_info < (3, 0):
    PY3 = False
elif version_info >= (3, 0):
    PY3 = True

if not PY3:
    try:
        from StringIO import StringIO
    except ImportError:
        import cStringIO as StringIO
    import urllib
    import cookielib
    from urllib2 import BaseHandler, addinfourl, HTTPCookieProcessor, build_opener, install_opener, HTTPHandler, HTTPSHandler
else:
    from io import BytesIO as StringIO
    from http import cookiejar as cookielib
    from urllib.request import BaseHandler, HTTPCookieProcessor, build_opener, install_opener, HTTPHandler, HTTPSHandler
    from urllib.response import addinfourl


#reload(sys)
#sys.setdefaultencoding('utf8')

def to_utf8(text):
    if sys.version_info >= (3, 0) and isinstance(text, str):
        return text.encode('utf-8')
    elif sys.version_info < (3, 0) and isinstance(text, unicode):
        return text.encode('utf-8')
    else:
        return text

def deflate(data):
    try:
        return zlib.decompress(data, -zlib.MAX_WBITS)
    except zlib.error:
        return zlib.decompress(data)

class ContentEncodingProcessor(BaseHandler):
    """docstring for ContentEncodingProcessor"""
    def http_request(self, req):
        #req.add_header('Accept-Encoding','gzip, deflate')
        #req.add_header('Transfer-encoding', 'gzip, deflate')
        return req

    def http_response(self, req, resp):
        old_resp = resp
        if resp.headers.get('content-encoding') == 'gzip':
            gz = GzipFile(fileobj = StringIO(resp.read()), mode='r')
            resp = addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
        if resp.headers.get('content-encoding') == 'deflate':
            gz = StringIO(deflate(resp.read()))
            resp = addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
        return resp

DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept-Encoding": "gzip, deflate",
        #"Connection":"keep-alive"
    }

def getOpener():
    cj = cookielib.CookieJar()
    cookie_support = HTTPCookieProcessor(cj)
    encoding_support = ContentEncodingProcessor()
    opener = build_opener(cookie_support, encoding_support, HTTPHandler, HTTPSHandler)
    install_opener(opener)
    return opener

_g_opener = None

def search(url, data = None, header=DEFAULT_HEADERS, timeout=10*3):
    global _g_opener
    if not _g_opener:
        _g_opener = getOpener()
    if header:
        headers = []
        for (k, v) in header.items():
            headers.append((k, v))
        _g_opener.addheaders = headers   
    if not PY3 and data:
        data = urllib.urlencode(data)
    elif PY3 and data:
        data = bytes(json.dumps(data), encoding="utf-8")
    response = _g_opener.open(url, data = data, timeout=timeout)
    return response
    

def getBrowser():
    import mechanize
    # Browser
    br = mechanize.Browser()
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(True, max_time=1)
    # Want debugging messages?
    #br.set_debug_http(True)
    br.set_debug_redirects(True)
    br.set_debug_responses(True)
    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    return br

def test():
    url_host = "http://10.236.100.108/seven_global/fabu/android/cgi"
    br = getBrowser()
    # Open some site, let's pick a random one, the first that pops in mind:
    try:
        r = br.open(url_host + "/upload.cgi")
    except Exception as e:
        raise e
    html = r.read()
    # Show the source
    flib.printf( toUTF8(html) )
    # or
    #print br.response().read()
    # Show the html title
    flib.printf( br.title() )
    return
    # Show the response headers
    #print r.info()
    # or
    #print br.response().info()
    # Show the available forms
    for f in br.forms():
        flib.printf( f )
    # Select the first (index zero) form
    br.select_form(nr=0)
    # Let's search
    br.submit(name='submit')
    flib.printf( toUTF8(br.response().read()) )
    # Looking at some results in link format
    for l in br.links(url_regex='stockrt'):
        flib.printf( l )

    # If the protected site didn't receive the authentication data you would
    # end up with a 410 error in your face
    br.add_password('http://safe-site.domain', 'username', 'password')
    br.open('http://safe-site.domain')



    # Testing presence of link (if the link is not found you would have to
    # handle a LinkNotFoundError exception)
    br.find_link(text='Weekend codes')
    # Actually clicking the link
    req = br.click_link(text='Weekend codes')
    br.open(req)
    flib.printf( br.response().read() )
    flib.printf( br.geturl() )
    # Back
    br.back()
    flib.printf( br.response().read() )
    flib.printf( br.geturl() )

def test2():
    header = {"Cookie":"JSESSIONID=ABAAABAAADEAAFIF0390879C909ED6B25B79466EE283BE3; _ga=GA1.2.417433648.1513319104; _gid=GA1.2.1618013105.1513319104; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1513319105; user_trace_token=20171215142351-84d77e04-e160-11e7-9a0b-525400f775ce; LGSID=20171215142351-84d782ed-e160-11e7-9a0b-525400f775ce; PRE_UTM=m_cf_cpt_baidu_pc; PRE_HOST=bzclk.baidu.com; PRE_SITE=http%3A%2F%2Fbzclk.baidu.com%2Fadrc.php%3Ft%3D06KL00c00f7Ghk60yUKm0FNkUs0dpWPp00000PW4pNb00000zJBmtg.THL0oUhY1x60UWdBmy-bIfK15yRvujDYnvf3nj0snADdrAm0IHYznDNAf1mdPbD3wjDvPjmkn1c3PHfsPYf3nRfsP16zw0K95gTqFhdWpyfqn101n1csPHnsPausThqbpyfqnHm0uHdCIZwsT1CEQLILIz4_myIEIi4WUvYE5LNYUNq1ULNzmvRqUNqWu-qWTZwxmh7GuZNxTAn0mLFW5HRLrjDL%26tpl%3Dtpl_10085_15730_11224%26l%3D1500117464%26attach%3Dlocation%253D%2526linkName%253D%2525E6%2525A0%252587%2525E9%2525A2%252598%2526linkText%253D%2525E3%252580%252590%2525E6%25258B%252589%2525E5%25258B%2525BE%2525E7%2525BD%252591%2525E3%252580%252591%2525E5%2525AE%252598%2525E7%2525BD%252591-%2525E4%2525B8%252593%2525E6%2525B3%2525A8%2525E4%2525BA%252592%2525E8%252581%252594%2525E7%2525BD%252591%2525E8%252581%25258C%2525E4%2525B8%25259A%2525E6%25259C%2525BA%2526xp%253Did%28%252522m6c247d9c%252522%29%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FH2%25255B1%25255D%25252FA%25255B1%25255D%2526linkType%253D%2526checksum%253D220%26ie%3Dutf-8%26f%3D8%26tn%3Dbaidu%26wd%3D%25E6%258B%2589%25E5%258B%25BE%25E7%25BD%2591%26oq%3D%2525E6%25259D%2525AD%2525E5%2525B7%25259E%2525E7%252594%2525B5%2525E5%2525AD%252590%2525E7%2525A7%252591%2525E6%25258A%252580%2525E5%2525A4%2525A7%2525E5%2525AD%2525A6%26rqlang%3Dcn%26inputT%3D2518; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F%3Futm_source%3Dm_cf_cpt_baidu_pc; LGUID=20171215142351-84d785f4-e160-11e7-9a0b-525400f775ce; X_HTTP_TOKEN=352f0849051a7bc84ed05f3ba6808fe9; _putrc=7E09D7EE60C821B7; login=true; unick=%E5%90%B4%E4%BF%8A%E4%BA%9A; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; index_location_city=%E5%8C%97%E4%BA%AC; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1513319596; LGRID=20171215143204-aa3d51ef-e161-11e7-9a28-525400f775ce; TG-TRACK-CODE=index_search",
            "Host": "www.lagou.com",
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90?city=%E5%8C%97%E4%BA%AC&cl=false&fromSearch=true&labelWords=&suginput=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
    data = {'first': 'true', 'pn': 1, 'kd': '开发工程师'}
    url = 'http://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
    resp = search(url, header=header, data=data)
    data = resp.read()
    print (data)
    with open('common_handler_baidu.html', 'wb') as f:
        f.write(data)
    jdata = json.loads(data)
    print (jdata)

if __name__ == '__main__':
    test2()