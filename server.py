from flask import Flask, jsonify, request
from typing import List, Dict, Tuple
import datetime
import os
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

    if 'text' not in request.args or request.args.get('text') == "":
        json_menu_items = [convert_menu_to_api_element(menu, name, False) for name, menu in get_all_menus()]
        all_menus = True
    else:
        # Specific restaurant was requested
        restaurant = request.args.get('text')
        json_menu_items = [convert_menu_to_api_element(get_menu(restaurant), convert_user_command_to_restaurant_name(restaurant), True)]
        all_menus = False

    text = "Here are your lunch menus. To learn more about how to use this bot, use the ```/lunch help``` command."

    response = {'text': text,
                'extra_responses': json_menu_items}

    if not all_menus:
        response['response_type'] = 'in_channel'

    return jsonify(response)

def help_menu():
    """Return a help menu JSON.

    Returns
    -------
    flask.Response
        Response with JSON containing help.
    """

    help_text = "At the end of the /lunch command you can specify a restaurant. " \
              + "If no restaurant is specified, all restaurant menus will be listed.\n" \
              + "The following restaurants are supported:\n" \
              + "- ```hombre```\n" \
              + "- ```marjetica```\n" \
              + "- ```viabona```\n" \
              + "- ```loncekkuhaj```\n" \
              + "- ```kondor```\n" \
              + "- ```dd``` or ```dijaskidom```\n" \
              + "- ```barjan```\n" \
              + "- ```fe```\n" \
              + "- ```kurjitat```\n" \
              + "- ```spar```\n" \
              + "- ```ijs```\n" \
              + "- ```coolhouse``` or ```cool```\n" \
              + "Example: ```/lunch barjan```\n" \
              + "\n" \
              + "You can contribute to the project here: https://github.com/jackOdpirac/CosyFoodParser"

    return jsonify({'text': help_text,
                   'response_type': 'in_channel'})

def convert_menu_to_api_element(menu_items: List[str], name: str, in_channel: bool) -> Dict[str,str]:
    """Convert a list of menu options to a structure that can be converted into a JSON.

    Parameters
    ----------
    menu_items : List[str]
        List of menu options.

    name : str
        Name of the restaurant

    Returns
    -------
    Dict[str,str]
        JSON representation of the menu options.
    """

    menu_text = '## {}\n'.format(name) if name is not None else ''
    
    try:
        menu_text += '\n'.join(menu_items)
    except TypeError:
        menu_text += str(menu_items)

    return_value = {'text': menu_text}

    if in_channel:
        return_value['response_type'] = 'in_channel'

    return return_value

def get_all_menus() -> List[Tuple[str, List[str]]]:
    """Get a list of all menus.

    Returns
    -------
    List[Tuple[str, List[str]]]
        The first list represents different restaurants. The contained tuple contains
        a restaurant name and the list of individual menu items.
    """

    today = datetime.date.today()

    return [
        ("Marjetica", parsers.marjetica_tobacna(today)),
        ("Via bona", parsers.via_bona(today)),
        ("Loncek kuhaj", parsers.loncek_kuhaj(today)),
        ("Kondor", parsers.kondor(today)),
        ("Dijaski dom Vic", parsers.dijaski_dom_vic(today)),
        ("Barjan", parsers.barjan(today)),
        ("Delicije FE", parsers.delicije_fe(today)),
        ("Kurji tat", parsers.kurji_tat(today)),
        ("Interspar Vic", parsers.interspar_vic(today)),
        ("IJS", parsers.marende_dulcis_ijs(today)),
        ("CoolHouse", parsers.cool_house(today)),
        ("Hombre", parsers.hombre(today))
    ]

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
    date = datetime.date.today()

    if restaurant == "hombre":
        return parsers.hombre(date)

    elif restaurant == "marjetica":
        return parsers.marjetica_tobacna(date)

    elif restaurant == "viabona":
        return parsers.via_bona(date)

    elif restaurant == "loncekkuhaj":
        return parsers.loncek_kuhaj(date)

    elif restaurant == "kondor":
        return parsers.kondor(date)

    elif restaurant == "dd" or restaurant == "dijaskidom":
        return parsers.dijaski_dom_vic(date)
    
    elif restaurant == "barjan":
        return parsers.barjan(date)
        
    elif restaurant == "fe":
        return parsers.delicije_fe(date)
        
    elif restaurant == "kurjitat":
        return parsers.kurji_tat(date)
        
    elif restaurant == "spar":
        return parsers.interspar_vic(date)
        
    elif restaurant == "ijs":
        return parsers.marende_dulcis_ijs(date)
    
    elif restaurant == "coolhouse" or restaurant == "cool":
        return parsers.cool_house(date)
    
    else:
        return []

def convert_user_command_to_restaurant_name(restaurant: str) -> str:
    if restaurant == "hombre":
        return "Hombre"

    elif restaurant == "marjetica":
        return "Marjetica"

    elif restaurant == "viabona":
        return "Via bona"

    elif restaurant == "loncekkuhaj":
        return "Loncek kuhaj"

    elif restaurant == "kondor":
        return "Kondor"

    elif restaurant == "dd" or restaurant == "dijaskidom":
        return "Dijaski dom"
    
    elif restaurant == "barjan":
        return "Barjan"
        
    elif restaurant == "fe":
        return "Delicije FE"
        
    elif restaurant == "kurjitat":
        return "Kurji tat"
        
    elif restaurant == "spar":
        return "Spar"
        
    elif restaurant == "ijs":
        return "IJS"
    
    elif restaurant == "coolhouse" or restaurant == "cool":
        return "Cool House Vic"
    
    else:
        return ""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
