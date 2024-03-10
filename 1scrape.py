############################ 
# Dependencies
############################
# requests
# pyppeteer
############################
# pip install requests pyppeteer
############################
import time
import requests

import urllib.parse
import urllib.request
import os
import asyncio
from pyppeteer import launch

URL_PREFIX = "https://deps.mofe.gov.bn"
URL_SUFFIX = "/DEPD%20Documents%20Library/Forms/AllItems.aspx?RootFolder=%2FDEPD%20Documents%20Library%2FKH%2Fcars&FolderCTID=0x01200054D7905F1114F84892C81BDC2CC4C7CE&View={4DDE193B-C0DA-4E84-838E-C66D84EA697D}"

async def asyncScrapeFolder(pathEndpoint, page):
    url = URL_PREFIX + pathEndpoint
    print("  GET %s / %s" % ( url, pathEndpoint ))

    await page.goto(url)

    links = []

    while True:
        elements = await page.querySelectorAll('#contentBox td.ms-vb-title a')
        for a in elements:
            link = await page.evaluate('(element) => element.href', a)
            #linkpath = urllib.parse.unquote(link.replace(URL_PREFIX,""))
            linkpath = link.replace(URL_PREFIX,"")
            links.append(linkpath)

        # TODO: There are 30 rows for a page so click next button. There should probably be a better way than this
        if len(elements) != 30: 
            break

        await page.click('#contentBox .ms-commandLink.ms-promlink-button.ms-promlink-button-enabled')
        await page.waitForNavigation({"waitUntil" : "networkidle2"})

    return links


async def asyncScrapeSubFolders(pathEndpoint, page):
    print("GET SF %s" % ( pathEndpoint ))
    links = await asyncScrapeFolder(pathEndpoint, page)
    print("  links: (%s) %s" % (len(links), links))
    time.sleep(2)
    for link in links:
        encodedPath = link
        if encodedPath.lower().endswith(".pdf"):
            downloadPdf(urllib.parse.unquote(encodedPath))
        else:
            await asyncScrapeSubFolders(encodedPath, page)

def downloadPdf(unencodedPath):
  url = URL_PREFIX + urllib.parse.quote(unencodedPath)
  print("Download %s" % (url))
  rawPaths = unencodedPath.split("/")
  fullpath = os.path.join(*rawPaths)
  rawPaths.pop()
  filepath = os.path.join(*rawPaths)
  if os.path.exists(fullpath):
    print("Download exists. Skipping")
    return

  time.sleep(1)
  if not os.path.exists(filepath):
      os.makedirs(filepath)
  urllib.request.urlretrieve(url, fullpath)


async def main():
    browser = await launch({'headless': True})
    page = await browser.newPage()
    await asyncScrapeSubFolders(URL_SUFFIX, page)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())