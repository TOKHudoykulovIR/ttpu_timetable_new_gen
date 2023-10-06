import requests
from request_data import PostRequest
import pandas as pd
import dataframe_image as dfi

def action(user_group):
    url = 'https://ttpu.edupage.org/timetable/server/regulartt.js?__func=regularttGetData'
    post_data = PostRequest()

    json_respone = requests.post(url, headers=post_data.headers, json=post_data.payload).json()

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
        subject_name = None
        subject_short = None
        subject_color = None

        for subject_data in subjects_data:
            if subject_data["id"] == lesson["subjectid"]:
                subject_name = subject_data["name"]
                subject_short = subject_data["short"]
                subject_color = subject_data["color"]
                break

        if subject_name:
            user_group_lessons_detailed[lesson["id"]] = {
                "subject_id": lesson["subjectid"],
                "subject_name": subject_name,
                "subject_short": subject_short,
                "subject_color": subject_color,
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
                if rooms:
                    room_names = []
                    for room_data in rooms_data:
                        if room_data["id"] in rooms:
                            room_names.append(room_data.get("name"))
                    card['rooms'] = room_names

                card["id"] = card_data["id"]
                cards = lesson_data["cards"]
                cards.append(card)

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    lesson_numbers = list(range(1, 7))  # Assuming 6 lessons per day
    timetable_df = pd.DataFrame(columns=lesson_numbers, index=days_of_week)
    for day in days_of_week:
        for lesson in lesson_numbers:
            # Get the lesson details (you can replace this with your own data source)
            lesson_details = "..."
            # Fill in the DataFrame
            timetable_df.at[day, lesson] = lesson_details

    for lesson in user_group_lessons_detailed:
        current_lesson_data = user_group_lessons_detailed.get(lesson)
        subject_name = current_lesson_data.get("subject_name")
        reserved_card = current_lesson_data.get("cards")

        if bool(reserved_card):
            for card in reserved_card:
                # print(subject_name)
                # print(current_lesson_data.get("subject_short"))
                # print(current_lesson_data.get("subject_color"))
                # print(card.get("rooms"))
                # print(card.get("day"))
                # print(card.get("period"))
                # print()
                rooms = ', '.join(map(str, card.get("rooms")))
                timetable_df.at[card.get("day"), int(card.get("period"))] = f'{current_lesson_data.get("subject_short")}<br>{rooms}<br>{current_lesson_data.get("subject_color")}'

    timetable_df.to_csv("new.csv")


    def style_cells(val):
        if val == "...":
            col = "white"
        else:
            col = val.split("<br>")[2]
        return f'background-color: {col}'

    # ss = timetable_df.style.map(style_cells)

    dfi.export(timetable_df.style.map(style_cells), "mytable.png", table_conversion="matplotlib")


if __name__ == '__main__':
    action(user_group="G4")
