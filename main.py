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
    timetable_df = pd.DataFrame(
        columns=pd.MultiIndex.from_arrays([[1, 2, 3, 4, 5, 6], ["8:30-9:50  ", "10:00-11:20  ", "11:30-12:50", "13:50-15:10", "15:20-16:40", "18:20-19:40"]]),
        index=days_of_week
    )
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
                timetable_df.at[card.get("day"), int(
                    card.get("period"))] = f'<b>{current_lesson_data.get("subject_short")}</b><br><p style="font-size: 70%;">{rooms}</p>'

    timetable_df.to_csv("new.csv")

    import hashlib

    def string_to_color(input_string):
        hash_object = hashlib.md5(input_string.encode())
        hash_hex = hash_object.hexdigest()
        r = (int(hash_hex[0:2], 16) + 128) % 255
        g = (int(hash_hex[2:4], 16) + 128) % 255
        b = (int(hash_hex[4:6], 16) + 128) % 255
        color_string = f"rgb({r}, {g}, {b})"
        return color_string

    def style_cells(val):
        if val == "...":
            b_col = "white"
            f_col = "white"
        else:
            b_col = string_to_color(val.split("<br>")[0])
            f_col = "black"
        return f'background-color: {b_col}; color: {f_col}'

    styler = timetable_df.style
    df = styler.map(style_cells)

    df = df.set_properties(**{'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'})

    dfi.export(df, "mytable.png")


if __name__ == '__main__':
    action(user_group="IT4-20")
