from configparser import ConfigParser
from colorama import Fore
from colorama import Style
from colorama import init
from lxml import html
import requests
import sys
import os
import time
from datetime import datetime

## INITALISING COLORAMA
init(convert=True)
## GLOBAL VARIABLES THEIR VALUES DIRECTLY EXTRACTED FROM CONFIG FILES
PROXY_STATUS = False
HTTP_PROXY = None
PORT = None

FIRST_NAMES = None
LAST_NAMES = None
ZIP_CODES = None
COUNT = None
TIMEOUT = None
DELAY = None
## GLOBAL VARIABLE THEIR VALUE IS DERIVED FROM ABOVE VARIABLES
TARGET_URLS = []

def print_banner():
    ## OPENING CONSOLE IN REQUIRED RESOLUTIONS
    ## CLEARING CONSOLE
    if os.name == 'nt':
        os.system('cls')
        os.system("mode con:cols=110 lines=35")
    elif os.name == 'posix':
        os.system('clear')
    ## PRINTING BANNER
    print(f'''
                            
                 _ood>H&H&Z?#M#b-\.
             .\HMMMMMR?`\M6b."`' ''``v.
          .. .MMMMMMMMMMHMMM#&.      ``~o.
        .   ,HMMMMMMMMMM`' '           ?MP?.       
       . |MMMMMMMMMMM'                 `"$b&
      -  |MMMMHH##M'                     HMMH?
     -   TTM|     >..                   \HMMMMH
    :     |MM\,#-""$~b\.                `MMMMMM+
   .       ``"H&#        -               &MMMMMM|    {Fore.RED}         =[ Fast People Search         ]{Style.RESET_ALL}{Fore.YELLOW}
   :            *\v,#MHddc.              `9MMMMMb       + .. ..=[ Author : Prashant Varshney ]
   .               MMMMMMMM##\             `"":HM      + .. ..=[ Version : 1.0              ]
   -          .  .HMMMMMMMMMMRo_.              |M
   :             |MMMMMMMMMMMMMMMM#\           :M
   -              `HMMMMMMMMMMMMMM'            |T
   :               `*HMMMMMMMMMMM'             H'
    :                MMMMMMMMMMM|             |T
     ;               MMMMMMMM?'              ./
      `              MMMMMMH'               ./'
       -            |MMMH#'                 .
        `           `MM*                . `
          _          #M: .    .       .-'
             .          .,         .-'
                '-.-~ooHH__,,v~--`'

    {Style.RESET_ALL}''')

## READING CONFIGURATION FILES
def initialisation():
    global PROXY_STATUS
    global HTTP_PROXY
    global PORT

    global FIRST_NAMES
    global LAST_NAMES
    global ZIP_CODES 
    global COUNT
    global TIMEOUT
    global DELAY
    ############################## READING CONFIGURATION FILES ###############################
    config = ConfigParser(allow_no_value=True)
    if "Config.cfg" in os.listdir():
        print(f"{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Reading Configuration File - Config.cfg")
        try:
            config.read('Config.cfg')
        except:
            print(f'{Fore.RED}[  ERROR ]{Style.RESET_ALL} Failed To Read Config.cfg Due To Invalid Syntax of Configuration File')
            print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Exiting...')
            input()
            sys.exit(0)
    else:
        print(f"{Fore.RED}[  ERROR ]{Style.RESET_ALL} Configuration File - Config.cfg Is Missing")
        input(f"{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Exiting...")
        sys.exit(0)
    if "TargetingCities.cfg" in os.listdir(os.path.join(os.getcwd(),"InputData")):
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Reading Configuration File - TargetingCities.cfg ')
        try:
            config.read('InputData/TargetingCities.cfg')
        except:
            print(f'{Fore.RED}[  ERROR ]{Style.RESET_ALL} Failed To Read TargetingCities.cfg Due To Invalid Syntax of Configuration File')
            print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Exiting...')
            input()
            sys.exit(0)
    else:
        print(f"{Fore.RED}[  ERROR ]{Style.RESET_ALL} Configuration File - TargetingCities.cfg Is Missing")
        input(f"{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Exiting...")
        sys.exit(0)
    if "TargetingNames.cfg" in os.listdir(os.path.join(os.getcwd(),"InputData")):
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Reading Configuration File - TargetingNames.cfg ')
        try:
            config.read('InputData/TargetingNames.cfg')
        except:
            print(f'{Fore.RED}[  ERROR ]{Style.RESET_ALL} Failed To Read TargetingNames.cfg Due To Invalid Syntax of Configuration File')
            print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Exiting...')
            input()
            sys.exit(0)
    else:
        print(f"{Fore.RED}[  ERROR ]{Style.RESET_ALL} Configuration File - TargetingNames.cfg Is Missing")
        input(f"{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Exiting...")
        sys.exit(0)
    ############################## UPDATING GLOBAL VARIABLES ##################################
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Updating Global Variables')
    PROXY_STATUS = config["PROXY_STATUS"]["STATUS"]
    HTTP_PROXY = config["PROXY_SERVER"]["HTTP_PROXY"]
    PORT = config["PROXY_SERVER"]["PORT"]

    FIRST_NAMES = list(config["FIRST-NAME-COL"])
    LAST_NAMES = list(config["LAST-NAME-COL"])
    ZIP_CODES = list(config["ZIP-COL"])
    COUNT = int(config["SCRAPPER_CONFIG"]["COUNT"])
    DELAY = int(config["SCRAPPER_CONFIG"]["DELAY"])
    TIMEOUT = int(config["SCRAPPER_CONFIG"]["TIMEOUT"])

