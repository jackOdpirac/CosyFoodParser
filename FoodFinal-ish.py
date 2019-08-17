from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import re
import urllib
from urllib.request import urlopen
from time import sleep
import time
from tika import parser

"""Get food for Dijaski Dom Vic
"""
def dijaski_dom_vic(date):
    webpage = 'https://www.studentska-prehrana.si/sl/restaurant/Details/1485'#1314'

    # Open desired site with the date
    stud_preh_target_page(browser, webpage, date)
    # Get raw food menus
    raw_menu = stud_preh_get_raw_menus()

    # Get a total number of all menus
    num_of_all_menus = stud_preh_get_number_of_menus(raw_menu)
    # Parse menus into nicer format
    parsed_menu = stud_preh_parsed_menus(num_of_all_menus)

    return(parsed_menu)


"""Get food for Marjetica
"""
def marjetica_tobacna(date):
    webpage = browser.get('http://marjetice.si/')

    # Get and parse menus into nicer format
    raw_menus = browser.find_element_by_xpath("/html/body/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div").text

    # First repair any inconsistencies 
    raw_menus.replace("\n  ", "\n\n\n")

    # Find start date
    start = raw_menus.find(date)
    # Find first line
    next_line_start = raw_menus.find("\n", start) 

    all_menus = []
    # Locate start and end lines for each menu
    for i in range(0,3):
        next_line_start = raw_menus.find("\n", next_line_start)
        next_line_stops = raw_menus.find("\n", next_line_start+1)
        all_menus.append(raw_menus[next_line_start+1:next_line_stops])
        next_line_start = next_line_stops

    return(all_menus)

 
"""Get food for Via Bona
"""
def via_bona(date):
    webpage = browser.get('https://www.via-bona.com/sl/ponudba-hrane/malice-in-kosila/')

    raw_menus = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[2]/div/table[5]").text

    menu_start_words = ["\nNA  ŽLICO ", "\nMALICA ", "\nVEGE MALICA ", "\nSLADICA "]

    test = raw_menus

    inital_location = []

    # Get all inital menu location from keywords in menu_start_words
    for search_keyword in range(len(menu_start_words)):
        inital_location.append([ (i.start(), i.end()) for i in re.finditer(menu_start_words[search_keyword], test)])

    # Unwrap list
    inital_location = sum(inital_location, [])

    shorter_raw_menus = test[inital_location[0][1]:inital_location[-1][1]]

    real_location_start = []
    real_location_ended = []

    real_location_start = [ (i.start(), i.end()) for i in re.finditer("€\n", shorter_raw_menus)]
    real_location_ended = [ (i.start(), i.end()) for i in re.finditer("\n \n", shorter_raw_menus)]

    all_menus = []
    for i in range(len(inital_location)-1):
        temp_menu = shorter_raw_menus[real_location_start[i][1]:real_location_ended[i][0]] 
        temp_menu = temp_menu.replace("\n", " ")
        temp_menu = temp_menu.replace("   ", " ")
        temp_menu = temp_menu.replace("  ", " ")
        temp_menu = temp_menu.lower().capitalize()
        all_menus.append(temp_menu)

    return(all_menus)


"""Get food for Barjan
"""
def barjan(date):
    url = "https://www.facebook.com/PIZZERIA-BARJAN-119529851401554/"

    # Load Barjan FB page 
    request  = urllib.request.Request(url)
    response = urllib.request.urlopen(request)     
    raw_html = response.read().decode('utf-8')

    # Start and stop strings
    start_location = date
    end_location   = "</span></p><span class=\"text_exposed_hide\">"

    # Find start and stop
    raw_menu_start = raw_html.find(date)
    raw_menu_stop  = raw_html.find(end_location, raw_menu_start)

    # Actual raw menus
    raw_menus = raw_html[raw_menu_start:raw_menu_stop]

    # Remove all tags and all the other crap
    clean_menus = re.sub('<[^>]+>', '', raw_menus)
    clean_menus = clean_menus.replace("...","")
    clean_menus = clean_menus.replace(date, "")

    # Create a nicer list of menus 
    nicer_list = clean_menus.split("-")

    # Skip souppe of the day 
    nicer_list = nicer_list[1:] 

    # Capitalize and create final menus
    all_menus = []
    for i in range(len(nicer_list)):
        temp_menu = nicer_list[i].capitalize()
        all_menus.append(temp_menu)

    return(all_menus)

