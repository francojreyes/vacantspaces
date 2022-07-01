import json
import os
from pprint import pprint
import re
import time

import cchardet
import lxml
import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from pymongo import MongoClient
from pymongo.server_api import ServerApi

data = {
        'Summer': {"termStart": "04/01/2022",},
        'T1': {"termStart": "14/02/2022",},
        'T2': {"termStart": "30/05/2022"},
        'T3': {"termStart": "12/09/2022"}
    }

def my_set(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def scrape(session):
    page = session.get('http://timetable.unsw.edu.au/2022/subjectSearch.html')
    links = re.findall(r'[A-Z]{8}.html', page.text)
    subject_links = my_set(links)
    for link in subject_links:
        scrape_subject(session, 'http://timetable.unsw.edu.au/2022/' + link)
        print('Scraped', 'http://timetable.unsw.edu.au/2022/' + link)

    # connect to mongodb
    from dotenv import load_dotenv
    load_dotenv()
    client = MongoClient(os.getenv('MONGODB_URL'), server_api=ServerApi('1'))
    db = client.vacantspaces
    db.classdata.replace_one({}, data)


def scrape_subject(session, url):
    page = session.get(url)
    links = re.findall(r'[A-Z]{4}[0-9]{4}.html', page.text)
    course_links = my_set(links)
    for link in course_links:
        scrape_course(session, 'http://timetable.unsw.edu.au/2022/' + link)


def scrape_course(session, url):
    page = session.get(url)
    strainer = SoupStrainer(class_="formBody")
    soup = BeautifulSoup(page.text, 'lxml', parse_only=strainer)

    body = list(soup.children)[-1]
    term_heads = body.find_all(is_heading, class_="classSearchSectionHeading")

    for head in term_heads:
        if 'SUMMER' in head.text:
            term = 'Summer'
        elif 'ONE' in head.text:
            term = 'T1'
        elif 'TWO' in head.text:
            term = 'T2'
        elif 'THREE' in head.text:
            term = 'T3'

        class_table = head.find_parent('table').next_sibling.next_sibling
        classes = class_table.find_all(class_='formBody')
        for class_ in classes:
            class_data = class_.find(class_='formBody')
            if not class_data or class_data.text == '':
                continue
            class_data = class_data.find_all(class_='data')[0:4]

            room_id = class_data[2].text.split()[-1].strip('( )')
            if room_id in ['ONLINE', 'SEESCHOOL', '']:
                continue
            if room_id not in data[term]:
                data[term][room_id] = {}
                data[term][room_id]['name'] = class_data[2].text.split('(')[0].strip()

            raw_weeks = class_data[3].text
            raw_weeks = raw_weeks.replace("N1", "6")
            raw_weeks = raw_weeks.replace("N2", "12")
            raw_weeks = raw_weeks.replace("N3", "13")
            raw_weeks = raw_weeks.replace("N4", "14")
            raw_weeks = raw_weeks.split(',')
            weeks = []
            for week in raw_weeks:
                try:
                    if '-' in week:
                        split = week.split('-')
                        for i in range(int(split[0]), int(split[-1]) + 1):
                            weeks.append(str(i))
                    else:
                        weeks.append(week.strip())
                except ValueError:
                    print("Something wacky with", url[-13:-5])

            for week in weeks:
                if week not in data[term][room_id]:
                    data[term][room_id][week] = {}

                raw_days = class_data[0].text
                for day in raw_days.split(','):
                    day = day.strip()
                    if day not in data[term][room_id][week]:
                        data[term][room_id][week][day] = []

                    raw_times = class_data[1].text.split('-')
                    class_ = {
                        'start': raw_times[0].strip(),
                        'end': raw_times[-1].strip()
                    }

                    if class_ not in data[term][room_id][week][day]:
                        data[term][room_id][week][day].append(class_)


def is_heading(tag):
    return isinstance(tag, Tag) and " - Detail" in tag.text

def is_link(href):
    link_regex = r'[A-Z]{4}([0-9]{4}|[A-Z]{4})\.html'
    return href and re.fullmatch(link_regex, href)

if __name__ == '__main__':
    s = time.perf_counter()
    session = requests.Session()
    scrape(session)
    elapsed = time.perf_counter() - s
    print(f"Scraped timetable in {elapsed//60:0.0f}m{elapsed%60:0.2f}s")
