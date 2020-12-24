#------------- General Configuration Data file -------------


## General Consts --------------------

CCDM_VERSION = '0.0.1 - beta'

#General Paths for use to access various resources --------
IMAGES_PATH = "resources/images/"
TEMPLATES_PATH = "resources/templates/"

#Enable and set up daily logs ---------------
#Write a log file at the end of each day (23:30)
ENABLE_DAILY_LOGS = True      
LOGS_PATH = "CCDM_logs/"

#Send daily log information via email ----------
#see email config file for set-up of statics
ENABLE_DAILY_EMAILS = False  


VERBOSE_MODE = 1    # Set high to have program annunciate various process steps
LOCAL_VERBOSE_MODE = 1  # Set high to allow local methods to annuciate 

MAX_CC_COUNT = 4
CC_COUNT = 1        # Later to be read automatically based upon UDP annunciations

CC_NAMES = ["Charge Controller 1", "Charge Controller 2", "Charge Controller 3", "Charge Controller 4"]
CC_IP_ADDRS = ["192.168.30.101", "192.168.30.102", "192.168.30.103", "192.168.30.104"]
CC_PORTS = ["502", "502", "502", "502"]
CC_IDS = ["1", "1", "1", "1"]
CC_TIMEOUTS = [2000,2000,2000,2000] #TCP connection timeout in milliseconds)

#Current Valid CC_OEM_TYPES are:
#"Midnite - Classic"
#"Tristar - MPPT 60"
CC_OEM_TYPES = ["Midnite - Classic", "Midnite - Classic", "Midnite - Classic", "Midnite - Classic"]
CC_EXPECTED_MAX_POWER = [700, 700, 700, 700]    #Set value in watts of expected maximum input power to be seen on charge controller
CC_POLLING_RATE = 0.5   #Set general system update rate (in secs)


## UI Consts ----------------------------
UI_TITLE = "Charge Controller Data Manager (CCDM)"
    
#Various UI view configurations / styles,
#UI_Mode choices are:
#graphics
#lists-only
UI_VIEW_STYLES = {
                "Application_Version": CCDM_VERSION,
                "UI_Mode": "graphics",
                "Tab_BG_Color": "default",
                "Widget_Group_Type": "tile",            #Valid inputs: None, "tile"
                "Widget_Group_BG": "light blue",
                "EntryWidget_BG": "gray90",
                "Base_Font_Size": 14                    #Valid range: 8-14 (might be limited based on screen res check)
                }    

UI_SHOW_CONFIGURATION = 1     #Set to show Controller configured parameters and this applications confiiguration