"""Get food for Marende Dulcis IJS
"""
def marende_dulcis_ijs(date, day_of_week):
    # Little hack
    raw = parser.from_file('example.pdf')
    raw_pdf = raw['content']

    url  = "https://gourmet.si/wp-content/uploads/2016/02/"+date+".pdf"

    # Download PDF
    pdf_name = "ijs"+date
    pdf_download_from_url(pdf_name, url)

    # Open and parse stored PDF
    raw = parser.from_file(pdf_name + ".pdf")
    raw_pdf = raw['content']

    # Remove excessive content
    search_start_string = "@dulcis-gourmet.si. "
    search_end_string   = "mailto:merende@dulcis-gourmet.si"
    slo_start_location = raw_pdf.find(search_start_string)
    eng_start_location = raw_pdf.find(search_end_string, slo_start_location+1)

    # Crop all that is not actual menu 
    raw_menus = raw_pdf[slo_start_location:eng_start_location]

    # Remove new line characters
    raw_menus = raw_menus.replace("\n","")

    # Remove all shady alergene numbers and commas
    raw_menus = re.sub("([0-9]+)"," ", raw_menus).replace(" ,", "")

    # Remove all multiple spaces
    raw_menus = re.sub(" +", " ", raw_menus)

    # "DODATNA PONUDBA SOLATE" has a higher priority than "DODATNA PONUDBA" for nicer split 
    main_categories = "JUHA | ENOLONČNICA | MESNA JED | GLAVNA JED S PRILOGO | BREZMESNA JED | DODATNA PONUDBA SOLATE | DODATNA PONUDBA"

    # Split raw menu depending on main_categories
    raw_split = re.split(main_categories, raw_menus)

    # Get full menu
    full_week_menu = ijs_get_full_menu(raw_split)

    # Split "DODATNA PONUDBA" at full_week_menu[5] into to two lists
    nicer_full_week_menu = full_week_menu[:5] + [full_week_menu[5][::2]] + [full_week_menu[5][1::2]] + full_week_menu[6:]

    # Create a menu based on a given workday
    all_menus = [] 
    for i in range(1,8):
        menu = nicer_full_week_menu[i][day_of_week]
        all_menus.append(menu)

    return(all_menus) 


"""Get food for Loncek Kuhaj
"""
def loncek_kuhaj(date):
    url = "https://www.loncek-kuhaj.si/tedenski-jedilnik-tp.php"

    # Get raw menus 
    raw_menus = loncek_get_raw_menus(url)

    # Remove all of the prices
    raw_menus = re.sub("(\n[0-9]+,[0-9]+ €)"," ", raw_menus)

    # Remove annoying DNEVNA JUHA and following juha/minestra/whatever
    raw_menus = re.sub("(\nDNEVNA JUHA\n.*?\n)"," ", raw_menus)

    # Remove all the dates
    raw_menus = re.sub("([0-9]+. [0-9]+. [0-9]+)"," ", raw_menus)

    # Remove all multiple spaces
    raw_menus = re.sub(" +", " ", raw_menus)

    # Split raw menu through days
    splited_raw_menus = re.split(r"Ponedeljek, |Torek, |Sreda, |Četrtek, |Petek, ", raw_menus)

    # Skip everything prior Ponedeljek
    splited_raw_menus = splited_raw_menus[1:]

    # Split every day menu by "Dnevna juha, "
    full_week_menu = []
    for i in range(0,5):
        day_menu = re.split(r"Dnevna juha, ", splited_raw_menus[i])
        # Splitting defect, ignore
        day_menu = day_menu[1:]
        full_week_menu.append(day_menu)

    # Capitalize and remove "\n"
    all_menus = []
    for i in range(len(full_week_menu)):
        daily_menu = []
        for j in full_week_menu[i]:
            daily_menu.append(j.capitalize().replace("\n",""))
        all_menus.append(daily_menu)

    #final menus
    return(all_menus[date])


"""Get food for Delicije - Fakulteta za Elektrotehniko Menza
"""
def delicije_fe(date):
    webpage = "https://www.studentska-prehrana.si/restaurant/Details/2521#"

    # Open desired site with the date
    stud_preh_target_page(browser, webpage, date)

    # Get raw food menus
    raw_menu = stud_preh_get_raw_menus()
    #print(raw_menu)

    # Get a total number of all menus
    num_of_all_menus = stud_preh_get_number_of_menus(raw_menu)

    # Parse menus into nicer format
    parsed_menu = stud_preh_parsed_menus(num_of_all_menus)

    return(parsed_menu)


