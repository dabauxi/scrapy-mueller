# -*- coding: utf-8 -*-
import scrapy
import json


def parse_product_entry(response):
    prod_name = response.selector.css(".mu-sale-box__headline").get()
    if not prod_name:

        return
    prod_name = prod_name[prod_name.find("\n") + 2:prod_name.rfind("<")].strip()
    feature_table = response.selector.css("#features")
    tds = feature_table.xpath("//td")
    prod_ingredients = ""
    for i in range(len(tds)):
        td = tds[i]
        if "Inhaltsstoffe" in td.get():
            prod_ingredients = tds[i+1].get()
            break

    if not prod_ingredients:
        return

    prod_ingredients = prod_ingredients[prod_ingredients.find("\n") + 2:prod_ingredients.rfind("<")].strip()
    prod_ingredients.replace("/", ",")
    print(prod_name)
    print(prod_ingredients)
    with open(f'./mueller/results/{prod_name}.json', 'w') as outfile:
        json.dump({"name": prod_name, "ingredients": prod_ingredients}, outfile)


class MuellerSpider(scrapy.Spider):
    BASE_URL = "https://www.mueller-drogerie.at"
    name = 'search_spider'
    allowed_domains = ['mueller-drogerie.at']

    def start_requests(self):
        products = {
            "drogerie/pflege/haarpflege/haarwaesche/",
        }

        urls = [f"{MuellerSpider.BASE_URL}/{product}" for product in products]
        for product in products:
            for i in range(2, 300):
                urls.append(f"https://www.mueller-drogerie.at/{product}?p={i}")
        for url in urls:
            yield scrapy.Request(url, self.parse_site)

    def parse_site(self, response):
        urls = set()
        for i in range(1, 61):
            prod_box = response.selector.xpath(f"/html/body/div/div[2]/main/div[2]/div/div/div[2]/div[{i}]/div/a").get()
            if not prod_box:
                return
            href = prod_box[prod_box.find("href=")+6:]
            href = href[:href.find('"')]
            urls.add(f"{MuellerSpider.BASE_URL}{href}")

        for url in urls:
            request = scrapy.Request(url=url, callback=parse_product_entry)
            yield request
