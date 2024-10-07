from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsTheHindu
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Getting Latest News'

    def handle(self, *args, **kwargs):
        now = datetime.now()
        today = make_aware(now).date()
        self.stdout.write(self.style.HTTP_INFO(f'Starting Scraping from The Hindu today: {today}'))
        url = 'https://www.thehindu.com/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')

        for item in soup.find_all('h3'):
            news = {}
            news['headline'] = item.text.strip()
            if item.find_all('a'):
                news['link'] = item.find_all('a')[0]['href'].strip()
                news_response = requests.get(news['link'])
                news_soup = BeautifulSoup(news_response.text,'html.parser')
                sub_title = news_soup.find_all('h2',class_ = 'sub-title')

                if sub_title:
                    news['sub_title'] = sub_title[0].text.strip()
                else:
                    news['sub_title'] = sub_title

                publish_time = news_soup.find_all('p',class_='publish-time-new')
                if publish_time:
                    news['publish_time'] = publish_time[0].text.strip()
                else:
                    news['publish_time'] = publish_time
                
                author = news_soup.find_all('a',class_='person-name')
                if author:
                    news['author'] = author[0].text.strip()
                else:
                    news['author'] = author
                
                result = []
                visited_tags = set()

                for first_p in news_soup.find_all('p'):
                    if first_p in visited_tags:
                        continue

                    next_h4 = first_p.find_next_sibling('h4')
                    if next_h4 and next_h4 not in visited_tags:
                        second_p = next_h4.find_next_sibling('p')
                        if second_p and second_p not in visited_tags:
                            result.append(str(first_p))
                            result.append(str(next_h4))
                            result.append(str(second_p))

                            visited_tags.update([first_p,next_h4,second_p])
                
                formatted_html = ''.join(result)
                news['content'] = formatted_html

                saved, _ = NewsTheHindu.objects.get_or_create(**news)
    
        
        self.stdout.write(self.style.SUCCESS(f'Completed Scraping from The Hindu today: {today}'))