"""Get food for Kurji Tat
"""
def kurji_tat(date):
    webpage = "https://www.studentska-prehrana.si/restaurant/Details/1429#"

    # Open desired site with the date
    stud_preh_target_page(browser, webpage, date)

    # Get raw food menus
    raw_menu = stud_preh_get_raw_menus()

    # Get a total number of all menus
    num_of_all_menus = stud_preh_get_number_of_menus(raw_menu)

    # Parse menus into nicer format
    complete_menus = stud_preh_parsed_menus(num_of_all_menus)

    # Remove everyday menus
    parsed_menu = stud_preh_remove_everyday_menus(complete_menus, num_of_all_menus, "Dunajski zrezek")

    return(parsed_menu)


"""Get food for Interspar Vic
"""
def interspar_vic(date):
    webpage = "https://www.studentska-prehrana.si/restaurant/Details/1370#"

    parsed_menu =[]

    # Open desired site with the date
    stud_preh_target_page(browser, webpage, date)

    # Get raw food menus
    raw_menu = stud_preh_get_raw_menus()

    # Get a total number of all menus
    num_of_all_menus = stud_preh_get_number_of_menus(raw_menu)

    # Parse menus into nicer format
    complete_menus = stud_preh_parsed_menus(num_of_all_menus)

    # Remove everyday menus
    parsed_menu = stud_preh_remove_everyday_menus(complete_menus, num_of_all_menus, "Dunajski puranji zrezek, priloga")

    # Add dish of the week to the end
    dish_of_the_week = spar_get_dish_of_the_week()

    parsed_menu.append(dish_of_the_week)

    return(parsed_menu)


"""Get food for Kondor
"""
def kondor(date):
    url = "https://restavracijakondor.si/#menu"

    # Open url
    webpage = browser.get(url)

    # Get raw menus
    day_id_xpath = ["//*[@id='malice']/div[1]/div[1]/dl", "//*[@id='malice']/div[1]/div[2]/dl", "//*[@id='malice']/div[1]/div[3]/dl","//*[@id='malice']/div[2]/div[1]/dl", "//*[@id='malice']/div[2]/div[2]/dl"]

    # Get raw text for targeted day
    raw_text = browser.find_element_by_xpath(day_id_xpath[date]).text

    # Split by new line
    raw_menus = raw_text.split("\n")

    # Remove juha and other crap 
    raw_menus = raw_menus[2:]

    # Capitalize
    parsed_menu = []
    for i in range(0, len(raw_menus)):
        parsed_menu.append(raw_menus[i].lower().capitalize())

    return(parsed_menu)

"""Wait until menus are shown and return raw menu list
"""
def stud_preh_get_raw_menus():
    try:
        # Wait until menu is loaded
        while len(browser.find_element_by_xpath("//*[@id='menu-list']").text) == 0:
            pass
            #print("waiting ...")

        return(browser.find_element_by_xpath("//*[@id='menu-list']").text)
    except:
        print("Xpath problem")

"""Load desired page
"""
def stud_preh_target_page(browser, webpage, date):
    try:
        browser.get(webpage)

        # Select menu for specific day
        browser.find_element_by_xpath("//*[@title='"+date+"']").click()
    except:
        print("No matching date for studentska prehrana.")
    
"""Return the total number of all available menus.
"""
def stud_preh_get_number_of_menus(parse_menu):
    try:
        total_dishes = 0
        current_dish = 0

        while current_dish != -1:
            current_dish = parse_menu.find(""+str(total_dishes + 1)+"   ")
            total_dishes += 1
            #print(total_dishes-1)
        return(total_dishes - 1)
    except:
        print("Poblem finding total number of menus")
        
"""Return all available menus in a nice format
"""
def stud_preh_parsed_menus(num_of_menus):
    try:
        all_menus = []
        # Get all the menus
        for i in range(1, num_of_menus+1):
            menu = browser.find_element_by_xpath("//*[@id='menu-list']/div["+str(i)+"]/div/div/div[1]/h5/strong").text
            # Throw out all the crap and capitalize
            menu = menu.replace(str(i)+"   ", "").lower().capitalize()
            all_menus.append(menu)
        return(all_menus)
    except:
        print("Xpath problem")
        
