import datetime
import re
import os
import urllib
from urllib.request import urlopen
from time import sleep
import time
import fitz
from lxml import html
import requests

class WeekendErrorMenu(Exception):
    print("")

    
class MenuParsers:
    def barjan(self, menu_date : datetime.date):
        """Get food for Barjan
        """
        
        date = str(menu_date.day)+"."+str(menu_date.month)
        
        # Find current day of the week
        workday = menu_date.weekday() + 1
        
        try:
            # Only for work days
            if workday > 5:
                raise WeekendErrorMenu
                
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
            nicer_list = clean_menus.split(" -")

            # Skip souppe of the day 
            nicer_list = nicer_list[1:] 

            # Capitalize and create final menus
            all_menus = []
            for i in range(len(nicer_list)):
                temp_menu = nicer_list[i].capitalize()
                all_menus.append(temp_menu)

            return(all_menus)

        except NotImplementedError:
            return["Barjan doesn't serve during weekends."]

        except:
            return["Barjan doesn't serve during weekends."]
            

    def marende_dulcis_ijs(self, menu_date : datetime.date):
        """Get food for Marende Dulcis IJS
        """

        date, day_of_week = self.get_ijs_date(menu_date)
        
        try:
            # Only for work days
            if day_of_week > 5:
                raise WeekendErrorMenu
            
            url  = "https://gourmet.si/wp-content/uploads/2016/02/"+date+".pdf"
            
            # Download PDF
            pdf_name = "ijs{}.pdf".format(date)
            self.pdf_download_from_url(pdf_name, url)

            # Open and parse stored PDF
            raw = fitz.open(pdf_name)
            raw_pdf = raw.loadPage(0)            
            raw_text = raw_pdf.getText("type")

            # Remove excessive content
            search_start_string = "@dulcis-gourmet.si. "
            slo_start_location = raw_text.find(search_start_string)

            # Crop all that is not actual menu 
            raw_menus = raw_text[slo_start_location:]

            # Remove new line characters
            raw_menus = raw_menus.replace("\n","")

            # Remove all shady alergene numbers and commas
            raw_menus = re.sub("([0-9]+)"," ", raw_menus).replace(" ,", "")

            # Remove all multiple spaces
            raw_menus = re.sub(" +", " ", raw_menus)

            # Take care of a capitalized second words which are not nice for parser
            raw_menus = self.ijs_convert_special_words_to_lower_case(raw_menus)       

            # "DODATNA PONUDBA SOLATE" has a higher priority than "DODATNA PONUDBA" for nicer split 
            main_categories = "JUHA | ENOLONČNICA | MESNA JED | GLAVNA JED S PRILOGO | BREZMESNA JED | DODATNA PONUDBA SOLATE | DODATNA PONUDBA"

            # Split raw menu depending on main_categories
            raw_split = re.split(main_categories, raw_menus)

            # Get full menu
            full_week_menu = self.ijs_get_full_menu(raw_split)

            # Split "DODATNA PONUDBA" at full_week_menu[5] into to two lists
            nicer_full_week_menu = full_week_menu[:5] + [full_week_menu[5][::2]] + [full_week_menu[5][1::2]] + full_week_menu[6:]

            # Create a menu based on a given workday
            all_menus = [] 
            for i in range(1,8):
                menu = nicer_full_week_menu[i][day_of_week]
                all_menus.append(menu)
            
            # Close and delete pdf
            raw.close()
            os.remove(pdf_name)
            
            return(all_menus)

        except NotImplementedError:
            return["Marende IJS doesn't serve during weekends."]

        except:
            return["Marende IJS encountered a problem while getting and parsing menus"]

        
    def pdf_download_from_url(self, file_name, download_url):
        """Download PDF from given url
        """
        
        response = urllib.request.urlopen(download_url)
        with open(file_name, 'wb') as file:
            file.write(response.read())

            
    def ijs_get_individual_food_locations(self, sub_menu):
        """Get individual menu positions depending on a upper case
        """

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

            
    def ijs_get_full_menu(self, divided_raw_menu):
        """Get a complete, parsed weekly menu
        """

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

            
    def ijs_convert_special_words_to_lower_case(self, replaced_raw_menu):
        """Convert words to lower case that would otherwise cause havoc
        """

        raw_menus = replaced_raw_menu.replace(" Nica ", " nica ")
        raw_menus = raw_menus.replace(" BBQ ", " bbq ") 

        return(raw_menus)

            
    def get_ijs_date(self, menu_date : datetime.date):
        """Calculate first or last Monday for Josko
        """

        work_day = menu_date.weekday() 

        # Select first next or last monday
        if work_day > 4:
            work_day = 0
            monday = menu_date + datetime.timedelta(days=-menu_date.weekday(), weeks=1)
        else:
            monday = menu_date - datetime.timedelta(days=menu_date.weekday())
            
        date = str("{:02d}".format(monday.day))+str("{:02d}".format(monday.month))+str(monday.year)
        
        return(date, work_day)

    
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
   

    def open_target_page(self, webpage):
        """Load desired page
        """    

        # Load page 
        page      = requests.get(webpage)
        page_tree = html.fromstring(page.content)

        return(page_tree)


    def studentska_prehrana_all_menus(self, page_tree):
        """Return all available menus in a nice format
        """

        all_menus = []

        # Get all of the todays menus
        for current_menu in range(1, 42):
            raw_table = page_tree.xpath("//*[@id='menu-list']/div["+str(current_menu)+"]/div/div/div[1]/h5/strong//text()")

            # Detect last menu, then break
            if not raw_table:
                #print(current_menu-1)
                break
            # 
            else:
                # Join into a string
                single_menu = "".join(raw_table)

                # Remove all the crap and double spaces
                single_menu = re.sub("[0-9]+ \xa0  ","", single_menu)
                single_menu = re.sub(" +", " ", single_menu)

                # Lower case then capitalize
                single_menu = single_menu.lower().capitalize()

                all_menus.append(single_menu)

        return(all_menus)


    def studentska_prehrana_clip_everyday_menus(self, menu, menu_delimiter):
        """Remove all everyday menus on Studentska prehrana
        """       
        
        # find menu delimiter search string
        for i in range(0, len(menu)):
            if menu[i] == menu_delimiter:
                menu_stop_location = i
                break

        # Chop menus after found menu_delimiter
        parsed_menu = menu[:menu_stop_location]

        return(parsed_menu)

            
    def studentska_prehrana_remove_everyday_menus(self, menu, everyday_menus):        
        """Remove all everyday menus for Studentska prehrana
        """       

        flagged_menus = []
        cleared_menu = menu

        # Search menu by menu
        for menu_pos in range(0, len(menu)):
            for everyday_pos in range(0, len(everyday_menus)):
                # Flag each everyday menu
                if menu[menu_pos] == everyday_menus[everyday_pos]:
                    flagged_menus.append(menu_pos)
                    break

        # Remove all everyday menus
        for i in sorted(flagged_menus, reverse=True):
            del cleared_menu[i]

        return(cleared_menu)

            
    def kurji_tat(self, menu_date : datetime.date):
        """Get food for Kurji Tat
        """
         
        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
                
            webpage = "https://www.studentska-prehrana.si/restaurant/Details/1429#"
            
            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            complete_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            # Remove everyday menus
            everyday_menus = ['Dunajski zrezek', 'Divjačinski golaž z njoki', 'Morski solatni krožnik', 'Ljubljanski zrezek', 'Testenine bolognese', 'Testenine s tartufno omako', 'Mesni solatni krožnik', 'Ocvrti sir', 'Solatni krožnik s sirom', 'Divjačinski golaž', 'Sardelice', 'Pražena telečja jetrca']

            all_menus = self.studentska_prehrana_remove_everyday_menus(complete_menus, everyday_menus)

            return(all_menus)      

        except NotImplementedError:
            return["Kurji Tat doesn't serve during weekends."]     

        except:
            return["Kurji Tat encountered a problem while getting and parsing menus"]
    
    
    def dijaski_dom_vic(self, menu_date : datetime.date):
        """Get food for Dijaski Dom Vic
        """

        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
                
            webpage = 'https://www.studentska-prehrana.si/sl/restaurant/Details/1314'
                
            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            all_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            return(all_menus)

        except NotImplementedError:
            return["Dijaski Dom Vic doesn't serve during weekends."]

        except:
            return["Dijaski Dom Vic encountered a problem while getting and parsing menus"]


    def marjetica_tobacna(self, menu_date : datetime.date):
        """Get food for Marjetica
        """
        
        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
                
            webpage = "https://www.studentska-prehrana.si/restaurant/Details/1424#"
                
            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            complete_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            # Remove everyday menus
            everyday_menus = ['Dunajski zrezek, priloga, solata', 'Sir na žaru, priloga, solata']

            all_menus = self.studentska_prehrana_remove_everyday_menus(complete_menus, everyday_menus)

            return(all_menus)

        except NotImplementedError:
            return["Marjetica doesn't serve during weekends."]

        except:
            return["Marjetica encountered a problem while getting and parsing menus"]
            
            
    def delicije_fe(self, menu_date : datetime.date):
        """Get food for Delicije - Fakulteta za Elektrotehniko Menza
        """

        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
                
            webpage = "https://www.studentska-prehrana.si/restaurant/Details/2521#"
                
            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            all_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            return(all_menus)

        except NotImplementedError:
            return["Menza FE doesn't serve during weekends."]  

        except:
            return["Menza FE encountered a problem while getting and parsing menus"]
        

    def kondor(self, menu_date : datetime.date):
        """Get food for Kondor
        """

        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
                
            webpage = "https://www.studentska-prehrana.si/restaurant/Details/1413#"

            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            complete_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            # Chop menus after found 4
            all_menus = complete_menus[:4]

            return(all_menus)

        except NotImplementedError:
            return["Kondor doesn't serve during weekends."]

        except:
            return["Kondor encountered a problem while getting and parsing menus"]

        
    def hombre(self, menu_date : datetime.date):
        """Get food for Hombre
        """

        try:   
            webpage = "https://www.studentska-prehrana.si/restaurant/Details/1403#"

            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            complete_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            # Chop menus after found 4
            all_menus = complete_menus[32:]

            return(all_menus)

        except:
            return["Hombre encountered a problem while getting and parsing menus"]


    def interspar_vic(self, menu_date : datetime.date):
        """Get food for Interspar Vic
        """

        try: 
            webpage = "https://www.studentska-prehrana.si/restaurant/Details/1370#"

            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Get all of the menus for today
            complete_menus = self.studentska_prehrana_all_menus(raw_page_tree)

            # Clip everyday menus
            menu_delimiter = "Dunajski puranji zrezek, priloga"
            all_menus = self.studentska_prehrana_clip_everyday_menus(complete_menus, menu_delimiter)

            # Add dish of the week to the end
            dish_of_the_week = self.spar_get_dish_of_the_week()

            all_menus.append(dish_of_the_week)

            return(all_menus)

        except:
            return["Spar Vic encountered a problem while getting and parsing menus"]
            
            
    def spar_get_dish_of_the_week(self):
        """Get Spar dish of the week 
        """
        
        try:
            webpage = "https://www.spar.si/aktualno/restavracija-interspar/tedenski-meni"

            # Open desired site with the date
            raw_page_tree = self.open_target_page(webpage)

            # Find exact row
            raw_table = raw_page_tree.xpath("/html/body/main/div[3]/article[1]/div/div/div[2]/div/h4/text()")

            # Join into a single string
            dish_of_the_week ="".join(raw_table)

            # Remove all of the crap and multiple spaces
            dish_of_the_week = re.sub("([0-9]*)","", dish_of_the_week)
            dish_of_the_week = re.sub("([0-9]+,[0-9]+ €)","", dish_of_the_week)
            dish_of_the_week = re.sub(" ,", "", dish_of_the_week)
            dish_of_the_week = re.sub("\n", "", dish_of_the_week)
            dish_of_the_week = re.sub(" +", " ", dish_of_the_week)

            # To lower case and capitalize
            dish_of_the_week = dish_of_the_week.lower().capitalize()

            return(dish_of_the_week)
        
        except:
            print("Problem finding dish of the week.")
           
    
    def via_bona(self, menu_date : datetime.date):
        """Get food for Via Bona
        """
        
        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
    
            url = "https://www.via-bona.com/sl/ponudba-hrane/malice-in-kosila/"

            # Open page
            page = requests.get(url)
            page_tree = html.fromstring(page.content)
            raw_table = page_tree.xpath("/html/body/div[5]/div/div/div[2]/div[2]/div/table["+str(date)+"]/tbody/tr[2]/td//text()")

            # Join into a single string
            raw_table_menu ="".join(raw_table)

            # Remove all the crap, prices, double spaces,... 
            raw_table_menu = re.sub("\xa0"," ", raw_table_menu)
            raw_table_menu = re.sub("([0-9]+,[0-9]+ €)"," ", raw_table_menu)
            raw_table_menu = re.sub(", SOLATA", "", raw_table_menu)
            raw_table_menu = re.sub(" +", " ", raw_table_menu)

            # Split words
            menu_split_words = ["NA ŽLICO [0-9] - ", "MALICA [0-9] - ", "VEGE MALICA - ", "SLADICA - "]

            split_location = []

            # Get all inital menu location from keywords in menu_start_words
            for search_keyword in range(len(menu_split_words)):
                split_location.append([ (i.start(), i.end()) for i in re.finditer(menu_split_words[search_keyword], raw_table_menu)])

            # Unwrap list
            split_location = sum(split_location, [])

            all_menus = []
            # Find and parse single menus and then append them into all_menus
            for i in range(len(split_location)-1):
                single_menu = raw_table_menu[split_location[i][1]:split_location[i+1][0]] 

                # Lower case then capitalize
                single_menu = single_menu.lower().capitalize()

                all_menus.append(single_menu)

            return(all_menus)

        except NotImplementedError:
            return["ViaBona doesn't serve during weekends."]   

        except:
            return["ViaBona encountered a problem while getting and parsing menus"]
            
            
    def loncek_kuhaj(self, menu_date : datetime.date):
        """Get food for Loncek Kuhaj
        """
        
        # Find current day of the week
        date = menu_date.weekday() + 1

        try:
            # Only for work days
            if date > 5:
                raise WeekendErrorMenu
                
            url = "https://www.loncek-kuhaj.si/tedenski-jedilnik-tp.php"

            hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                   'Accept-Encoding': 'none',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Connection': 'keep-alive'}

            # Open page
            page = requests.get(url, headers = hdr)
            page_tree = html.fromstring(page.content)
            raw_table = page_tree.xpath("//*[@id='pm_layout_wrapper']/div[3]/div[1]//text()")

            # Join into a single string
            raw_menus ="".join(raw_table)

            # Remove all the crap, numbers, double spaces and annoying Dnevna and following juha/minestra/whatever until ','
            raw_menus = re.sub("(Dnevna .*?,)"," ", raw_menus)
            raw_menus = re.sub("\t"," ", raw_menus)
            raw_menus = re.sub("\r"," ", raw_menus)
            raw_menus = re.sub("\n"," ", raw_menus)
            raw_menus = re.sub("([0-9]+,[0-9]+)"," ", raw_menus)
            raw_menus = re.sub(" +", " ", raw_menus)

            # Split raw menu through days
            splited_raw_menus = re.split(r"Ponedeljek, |Torek, |Sreda, |Četrtek, |Petek, ", raw_menus)

            # Select menu only for specific day and split according to "€"
            day_menu = re.split(r"€ ", splited_raw_menus[date])

            # Clip first element
            day_menu = day_menu[1:]

            all_menus = []

            # Capitalize each menu
            for i in range(0, len(day_menu)):
                all_menus.append(day_menu[i].capitalize())

            return(all_menus)

        except NotImplementedError:
            return["Loncek Kuhaj doesn't serve during weekends."]

        except:
            return["Loncek Kuhaj encountered a problem while getting and parsing menus"]
            
            
