from flask import Flask, jsonify
from typing import List, Dict
import datetime
import menu_parsers

app = Flask(__name__)

@app.route('/')
def serve():
    date = '19 avg'
    interspar_vic_menu = menu_parsers.interspar_vic(date)

    json_menu_items = [convert_menu_to_api_element(menu) for menu in get_all_menus()]

    response = {'text': 'Here are your lunch menus:',
                'extra_responses': json_menu_items,
                'response_type': 'in_channel'}

    return jsonify(response)

def convert_menu_to_api_element(menu_items: List[str]) -> Dict[str,str]:
    menu_text = '\n'.join(menu_items)

    return {'text': menu_text, 'response_type': 'in_channel'}

def get_all_menus() -> List[List[str]]:
    # Date formatting
    all_months = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "avg", "sep", "okt", "nov", "dec"]

    # Get date
    work_day = datetime.date.today().weekday() + 1

    if work_day > 5:
        work_day = 1

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    # Generate the right day format for each website 
    stud_preh_date = str("{:02d}".format(day))+" "+all_months[(month)-1]
    marjetka_date = str(day)+"."+str(month)+"."+str(year)
    viabona_date = marjetka_date
    barjan_date = str(day)+"."+str(month)
    loncek_kuhaj_date = work_day - 1
    kondor_date = work_day
    josko_date = menu_parsers.get_ijs_date(datetime.date.today().weekday() + 1)

    menus = []

    # FIXME: Studentska prehrana, barjan and IJS not working
    menus.append(menu_parsers.marjetica_tobacna(marjetka_date))
    menus.append(menu_parsers.via_bona(viabona_date))
    menus.append(menu_parsers.loncek_kuhaj(loncek_kuhaj_date))
    menus.append(menu_parsers.kondor(kondor_date))

    return menus

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
