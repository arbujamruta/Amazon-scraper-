import scrapy
from lxml import html


def remove_empty(l):
    i = len(l) - 1
    while (i >= 0):
        l[i] = l[i].strip()
        if l[i] == "":
            l.pop(i)
        i = i - 1
    return l

def normalize_whitespace(str):
    import re
    str = str.strip()
    str = re.sub(r'\s+', ' ', str)
    return remove_en(str)

def normalize_whitespace_list(lis):
    import re
    lis2 = []
    for str in lis:
        str = str.strip()
        str = re.sub(r'\s+', ' ', str)
        if str!="":
            lis2.append(remove_en(str))
    return lis2

def remove_en(str):
    return str.encode("ascii", "ignore").decode().strip()

def convert_num(str):
    s=""
    for i in str:
        if i.isdigit():
            s += i
    return int(s)


class ExampleSpider(scrapy.Spider):
    name = "amazon"

    def start_requests(self):
        links = []
        l = "https://www.amazon.in/s?k=bags&page=2&crid=2EPPM1MX5J2JV&qid=1675314228&sprefix=bag%2Caps%2C551&ref=sr_pg_1"

        for i in range(1,21):
            links.append(l.replace("&page=2","&page="+str(i)))
        headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        'upgrade-insecure-requests': 1,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

        for i in range(len(links)):
            yield scrapy.Request(links[i],callback=self.parse_item_links)

    def parse_item_links(self,response):
        prices = response.xpath('//div[@data-component-type="s-search-result"]//div[@class="a-section a-spacing-none a-spacing-top-micro s-price-instructions-style"]')
        title = response.xpath('//div[@data-component-type="s-search-result"]//span[@class="a-size-medium a-color-base a-text-normal"]/text()').getall()
        no_of_reviews = response.xpath('//div[@data-component-type="s-search-result"]//span[@class="a-size-base s-underline-text"]/text()').getall()
        product_links = response.xpath('//div[@data-component-type="s-search-result"]//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href').getall()
        #rating = response.xpath('//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div/div/div/div/div/div/div[2]/div/div/div[2]/div/span[1]/span[3]/a/i[1]/span').getall()
        rating = response.xpath('//div[@data-component-type="s-search-result"]//div[@class="a-row a-size-small"]/span[1]/@aria-label').getall()
        for i in range(len(prices)):
            tree = html.fromstring(prices[i].get())
            prod_price = tree.xpath('//span[@class="a-price-whole"]/text()')
            #print(len(title), len(prices), len(no_of_reviews), len(product_links),len(rating))
           # print(title[i],prod_price,no_of_reviews[i],product_links[i])
            yield scrapy.Request("https://www.amazon.in"+product_links[i],meta={"title":title[i],"price":prod_price
                                                                                ,"reviews":no_of_reviews[i],"rating":rating[i].split()[0]})

        # next = response.xpath('//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href').get()
        #
        # if next:
        #     yield scrapy.Request("https://www.amazon.in"+next,callback=self.parse_item_links)



    def parse(self, response):
        features = response.xpath('//div[@id="feature-bullets"]/ul/li//text()').getall()
        product_description = response.xpath('//div[@id="productDescription"]//text()').getall()
        product_description = remove_empty(product_description)
        pd_key = response.xpath('//table[@id="productDetails_techSpec_section_1"]//tr/th/text()').getall()
        pd_value = response.xpath('//table[@id="productDetails_techSpec_section_1"]//tr/td/text()').getall()

        pd_key = remove_empty(pd_key)
        pd_value = remove_empty(pd_value)


        # i = len(pd_key)-1
        # while(i>=0):
        #     pd_key[i] = pd_key[i].strip()
        #     if pd_key[i] == "":
        #         pd_key.pop(i)
        #         i=i+1
        #     i=i-1
        #
        # i = len(pd_value)-1
        # while(i>=0):
        #     pd_value[i] = pd_value[i].strip()
        #     if pd_value[i] == "":
        #         pd_value.pop(i)
        #         i=i+1
        #     i=i-1

        d = {}
        for i in range(len(pd_key)):
            d[normalize_whitespace(pd_key[i]).replace(":","")] = normalize_whitespace(pd_value[i]).replace(":","")

        d['product_description'] = product_description

        product_description_text = response.xpath('//div[@class="aplus-v2 desktop celwidget"]//*[self::h3 or self::h1 or self::h2 or self::h4 or self::h5 or self::h6 or self::p]//text()').getall()
        product_description_text = normalize_whitespace_list(product_description_text)

        d["from_manufacturer_text"] = product_description_text

        # ad_key = response.xpath('//table[@id="productDetails_detailBullets_sections1"]//tr/th/text()')
        # ad_value = response.xpath('//table[@id="productDetails_detailBullets_sections1"]//tr/td/text()')
        #
        # print(ad_key)
        # print(ad_value)
        # ad_key = remove_empty(ad_key)
        # ad_value = remove_empty(ad_value)



        # for i in range(len(ad_key)):
        #     print(len(ad_key))
        #     d[ad_key[i]] = ad_value[i]

        add_rows = response.xpath('//table[@id="productDetails_detailBullets_sections1"]//tr')

        for i in add_rows:
            d[normalize_whitespace(i.css('th::text').get().strip().replace(":",""))] = normalize_whitespace(i.css('td::text').get().strip())

        product_detail_rows = response.xpath('//div[@id="detailBullets_feature_div"]/ul/li')

        for i in product_detail_rows:
            d[normalize_whitespace(i.css('span.a-text-bold::text').get()).replace(":","").strip()] = normalize_whitespace(i.css('span:nth-child(2)::text').get())


        # If Prices in Range
        prices = []
        for i in response.meta['price']:
            prices.append(convert_num(i))

        try:
            manu = d['Manufacturer']
        except:
            manu=""
        print("Dictonary : ",d)



        yield {
            "Product_Name":response.meta['title'],
            "Number_Of_Reviews": convert_num(response.meta['reviews']),
            "Rating": float(response.meta['rating']),
            "Product_Price": prices,
            "Product_URL":response.url,
            "Description":features,
            "ASIN": d['ASIN'],
            "Product_Description_Table":d,
            "Manufacturer":manu
        }