if __name__ == "__main__":
    parsers = MenuParsers()

    # Get date
    date = datetime.date.today()

    barjan_menu = parsers.barjan(date)
    print("Barjan: "+str(barjan_menu))
    
    via_bona_menu = parsers.via_bona(date)
    print("ViaBona: "+str(via_bona_menu))

    ijs_menu = parsers.marende_dulcis_ijs(date)
    print("IJS "+str(ijs_menu)) 

    marjetica_menu = parsers.marjetica_tobacna(date)
    print("Marjetice: "+str(marjetica_menu))

    interspar_vic_menu = parsers.interspar_vic(date)
    print("SparVic: "+str(interspar_vic_menu))

    loncek_kuhaj_menu = parsers.loncek_kuhaj(date)
    print("LoncekKuhaj: "+str(loncek_kuhaj_menu))
    
    kurji_tat_menu = parsers.kurji_tat(date)
    print("KurjiTat: "+str(kurji_tat_menu))
    
    fe_menza_menu = parsers.delicije_fe(date)
    print("MenzaFe: "+str(fe_menza_menu))    
    
    kondor_menu = parsers.kondor(date)
    print("Kondor: "+str(kondor_menu))

    ddv_menu = parsers.dijaski_dom_vic(date)
    print("DDV: "+str(ddv_menu))
    
    hombre_menu = parsers.hombre(date)
    print("Hombre: "+str(hombre_menu))
