from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import datetime
import re
import os
import urllib
from urllib.request import urlopen
from time import sleep
import time
from tika import parser

class MenuParsers:
    def __init__(self):
        # If the variable is set, Selenium will attempt to
        # connect to a remote Chromedriver.
        host_var = "CHROME_HOST"
        if host_var in os.environ:
            url = "http://{}/wd/hub".format(os.environ.get(host_var))
            self.browser = webdriver.Remote(url, DesiredCapabilities.CHROME)
        else:
            # Disable loading of images
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"profile.managed_default_content_settings.images": 2}
            chromeOptions.add_experimental_option("prefs", prefs)
            self.browser = webdriver.Chrome(chrome_options=chromeOptions)

    def __del__(self):
        self.browser.close()

    def dijaski_dom_vic(self, date):
        """Get food for Dijaski Dom Vic
        """

        webpage = 'https://www.studentska-prehrana.si/sl/restaurant/Details/1485'#1314'

        # Open desired site with the date
        self.stud_preh_target_page(self.browser, webpage, date)
        # Get raw food menus
        raw_menu = self.stud_preh_get_raw_menus()

        # Get a total number of all menus
        num_of_all_menus = self.stud_preh_get_number_of_menus(raw_menu)
        # Parse menus into nicer format
        parsed_menu = self.stud_preh_parsed_menus(num_of_all_menus)

        return(parsed_menu)


    def marjetica_tobacna(self, date):
        """Get food for Marjetica
        """

        webpage = self.browser.get('http://marjetice.si/')

        # Get and parse menus into nicer format
        raw_menus = self.browser.find_element_by_xpath("/html/body/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div").text

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

    
    def via_bona(self, date):
        """Get food for Via Bona
        """

        webpage = self.browser.get('https://www.via-bona.com/sl/ponudba-hrane/malice-in-kosila/')

        raw_menus = self.browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[2]/div/table[5]").text

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


    def barjan(self, date):
        """Get food for Barjan
        """

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

    def marende_dulcis_ijs(self, date, day_of_week):
        """Get food for Marende Dulcis IJS
        """

        # Little hack
        raw = parser.from_file('example.pdf')
        raw_pdf = raw['content']

        url  = "https://gourmet.si/wp-content/uploads/2016/02/"+date+".pdf"

        # Download PDF
        pdf_name = "ijs"+date
        self.pdf_download_from_url(pdf_name, url)

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


    def loncek_kuhaj(self, date):
        """Get food for Loncek Kuhaj
        """

        url = "https://www.loncek-kuhaj.si/tedenski-jedilnik-tp.php"

        # Get raw menus 
        raw_menus = self.loncek_get_raw_menus(url)

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
            # Splitting defect,self,  ignore
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


    def delicije_fe(self, date):
        """Get food for Delicije - Fakulteta za Elektrotehniko Menza
        """

        webpage = "https://www.studentska-prehrana.si/restaurant/Details/2521#"

        # Open desired site with the date
        self.stud_preh_target_page(self.browser, webpage, date)

        # Get raw food menus
        raw_menu = self.stud_preh_get_raw_menus()
        #print(raw_menu)

        # Get a total number of all menus
        num_of_all_menus = self.stud_preh_get_number_of_menus(raw_menu)

        # Parse menus into nicer format
        parsed_menu = self.stud_preh_parsed_menus(num_of_all_menus)

        return(parsed_menu)


    def kurji_tat(self, date):
        """Get food for Kurji Tat
        """

        webpage = "https://www.studentska-prehrana.si/restaurant/Details/1429#"

        # Open desired site with the date
        self.stud_preh_target_page(self.browser, webpage, date)

        # Get raw food menus
        raw_menu = self.stud_preh_get_raw_menus()

        # Get a total number of all menus
        num_of_all_menus = self.stud_preh_get_number_of_menus(raw_menu)

        # Parse menus into nicer format
        complete_menus = self.stud_preh_parsed_menus(num_of_all_menus)

        # Remove everyday menus
        parsed_menu = self.stud_preh_remove_everyday_menus(complete_menus, num_of_all_menus, "Dunajski zrezek")

        return(parsed_menu)


    def interspar_vic(self, date):
        """Get food for Interspar Vic
        """

        webpage = "https://www.studentska-prehrana.si/restaurant/Details/1370#"

        parsed_menu =[]

        # Open desired site with the date
        self.stud_preh_target_page(self.browser, webpage, date)

        # Get raw food menus
        raw_menu = self.stud_preh_get_raw_menus()

        # Get a total number of all menus
        num_of_all_menus = self.stud_preh_get_number_of_menus(raw_menu)

        # Parse menus into nicer format
        complete_menus = self.stud_preh_parsed_menus(num_of_all_menus)

        # Remove everyday menus
        parsed_menu = self.stud_preh_remove_everyday_menus(complete_menus, num_of_all_menus, "Dunajski puranji zrezek, priloga")

        # Add dish of the week to the end
        dish_of_the_week = self.spar_get_dish_of_the_week()

        parsed_menu.append(dish_of_the_week)

        return(parsed_menu)


    def kondor(self, date):
        """Get food for Kondor
        """

        url = "https://restavracijakondor.si/#menu"

        # Open url
        webpage = self.browser.get(url)
            
        # Get raw menus
        day_id_xpath = ["//*[@id='malice']/div[1]/div[1]/dl", "//*[@id='malice']/div[1]/div[2]/dl", "//*[@id='malice']/div[1]/div[3]/dl","//*[@id='malice']/div[2]/div[1]/dl", "//*[@id='malice']/div[2]/div[2]/dl"]

        # Wait until menu is loaded
        try:
            # Wait
            while len(self.browser.find_element_by_xpath(day_id_xpath[date]).text) == 0:
                pass
                #print("waiting ...")
        except:
            self.browser.find_element_by_xpath(day_id_xpath[date]).text
            print("Xpath problem")
        
        # Get raw text for targeted day
        raw_text = self.browser.find_element_by_xpath(day_id_xpath[date]).text

        # Split by new line
        raw_menus = raw_text.split("\n")

        # Remove juha and other crap 
        raw_menus = raw_menus[2:]

        # Capitalize
        parsed_menu = []
        for i in range(0, len(raw_menus)):
            parsed_menu.append(raw_menus[i].lower().capitalize())

        return(parsed_menu)

    def stud_preh_get_raw_menus(self, ):
        """Wait until menus are shown and return raw menu list
        """

        try:
            # Wait until menu is loaded
            while len(self.browser.find_element_by_xpath("//*[@id='menu-list']").text) == 0:
                pass
                #print("waiting ...")

            return(self.browser.find_element_by_xpath("//*[@id='menu-list']").text)
        except:
            print("Xpath problem")

    def stud_preh_target_page(self, browser, webpage, date):
        """Load desired page
        """

        try:
            self.browser.get(webpage)

            # Select menu for specific day
            self.browser.find_element_by_xpath("//*[@title='"+date+"']").click()
        except:
            print("No matching date for studentska prehrana.")
        
    def stud_preh_get_number_of_menus(self, parse_menu):
        """Return the total number of all available menus.
        """

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
            
    def stud_preh_parsed_menus(self, num_of_menus):
        """Return all available menus in a nice format
        """

        try:
            all_menus = []
            # Get all the menus
            for i in range(1, num_of_menus+1):
                menu = self.browser.find_element_by_xpath("//*[@id='menu-list']/div["+str(i)+"]/div/div/div[1]/h5/strong").text
                # Throw out all the crap and capitalize
                menu = menu.replace(str(i)+"   ", "").lower().capitalize()
                all_menus.append(menu)
            return(all_menus)
        except:
            print("Xpath problem")
            
    def stud_preh_remove_everyday_menus(self, menu, num_of_all_menus, menu_delimiter):
        """Remove all everyday menus
        """       

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
            
    def marjetka_get_menus(self, date):
        """Return all available menus in a nice format
        """

        try:
            raw_menus = self.browser.find_element_by_xpath("/html/body/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div").text

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
            
            
    def barjan_fb_target_page(self, url):
        """Load Barjan FB page
        """

        try:
            # Load webpage
            request  = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            
            raw_html = response.read().decode('utf-8')
            return(raw_html)
        except:
            print("Problem opening Barjan FB url")
            
            
    def fb_barjan_get_raw_menus(self, date, raw_html):
        """Find beggining and the end of the raw menu for specific date from Barjan's FB page
        """

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

        
    def fb_barjan_beautify_raw_menus(self, raw_menus):
        """Beautify and parse Barjan's raw menus
        """

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

        

    def pdf_download_from_url(self, file_name, download_url):
        """Download PDF from given url
        """

        try:
            response = urllib.request.urlopen(download_url)
            file = open(file_name + ".pdf", 'wb')
            file.write(response.read())
            file.close()
        except:
            print("Problem while downloading PDF")
            

    def ijs_get_individual_food_locations(self, sub_menu):
        """Get individual menu positions depending on a upper case
        """

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

    def ijs_get_full_menu(self, divided_raw_menu):
        """Get a complete, parsed weekly menu
        """

        try:
            full_menu = []
            # Cycle through all main the categories
            for i in range(1, len(divided_raw_menu)):
                all_positions = self.ijs_get_individual_food_locations(divided_raw_menu[i])

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
            
    def loncek_get_raw_menus(self, url):
        """Load Loncek Kuhaj page
        """

        try:
            # Load webpage
            webpage = self.browser.get('https://www.loncek-kuhaj.si/tedenski-jedilnik-tp.php')
            
            raw_menus = self.browser.find_element_by_xpath("//*[@id='pm_layout_wrapper']/div[3]/div[1]").text
            
            return(raw_menus)
        except:
            print("Problem opening Loncek Kuhaj url")
            
    def spar_get_dish_of_the_week(self, ):
        """Get Spar dish of the week 
        """

        try:
            webpage = "https://www.spar.si/sl_SI/aktualno/restavracija-interspar/tedenski-meni.html"
            self.browser.get(webpage)

            # Dish of the week iz here
            dish_of_the_week = self.browser.find_element_by_xpath("/html/body/main/div[3]/article[1]/div/div/div[2]/div/h4").text

            # Remove all of the prices
            dish_of_the_week = re.sub("([0-9]+,[0-9]+ €)"," ", dish_of_the_week)
            # Remove all multiple spaces
            dish_of_the_week = re.sub(" +", " ", dish_of_the_week)
            # To lower case and capitalize
            dish_of_the_week = dish_of_the_week.lower().capitalize()
            
            return(dish_of_the_week)
        
        except:
            print("Problem finding dish of the week.")
            
            
    def get_ijs_date(self, work_day):
        """Calculate first or last Monday for Josko
        """

        # Get todays date
        today = datetime.date.today()
        
        # Select first next or last monday
        if work_day > 5:
            monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
        else:
            monday = today - datetime.timedelta(days=today.weekday())
            
        date = str("{:02d}".format(monday.day))+str("{:02d}".format(monday.month))+str(monday.year)
        
        return(date)

    def get_month_as_string(self, month : int) -> str:
        """Get the three letter representation of the specified month.

        Parameters
        ----------
        month : int
            Number of the month between 1 and 12.

        Returns
        -------
        str
            Three letter string representation of the month.
        """

        # Date formatting
        all_months = ("jan", "feb", "mar", "apr", "maj", "jun", "jul", "avg", "sep", "okt", "nov", "dec")

        return all_months[month - 1]

