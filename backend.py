import json
import datetime

with open("classData.json", "r") as f:
    data = json.load(f)

def now():
    dt = datetime.datetime.now()
    dt += datetime.timedelta(hours=10)

    t1 = datetime.datetime.strptime(data['T1']['termStart'], '%d/%m/%Y')
    t2 = datetime.datetime.strptime(data['T2']['termStart'], '%d/%m/%Y')
    t3 = datetime.datetime.strptime(data['T3']['termStart'], '%d/%m/%Y')

    if dt < t1:
        term = 'Summer'
    elif dt < t2:
        term = 'T1'
    elif dt < t3:
        term = 'T2'
    else:
        term = 'T3'

    termStart = datetime.datetime.strptime(data[term]['termStart'], '%d/%m/%Y')
    day = dt.strftime('%a')
    week = str(int((dt - termStart).days / 7 + 1))
    time = dt.strftime('%H:%M')

    print(f"Now is {term} Week {week} {day} {time}")

    return (term, week, day, time)


def vacantspaces(campus, term, week, day, time):
    result = []
    for building in data[term]:
        if building == 'termStart' or not building.startswith(campus):
            continue

        building_data = data[term][building]
        for room in data[term][building]:
            room_data = building_data[room]
            if week not in room_data:
                result.append({
                    'room': room_data['name'],
                    'from': '--:--',
                    'to': '--:--',
                })
                continue

            week_data = room_data[week]
            if day not in week_data:
                result.append({
                    'room': room_data['name'],
                    'from': '--:--',
                    'to': '--:--',
                })
                continue

            day_data = sorted(week_data[day], key=lambda x: x['end'])
            if len(day_data) == 0:
                result.append({
                    'room': room_data['name'],
                    'from': '--:--',
                    'to': '--:--',
                })
            elif time < day_data[0]['start']:
                result.append({
                    'room': room_data['name'],
                    'from': '--:--',
                    'to': day_data[0]['start'],
                })
            elif time >= day_data[-1]['end']:
                result.append({
                    'room': room_data['name'],
                    'from': day_data[-1]['end'],
                    'to': '--:--',
                })
            elif len(day_data) >= 2:
                for i, lesson in enumerate(day_data[0:-1]):
                    next_lesson = day_data[i+1]
                    if lesson['end'] <= time < next_lesson['start']:
                        result.append({
                            'room': room_data['name'],
                            'from': lesson['end'],
                            'to': next_lesson['start'],
                        })
                    break

    result.sort(key=lambda x: x['room'])
    return result