"""Remove all everyday menus
"""       
def stud_preh_remove_everyday_menus(menu, num_of_all_menus, menu_delimiter):
    try:
        # find menu delimiter search string
        for i in range(0, num_of_all_menus):
            if menu[i] == menu_delimiter:
                menu_stop_location = i
        # Chop menus after found menu_delimiter
        parsed_menu = menu[:menu_stop_location]
        return(parsed_menu)
    except:
        print("Problem finding menu_delimiter")
        
"""Return all available menus in a nice format
"""
def marjetka_get_menus(date):
    try:
        raw_menus = browser.find_element_by_xpath("/html/body/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div").text

        # First repair any inconsistencies 
        raw_menus.replace("\n  ", "\n\n\n")

        # Find start date
        start = raw_menus.find(date)
        # Find first line
        next_line_start = raw_menus.find("\n", start) 

        all_menus = []

        # Locate start and end lines for each menu
        for i in range(0,3):
            next_line_start = raw_menus.find("\n", next_line_start)
            next_line_stops = raw_menus.find("\n", next_line_start+1)
            all_menus.append(raw_menus[next_line_start+1:next_line_stops])
            next_line_start = next_line_stops

        return(all_menus)
    except:
        print("Problem finding matching date for marjetka")
        
        
"""Load Barjan FB page
"""
def barjan_fb_target_page(url):
    try:
        # Load webpage
        request  = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        
        raw_html = response.read().decode('utf-8')
        return(raw_html)
    except:
        print("Problem opening Barjan FB url")
        
        
"""Find beggining and the end of the raw menu for specific date from Barjan's FB page
"""
def fb_barjan_get_raw_menus(date, raw_html):
    try:
        # Start and stop strings
        start_location = date
        end_location   = "</span></p><span class=\"text_exposed_hide\">"
        
        # Find start and stop
        raw_menu_start = raw_html.find(date)
        raw_menu_stop  = raw_html.find(end_location, raw_menu_start)
        
        # Actual raw menus
        raw_menus = raw_html[raw_menu_start:raw_menu_stop]
        return(raw_menus)
    except:
        print("Date for Barjan not found on the face")
        return(0)

    
"""Beautify and parse Barjan's raw menus
"""
def fb_barjan_beautify_raw_menus(raw_menus):
    try:
        # Remove all tags and all the other crap
        clean_menus = re.sub('<[^>]+>', '', raw_menus)
        clean_menus = clean_menus.replace("...","")
        clean_menus = clean_menus.replace(date, "")

        # Create a nicer list of menus 
        nicer_list = clean_menus.split("-")

        # Skip souppe of the day 
        nicer_list = nicer_list[1:] 

        # Capitalize and create final menus
        parsed_menus = []
        for i in range(len(nicer_list)):
            temp_menu = nicer_list[i].capitalize()
            parsed_menus.append(temp_menu)
        return(parsed_menus)
    
    except:
        print("Something went wrong with beautification:(")
        return(0)

    

"""Download PDF from given url
"""
def pdf_download_from_url(file_name, download_url):
    try:
        response = urllib.request.urlopen(download_url)
        file = open(file_name + ".pdf", 'wb')
        file.write(response.read())
        file.close()
    except:
        print("Problem while downloading PDF")
        

"""Get individual menu positions depending on a upper case
"""
def ijs_get_individual_food_locations(sub_menu):
    try:
        slo_upper_alphabet = ["A","B","C","Č","D","E","F","G","H","I","J","K","L","M","N","O","P","R","S","Š","T","U","V","Z","Ž"]
        slo_lower_alphabet = ["a","b","c","č","d","e","f","g","h","i","j","k","l","m","n","o","p","r","s","š","t","u","v","z","ž",]
        all_positions = []
        # Cycle trough all of a sub_menu
        for i in range(0, len(sub_menu)):
            for j in range(0, len(slo_upper_alphabet)):
                if sub_menu[i] == slo_upper_alphabet[j]:
                    all_positions.append(i)

        # Add last list's last index
        all_positions.append(len(sub_menu))

        return(all_positions)
    except:
        print("Something went wrong while searching for the menus positions")

