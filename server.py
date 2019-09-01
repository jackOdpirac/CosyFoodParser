from flask import Flask, jsonify, request
from typing import List, Dict
import datetime
from menu_parsers import MenuParsers

app = Flask(__name__)
parsers = MenuParsers()

@app.route('/')
def serve():
    """Default route that is run when the MM server connects to the API.

    Returns
    -------
    flask.Response
        Response with JSON containing lunch information.
    """

    if 'text' in request.args and 'help' in request.args.get('text'):
        return help_menu()

    if 'text' not in request.args:
        json_menu_items = [convert_menu_to_api_element(menu) for menu in get_all_menus()]
    else:
        # Specific restaurant was requested
        restaurant = request.args.get('text')
        json_menu_items = [convert_menu_to_api_element(get_menu(restaurant))]

    response = {'text': 'Here are your lunch menus:',
                'extra_responses': json_menu_items,
                'response_type': 'in_channel'}

    return jsonify(response)

def help_menu():
    """Return a help menu JSON.

    Returns
    -------
    flask.Response
        Response with JSON containing help.
    """

    help_text = "After the /lunch command you can specify a restaurant. " \
              + "If no restaurant is specified, all restaurant menus will be listed.\n" \
              + "The following restaurants are supported:\n" \
              + "- marjetica\n" \
              + "- viabona\n" \
              + "- loncekkuhaj\n" \
              + "- kondor"

    return jsonify({'text': help_text,
                   'response_type': 'in_channel'})

def convert_menu_to_api_element(menu_items: List[str]) -> Dict[str,str]:
    """Convert a list of menu options to a structure that can be converted into a JSON.

    Parameters
    ----------
    menu_items : List[str]
        List of menu options.

    Returns
    -------
    Dict[str,str]
        JSON representation of the menu options.
    """
    
    menu_text = '\n'.join(menu_items)

    return {'text': menu_text, 'response_type': 'in_channel'}

def get_all_menus() -> List[List[str]]:
    """Get a list of all menus.

    Returns
    -------
    List[List[str]]
        The first list represents different restaurants. The contained lists contain individual menu items.
    """

    # Get date
    work_day = datetime.date.today().weekday() + 1

    if work_day > 5:
        work_day = 1

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    # Generate the right day format for each website 
    stud_preh_date = "{:02d} {}".format(day, parsers.get_month_as_string(month))
    marjetka_date = "{}.{}.{}".format(day, month, year)
    viabona_date = marjetka_date
    barjan_date = "{}.{}".format(day, month)
    loncek_kuhaj_date = work_day - 1
    kondor_date = work_day
    josko_date = parsers.get_ijs_date(datetime.date.today().weekday() + 1)

    menus = []

    # FIXME: Studentska prehrana, barjan and IJS not working
    menus.append(parsers.marjetica_tobacna(marjetka_date))
    menus.append(parsers.via_bona(viabona_date))
    menus.append(parsers.loncek_kuhaj(loncek_kuhaj_date))
    menus.append(parsers.kondor(kondor_date))

    return menus

def get_menu(restaurant : str) -> List[str]:
    """Get the menu of a single restaurant.

    Parameters
    ----------
    restaurant : str
        Name of the restaurant

    Returns
    -------
    List[str]
        Menu items of the specified restaurant
    """

    # Get date
    work_day = datetime.date.today().weekday() + 1

    if work_day > 5:
        work_day = 1

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    if restaurant == "marjetica":
        date = "{}.{}.{}".format(day, month, year)
        return parsers.marjetica_tobacna(date)

    elif restaurant == "viabona":
        date = "{}.{}.{}".format(day, month, year)
        return parsers.via_bona(date)

    elif restaurant == "loncekkuhaj":
        date = work_day - 1
        return parsers.loncek_kuhaj(date)

    elif restaurant == "kondor":
        date = work_day
        return parsers.kondor(date)
    
    else:
        return []

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
