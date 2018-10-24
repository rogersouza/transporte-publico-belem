import scrapy
import time
from linhas_belem.items import OnibusInfoItem

class LinhasOnibusSpider(scrapy.Spider):
    name = 'linhas_onibus'
    allowed_domains = ['moovitapp.com']
    start_urls = ['https://moovitapp.com/index/pt-br/transporte_p%C3%BAblico-lines-Belem-1-3183-971095']

    def parse(self, response):
        busline_name_selector = response.css('div.info-link a span::text')
        busline_link_selector = response.css('a[itemprop=url]::attr(href)')

        for busline_name, busline_link in zip(busline_name_selector, busline_link_selector):
            busline_link = self._format_url(busline_link.extract())
            busline_name = busline_name.extract()

            yield scrapy.Request(
                url=busline_link,
                callback=self.parse_bus_list_page,
                meta={"busline": busline_name}
            )

    def parse_bus_list_page(self, response):
        for bus_name in response.css('span.line-title::text'):
                item = OnibusInfoItem()
                item['linha'] = response.meta.get('busline')
                item['nome'] = bus_name.extract()
                yield item
        
        if self._has_next_page(response):
            
            next_page_link = self._get_next_page_link(response)

            yield scrapy.Request(
                url=next_page_link,
                callback=self.parse_bus_list_page,
                meta={"busline": response.meta.get('busline')}
            )

    def _get_next_page_link(self, response):
        next_page_partial_link = response.css('a.pagination-link.next::attr(href)').extract()
        next_page_link = self._format_url(next_page_partial_link)

        return next_page_link

    def _has_next_page(self, response):
        next_page_button = response.css('a.pagination-link.next').extract()
        
        if next_page_button:
            return True
        return False

    def _format_url(self, partial_url):
        url = f"https://{self.allowed_domains[0]}/index/pt-br/{partial_url}"
        return url