import requests
from request_data import PostRequest


def fetch_groups(groupids, json_respone):
    groups = json_respone.get("r").get("dbiAccessorRes").get("tables")[12].get("data_rows")
    groups_list = []
    for group_id in groupids:
        for group in groups:
            if group['id'] == group_id:
                firstname = group.get("name")
                groups_list.append(firstname)
    return groups_list


def fetch_teachers(teacher_ids, json_respone):
    teachers = json_respone.get("r").get("dbiAccessorRes").get("tables")[14].get("data_rows")
    teachers_dict = []
    for teacher_id in teacher_ids:
        for teacher in teachers:
            if teacher['id'] == teacher_id:
                firstname = teacher.get("firstname")
                lastname = teacher.get("lastname")
                teachers_dict.append(lastname)
    return teachers_dict


def fetch_subject(subject_id, json_respone):
    subjects = json_respone.get("r").get("dbiAccessorRes").get("tables")[13].get("data_rows")

    for subject in subjects:
        if subject['id'] == subject_id:
            subject_name = subject.get("name")
            return subject_name


def action(user_group):
    url = 'https://ttpu.edupage.org/timetable/server/regulartt.js?__func=regularttGetData'
    post_data = PostRequest()

    json_respone = requests.post(url, headers=post_data.headers, json=post_data.payload).json()

    # p = json_respone.get("r").get("dbiAccessorRes").get("tables")[1].get("data_rows")
    # for o in p:
    #     period = o.get("name")
    #     starttime = o.get("starttime")
    #     endtime = o.get("endtime")
    #     # print(f"{period}:  {starttime} - {endtime}")

    rooms_data = json_respone.get("r").get("dbiAccessorRes").get("tables")[11].get("data_rows")
    cards_data = json_respone.get("r").get("dbiAccessorRes").get("tables")[20].get("data_rows")
    groups_data = json_respone.get("r").get("dbiAccessorRes").get("tables")[12].get("data_rows")
    lessons_data = json_respone.get("r").get("dbiAccessorRes").get("tables")[18].get("data_rows")
    subjects_data = json_respone.get("r").get("dbiAccessorRes").get("tables")[13].get("data_rows")

    groups = {group_data["name"]: group_data["id"] for group_data in groups_data}
    if user_group in groups:
        group_id = groups[user_group]
    else:
        return  # user class not found

    user_group_lessons = []
    for lesson_data in lessons_data:
        if group_id in lesson_data["classids"]:
            user_group_lessons.append(lesson_data)

    user_group_lessons_detailed = {}

    for lesson in user_group_lessons:
        # room_names = []
        # rooms = lesson.get("classroomidss")
        # print(lesson.get("id"))
        # print(rooms)
        # for room_data in rooms_data:
        #     if room_data["id"] in rooms:
        #         room_names.append(room_data.get("name"))

        for subject_data in subjects_data:
            if subject_data["id"] == lesson["subjectid"]:
                subject_name = subject_data["name"]
                subject_short = subject_data["short"]
                subject_color = subject_data["color"]

                # user_group_lessons_detailed[lesson["id"]] = {
                #     "subject_id": lesson["subjectid"],
                #     "subject_name": subject_data["name"],
                #     "subject_short": subject_data["short"],
                #     "subject_color": subject_data["color"],
                #     "cards": []
                # }
                break

        user_group_lessons_detailed[lesson["id"]] = {
            "subject_id": lesson["subjectid"],
            "subject_name": subject_name,
            "subject_short": subject_short,
            "subject_color": subject_color,
            # "rooms": room_names,
            "cards": []
        }

    for card_data in cards_data:
        lesson_id = card_data["lessonid"]
        if lesson_id in user_group_lessons_detailed:
            card = {}

            lesson_data = user_group_lessons_detailed[lesson_id]
            day = card_data["days"]
            if day:
                if day == "100000":
                    day = "Monday"
                elif day == "010000":
                    day = "Tuesday"
                elif day == "001000":
                    day = "Wednesday"
                elif day == "000100":
                    day = "Thursday"
                elif day == "000010":
                    day = "Friday"
                elif day == "000001":
                    day = "Saturday"
                card["day"] = day
            if card_data["period"]:
                card["period"] = card_data["period"]

            if card:
                rooms = card_data["classroomids"]
                # print(rooms)
                if rooms:
                    room_names = []
                    for room_data in rooms_data:
                        if room_data["id"] in rooms:
                            room_names.append(room_data.get("name"))
                    card['rooms'] = room_names

                card["id"] = card_data["id"]
                cards = lesson_data["cards"]
                cards.append(card)

    for lesson in user_group_lessons_detailed:
        current_lesson_data = user_group_lessons_detailed.get(lesson)
        subject_name = current_lesson_data.get("subject_name")
        reserved_card = current_lesson_data.get("cards")

        if bool(reserved_card):
            for card in reserved_card:
                print(subject_name)
                print(current_lesson_data.get("subject_short"))
                print(card.get("rooms"))
                print(card.get("day"))
                print(card.get("period"))
                print()


if __name__ == '__main__':
    action(user_group="G1")
