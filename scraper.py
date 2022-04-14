from bs4 import BeautifulSoup, Tag
import requests
import json
import time

data = {
        'Summer': {"termStart": "03/01/2022",},
        'T1': {"termStart": "14/02/2022",},
        'T2': {"termStart": "30/05/2022"},
        'T3': {"termStart": "12/09/2022"}
    }

def scrape():
    url = 'http://timetable.unsw.edu.au/2022/subjectSearch.html'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    subject_links = soup.find_all('a', href=is_link)
    subject_links = set(link['href'] for link in subject_links)
    for link in subject_links:
        print('scraping', 'http://timetable.unsw.edu.au/2022/' + link)
        scrape_subject('http://timetable.unsw.edu.au/2022/' + link)

    with open('classData.json', 'w') as FILE:
        json.dump(data, FILE, indent=4)


def scrape_subject(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    course_links = soup.find_all('a', href=is_link)
    course_links = set(link['href'] for link in course_links)
    for link in course_links:
        scrape_course('http://timetable.unsw.edu.au/2022/' + link)


def scrape_course(url):
    print('scraping', url)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    body = soup.find_all(class_="formBody", limit=2)[-1]
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
            raw_weeks.replace("N1", "6")
            raw_weeks.replace("N2", "12")
            raw_weeks.replace("N3", "13")
            raw_weeks.replace("N4", "14")
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
    return href and '.html' in href and href.split('.')[0].isupper()

if __name__ == '__main__':
    scrape()
    print('Scraped data from CSESoc API')
    time.sleep(60*60*24)