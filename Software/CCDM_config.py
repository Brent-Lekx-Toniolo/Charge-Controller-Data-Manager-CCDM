##------------------- General Configuration Data file ----------------

CCDM_VERSION = '0.0.2 - beta'

##-------------------------- General Consts --------------------


#Set amount of Charge Controllers for CCDM to Poll
CC_COUNT = 1        #Note: Later to be read automatically based upon UDP annunciations
#Maximum Count (leave at 4)
MAX_CC_COUNT = 4


#Controller Names
CC_NAMES = ["Charge Controller 1", "Charge Controller 2", "Charge Controller 3", "Charge Controller 4"]


#TCP/IP Address
CC_IP_ADDRS = ["127.0.0.1", "192.168.30.102", "192.168.30.103", "192.168.30.104"]
#TCP Port Number
CC_PORTS = ["502", "502", "502", "502"]
#ID Number
CC_IDS = ["1", "1", "1", "1"]


#TCP connection timeout in milliseconds)
CC_TIMEOUTS = [2000,2000,2000,2000] 


#Set Charge Controller Types here
    #Current Valid CC_OEM_TYPES are:
    #"Midnite - Classic"
    #"Tristar - MPPT 60"
CC_OEM_TYPES = ["Midnite - Classic", "Midnite - Classic", "Midnite - Classic", "Midnite - Classic"]


#Set value, in watts, of expected maximum input power to be seen on charge controller
CC_EXPECTED_MAX_POWER = [700, 700, 700, 700]    

#Set general system update rate (in secs)
CC_POLLING_RATE = 0.5   




##----------------- UI Consts ----------------------------


UI_TITLE = "Charge Controller Data Manager (CCDM)"

    
#Various UI view configurations / styles
UI_VIEW_STYLES = {
                "Application_Version": CCDM_VERSION,
                "UI_Mode": "graphics",                  #UI_Mode choices are: "graphics" "lists-only"
                "Tab_BG_Color": "default",
                "Widget_Group_Type": "tile",            #Valid inputs: None, "tile"
                "Widget_Group_BG": "light blue",
                "EntryWidget_BG": "gray90",
                "Base_Font_Size": 14,                   #Valid range: 8-14 (might be limited based on screen res check)
                "Width_Override": 0,                    #Set UI Width override here (Minimum width = 1024), leave zero to allow CCDM to auto size to screen resolution
                "Height_Override": 0                    #Set UI Height override here (Minimum Height = 768), leave zero to allow CCDM to auto size to screen resolution
                }    

#Set Temperature Display Type
UI_TEMPERATURE_TYPE ="C"           #Valid Values are: "C" or "F"

#Set High to show Configuration Tab
UI_SHOW_CONFIGURATION = True


##--------------------- Path, Logging and Email Consts -------------------

#General Paths for use to access various resources
IMAGES_PATH = "resources/images/"
TEMPLATES_PATH = "resources/templates/"

#Set True to Allow daily logging feature
ENABLE_DAILY_LOGS = True      
LOGS_PATH = "CCDM_logs/"

#Set True to send daily log information via email
    #see email config file for set-up of statics
ENABLE_DAILY_EMAILS = False  

#Set Verbose Mode true to have program annunciate various process steps
VERBOSE_MODE = True
#Set Local Verbose Mode true to allow local methods to annunciate various process steps
LOCAL_VERBOSE_MODE = True  