"""Get a complete, parsed weekly menu
"""
def ijs_get_full_menu(divided_raw_menu):
    try:
        full_menu = []
        # Cycle through all main the categories
        for i in range(1, len(divided_raw_menu)):
            all_positions = ijs_get_individual_food_locations(divided_raw_menu[i])

            # Cycle through all dishes inside a category
            sub_menus = []
            for j in range(0, len(all_positions)-1):
                temp = divided_raw_menu[i][ all_positions[j] : all_positions[j+1] ]
                sub_menus.append(temp)

            # Apend sub_menus to full mentu
            full_menu.append(sub_menus)
        return(full_menu)
    except:
        print("Something went wrong during parsing")
        
"""Load Loncek Kuhaj page
"""
def loncek_get_raw_menus(url):
    try:
        # Load webpage
        webpage = browser.get('https://www.loncek-kuhaj.si/tedenski-jedilnik-tp.php')
        
        raw_menus = browser.find_element_by_xpath("//*[@id='pm_layout_wrapper']/div[3]/div[1]").text
        
        return(raw_menus)
    except:
        print("Problem opening Loncek Kuhaj url")
        
"""Get Spar dish of the week 
"""
def spar_get_dish_of_the_week():
    try:
        webpage = "https://www.spar.si/sl_SI/aktualno/restavracija-interspar/tedenski-meni.html"
        browser.get(webpage)

        # Dish of the week iz here
        dish_of_the_week = browser.find_element_by_xpath("//*[@id='main']/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody/tr[2]").text

        # Remove all of the prices
        dish_of_the_week = re.sub("([0-9]+,[0-9]+ €)"," ", dish_of_the_week)
        # Remove all multiple spaces
        dish_of_the_week = re.sub(" +", " ", dish_of_the_week)
        # To lower case and capitalize
        dish_of_the_week = dish_of_the_week.lower().capitalize()
        
        return(dish_of_the_week)
    
    except:
        print("Problem finding dish of the week.")
        
        
"""Calculate first or last Monday for Josko
"""
def get_ijs_date(work_day):
    # Get todays date
    today = datetime.date.today()
    
    # Select first next or last monday
    if work_day > 5: 
        monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
    else:
        monday = today - datetime.timedelta(days=today.weekday())
        
    date = str("{:02d}".format(monday.day))+str("{:02d}".format(monday.month))+str(monday.year)
    
    return(date)

if __name__ == "__main__":
    # Date formatting
    all_months = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "avg", "sep", "okt", "nov", "dec"]
    #today = datetime.today()

    # Get date
    work_day = datetime.date.today().weekday() + 1

    if work_day > 5:
        work_day = 1

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    print(work_day, day, month, year)

    # Generate the right day format for each website 
    stud_preh_date = str("{:02d}".format(day))+" "+all_months[(month)-1]
    marjetka_date = str(day)+"."+str(month)+"."+str(year)
    viabona_date = marjetka_date
    barjan_date = str(day)+"."+str(month)
    loncek_kuhaj_date = work_day - 1
    kondor_date = work_day
    josko_date = get_ijs_date(datetime.date.today().weekday() + 1)

    browser = webdriver.Chrome()

    date    = '29 jul'
    ddv_menu = dijaski_dom_vic(date)
    print(ddv_menu)

    date = "29.7.2019"
    marjetica_menu = marjetica_tobacna(date)
    print(marjetica_menu)

    date = "29.7.2019"
    via_bona_menu = via_bona(date)
    print(via_bona_menu)

    date = "26.7."
    barjan_menu = barjan(date)
    print(barjan_menu)

    date = 0
    loncek_kuhaj_menu = loncek_kuhaj(date)
    print(loncek_kuhaj_menu)

    date = '29 jul'
    fe_menza_menu = delicije_fe(date)
    print(fe_menza_menu)

    date = '29 jul'
    kurji_tat_menu = kurji_tat(date)
    print(kurji_tat_menu)

    date = '29 jul'
    interspar_vic_menu = interspar_vic(date)
    print(interspar_vic_menu)

    date = 0
    kondor_menu = kondor(date)
    print(kondor_menu)

    #date = "29072019"
    #day_of_week = 0
    #ijs_menu = marende_dulcis_ijs(date, day_of_week)
    #print(ijs_menu)

    browser.close()