## THIS METHOD CREATES AN ABSTRACTION FOR LOW LEVEL REQUESTS.GET(URL,HEADERS,PROXIES)
def get(URL):
    if PROXY_STATUS in ["True","TRUE","true"]:
        proxies={
            "http":f"{HTTP_PROXY}:{PORT}",
            "https":f"{HTTP_PROXY}:{PORT}"
        }
    else:
        proxies = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    ## CHECKING INTERNET CONNECTIVITY EVERY 100 REQUESTS SEND TI SERVER
    testing_connectivity = True
    while testing_connectivity:
        status = check_connectivity()
        if status == False:
            print(f'{Fore.RED}[  ERROR ]{Style.RESET_ALL} Connectivity Lost With Proxy Server')
            print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Retrying in 10 seconds')        
            time.sleep(10)
            initialisation()
        else:
            testing_connectivity = False
            print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Requesting URL : '+URL)
            try:
                return requests.get(URL,headers=headers,proxies=proxies,timeout=TIMEOUT)
            except:
                testing_connectivity = True

def check_connectivity():
    if PROXY_STATUS in ["True","TRUE","true"]:
        proxies={
            "http":f"{HTTP_PROXY}:{PORT}",
            "https":f"{HTTP_PROXY}:{PORT}"
        }
    else:
        proxies = {}
    try:
        response = requests.get("https://ident.me",proxies=proxies,timeout=TIMEOUT)
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Current Public IP : {response.text}')
        return True
    except:
        return False    

def generate_list_of_urls():
    global TARGET_URLS
    ## CREATING COMBINATIONS OF FIRST_NAMES, LAST_NAMES, ETC.
    for f_name in FIRST_NAMES:
        for l_name in LAST_NAMES:
            for zipcode in ZIP_CODES:
                ## CHECKING EMPTYINESS IN FIRST_NAMES OR LAST_NAMES
                if f_name == '""':
                    name = l_name
                elif l_name == '""':
                    name = f_name
                else:
                    name = f"{f_name}-{l_name}"
                fast_people_search(name,zipcode)
                if len(TARGET_URLS) >= COUNT:
                    return
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} All The Possible Combinations Of Names And CityStateZip Created')

## THIS METHOD CREATES A LIST OF TARGETING URLS FOR EXTRACTION OF DETAILS
def fast_people_search(name,zip_code):
    global TARGET_URLS
    search_string = "https://www.fastpeoplesearch.com/name/NAME_ZIPCODE/page/PAGENUMBER"
    ## FETCHING NUMBER OF RESULTS TO HARVEST
    response = get( search_string.replace("NAME",name).replace("ZIPCODE",zip_code).replace("PAGENUMBER","1") )
    markup_tree = html.fromstring(response.content)
    if markup_tree.xpath("/html/head/title/text()")[0] == 'Access denied | www.fastpeoplesearch.com used Cloudflare to restrict access':
        print(f'{Fore.RED}[  ERROR ]{Style.RESET_ALL} Access Denied From FastPeopleSearch.com')
        sys.exit(0)
    if markup_tree.xpath("/html/body/div[4]/div/div[2]/div[2]/text()")[0].strip() == 'Your exact search did not return any results.':
        if markup_tree.xpath("/html/body/div[4]/div/div[2]/div[3]/text()")[0].strip().split(" ")[0] == 'Over':
            number_of_records = int(markup_tree.xpath("/html/body/div[4]/div/div[2]/div[3]/text()")[0].strip().split(" ")[1][:-1])
        else:
            number_of_records = int(markup_tree.xpath("/html/body/div[4]/div/div[2]/div[3]/text()")[0].strip().split(" ")[0])
    else:
        if markup_tree.xpath("/html/body/div[4]/div/div[2]/div[2]/text()")[0].strip().split(" ")[0] == "Over":
            number_of_records = int(markup_tree.xpath("/html/body/div[4]/div/div[2]/div[2]/text()")[0].strip().split(" ")[1][:-1])
        else:
            number_of_records = int(markup_tree.xpath("/html/body/div[4]/div/div[2]/div[2]/text()")[0].strip().split(" ")[0])
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Number Of Search Results : ' + str(number_of_records))
    ## IF PER PAGE WE GOT 10 RESULTS MAX, SO TOTAL RECORD SPREADED AMONG
    number_of_pages = number_of_records if number_of_records < 10 else number_of_records // 10
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Number Of Pages To Query : ' + str(number_of_pages))
    ## EXTRACTING URL LINKS FROM WEBPAGE
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Starting Querying On Each Page\n')
    for index in range(1,number_of_pages+1):
        response = get( search_string.replace("NAME",name).replace("ZIPCODE",zip_code).replace("PAGENUMBER",str(index)) )
        markup_tree = html.fromstring(response.content)
        ## EXTRACTING LINKS PRESENT ON CURRENT PAGE
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Bundling List Of Users Found')
        url_links = markup_tree.xpath("//a[@class='btn btn-primary link-to-details']/@href")
        TARGET_URLS = list(set(TARGET_URLS + url_links))
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Links Harvested : {len(TARGET_URLS)}\n')
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Query Finished On Name : {name}, Address : {zip_code}')

