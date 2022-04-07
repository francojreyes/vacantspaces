import requests
import json
import time

def scrape():
    data = {}
    data['Summer'] = requests.get('https://timetable.csesoc.unsw.edu.au/api/terms/2022-Summer/freerooms/').json()
    data['T1'] = requests.get('https://timetable.csesoc.unsw.edu.au/api/terms/2022-T1/freerooms/').json()
    data['T2'] = requests.get('https://timetable.csesoc.unsw.edu.au/api/terms/2022-T2/freerooms/').json()
    data['T3'] = requests.get('https://timetable.csesoc.unsw.edu.au/api/terms/2022-T3/freerooms/').json()

    with open('classData.json', 'w') as FILE:
        json.dump(data, FILE, indent=4)

if __name__ == '__main__':
    scrape()
    time.sleep(60*60*24)