if __name__ == "__main__":
    parsers = MenuParsers()

    # Get date
    work_day = datetime.date.today().weekday() + 1

    if work_day > 5:
        work_day = 1

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    print(work_day, day, month, year)

    # Generate the right day format for each website 
    stud_preh_date = str("{:02d}".format(day))+" "+parsers.get_month_as_string(month)
    marjetka_date = str(day)+"."+str(month)+"."+str(year)
    viabona_date = marjetka_date
    barjan_date = str(day)+"."+str(month)
    loncek_kuhaj_date = work_day - 1
    kondor_date = work_day
    josko_date = parsers.get_ijs_date(datetime.date.today().weekday() + 1)

    date    = '19 avg'
    ddv_menu = parsers.dijaski_dom_vic(date)
    print("DDV: "+str(ddv_menu))

    date = "19.8.2019"
    marjetica_menu = parsers.marjetica_tobacna(date)
    print("Marjetice: "+str(marjetica_menu))

    date = "19.8.2019"
    via_bona_menu = parsers.via_bona(date)
    print("ViaBona: "+str(via_bona_menu))

    date = "14.8."
    barjan_menu = parsers.barjan(date)
    print("Barjan: "+str(barjan_menu))

    date = 0
    loncek_kuhaj_menu = parsers.loncek_kuhaj(date)
    print("LoncekKuhaj: "+str(loncek_kuhaj_menu))

    date = '19 avg'
    fe_menza_menu = parsers.delicije_fe(date)
    print("MenzaFe: "+str(fe_menza_menu))

    date = '19 avg'
    kurji_tat_menu = parsers.kurji_tat(date)
    print("KurjiTat: "+str(kurji_tat_menu))

    date = '19 avg'
    interspar_vic_menu = parsers.interspar_vic(date)
    print("SparVic: "+str(interspar_vic_menu))

    date = 0
    kondor_menu = parsers.kondor(date)
    print("Kondor: "+str(kondor_menu))

    date = "19082019"
    day_of_week = 0
    ijs_menu = parsers.marende_dulcis_ijs(date, day_of_week)
    print("IJS "+str(ijs_menu))