if __name__ == "__main__":
    print_banner()
    initialisation()
    if PROXY_STATUS in ["True","TRUE","true"]:
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Sending Requests Through Proxy Server\n')
    else:
        print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Sending Requests Through Your Public IP\n')
    generate_list_of_urls()
    TARGET_URLS = list(set(TARGET_URLS))
    print(f'\n{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Total Users Found : {len(TARGET_URLS)}')
    ## QUERY ABOUT THE EACH USER IN TARGET_URLS
    ## CREATING FILE FOR STORING HARVESTED DATA, HERE I AM GOING TO ADD HEADERS IN FILE
    USER_DETAILS = f'./HarvestedOutput/ScrappedDetails_{datetime.now().strftime("(%d-%m-%Y)_(%H-%M-%S)")}.csv'
    print(f'{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Storing Harvested Data in {USER_DETAILS}')
    with open(USER_DETAILS,'w') as fd:
        fd.write(f'Name,Age,Address,Wireless-1,Wireless-2,Wireless-3,Wireless-4,Wireless-5,Wireless-6,Landline-1,Landline-2,Landline-3,Landline-4,Landline-5,Landline-6\n')
        fd.flush()
    for i in range(len(TARGET_URLS)):
        user_name = ""
        user_age = 'NaN'
        user_contact = ""
        user_address = ""

        print(f'\n{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Serial : {i+1}')
        response = get("https://www.fastpeoplesearch.com"+TARGET_URLS[i])
        markup_tree = html.fromstring(response.content)
        ## NAME
        try:
            user_name = markup_tree.xpath("/html/body/div[4]/div/div[2]/div[4]/h2/span/text()")[0]
        except:
            pass
        ## AGE
        try:
            user_age = markup_tree.xpath("//*[@id='age-header']/text()")[0].split(" ")[1]
        except:
            pass
        ## CONTACT
        try:
            x = markup_tree.xpath("//div[@class='detail-box-phone']/p")
            user_contact = []
            for i in range(len(x)):
                if i == 0:
                    y = x[i].xpath("strong/a/text()")[0]
                    z = x[i].xpath("text()")[0]
                    user_contact.append((y,z))
                else:
                    y = x[i].xpath("a/text()")[0]
                    z = x[i].xpath("text()")[0]
                    user_contact.append((y,z))
        except:
            pass
        ## ADDRESS 
        try:
            x = markup_tree.xpath('/html/body/div[4]/div/div[2]/div[2]/div/p/strong/a/text()')
            user_address = ""
            for i in x:
                user_address += i.strip().replace(","," ")
        except:
            pass
        ## CHECKING FOR THAT QUERY WHICH DOESN'T HAVE AGE
        if user_age == 'NaN':
            continue
        ## SPLITING INTO DIFFERENT CATEGORIES LIKE LANDLINE AND WIRELESS
        ## SPLITING FURTHER INTO NUMERIC VALUES AND STRINGS
        wireless = []
        landline = []
        for i in range(len(user_contact)):
            if user_contact[i][1] == ' - landline':
                landline.append(user_contact[i][0])
            if user_contact[i][1] == ' - wireless':
                wireless.append(user_contact[i][0])
        print('\nName : '+user_name)
        print('Age : '+user_age)
        print(f'Wireless Contact : {wireless}')
        print(f'Landline Contact : {landline}')
        print('Address : '+user_address)
        ## WRITING IN CSV FILE
        with open(USER_DETAILS,'a') as fd:
            fd.write(user_name+','+user_age+','+user_address+',')
            ## ENTERING WIRELESS CONTACT NUMBERS
            blank_space = 6-len(wireless) if(len(wireless) <= 6) else 0
            for i in range(len(wireless)):
                fd.write(wireless[i]+',')
                if i == 6:
                    break
            for i in range(blank_space):
                fd.write(',')
            ## ENTERING LANDLINE CONTACT NUMBERS
            blank_space = 6-len(landline) if(len(landline) <= 6) else 0
            for i in range(len(landline)):
                fd.write(landline[i]+',')
                if i == 6:
                    break
            for i in range(blank_space):
                fd.write(',')
            fd.write('\n')
    print(f'\n\n{Fore.YELLOW}[  INFO  ]{Style.RESET_ALL} Extraction Completed')