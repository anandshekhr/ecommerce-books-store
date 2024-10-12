from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsTheHindu
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.timezone import make_aware
import time
import html


class Command(BaseCommand):
    help = 'Getting Latest News'

    import time

    def fetch_paragraphs_with_retry(self, news_soup, retries=3, delay=20):
        result = []
        visited_tags = set()

        for attempt in range(retries):
            first_p_tags = news_soup.find_all('p')

            # If we find no 'p' tags, wait and retry
            if not first_p_tags:
                # print(f"Attempt {attempt + 1} failed: No 'p' tags found. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue  # Retry the loop
            
            # If 'p' tags are found, process them
            for first_p in first_p_tags:
                if first_p in visited_tags:
                    continue

                result.append(str(first_p))
                visited_tags.update(str(first_p))
                next_h4 = first_p.find_next_sibling('h4')
                if next_h4 and next_h4 not in visited_tags:
                    result.append(str(next_h4))
                    visited_tags.update(str(next_h4))
                    second_p = next_h4.find_next_sibling('p')
                    if second_p and second_p not in visited_tags:
                        result.append(str(second_p))

                        visited_tags.update(str(second_p))

            # If result is found, break out of the retry loop
            if result:
                break
            # else:
            #     print(f"Attempt {attempt + 1} completed but no results found. Retrying...")

        # if not result:
        #     print("Failed to fetch any data after multiple attempts.")
        
        return result


    def handle(self, *args, **kwargs):
        now = datetime.now()
        today = make_aware(now).date()
        self.stdout.write(self.style.HTTP_INFO(f'Starting Scraping from The Hindu today: {today} at: {make_aware(now).time()}'))
        url = 'https://www.thehindu.com/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')

        for item in soup.find_all('h3'):
            news = {}
            news['headline'] = item.text.strip()
            if item.find_all('a'):
                news['link'] = item.find_all('a')[0]['href'].strip()

                # Introduce a delay before fetching the article content
                news_response = requests.get(news['link'])
                time.sleep(20) 

                news_soup = BeautifulSoup(news_response.text,'html.parser')
                sub_title = news_soup.find_all('h2',class_ = 'sub-title')

                if sub_title:
                    news['sub_title'] = sub_title[0].text.strip()
                else:
                    news['sub_title'] = None

                publish_time = news_soup.find_all('p',class_='publish-time-new')
                if publish_time:
                    news['publish_time'] = publish_time[0].text.strip()
                else:
                    news['publish_time'] = None

                author = news_soup.find_all('a',class_='person-name')
                if author:
                    news['author'] = author[0].text.strip()
                else:
                    news['author'] = None

                
                result = self.fetch_paragraphs_with_retry(news_soup)

                formatted_html = ''.join(item.replace('‘', '\'').replace('’', '\'') for item in result)
                news['content'] = formatted_html
                try:
                    obj, created = NewsTheHindu.objects.update_or_create(
                        # headline = news['headline'],
                        link=news['link'],  # unique field
                        defaults=news  # fields to update or set
                    )
                except:
                    pass


        self.stdout.write(self.style.SUCCESS(f'Completed Scraping from The Hindu today: {today} at: {make_aware(datetime.now()).time()}'))
