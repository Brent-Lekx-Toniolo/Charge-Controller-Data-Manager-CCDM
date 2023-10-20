#----------------------------------------------------- Header ---------------------------------------------------
# Charge Controller Data Manager (CCDM)
# program used to connect to various charge controllers (generally used in the solar power generating industry), gather some data from them and display on a UI

#----------------------------------------------------------------------------------------------------------------
'''
Original author: Brent Lekx-Toniolo
	S.H.H.D.I.
	Fort-Wisers
	OoR Tech
	
Rev Log:
	
    Alpha Draft, b.lekx-toniolo:      
		created simple program and used Tkinter as UI platform
                future revs will create multi platformed UI options as well as database connectivity and data log options
    0.0.1 - beta, b.lekx-toniolo
                general preperation for distribution on GitHUB
    0.0.2 - beta
                second trial beta release (see release / build notes), b.lekx-toniolo



Charge-Controller-Data-Manager-CCDM is licensed under the GNU Affero General Public License v3.0
Terms of this license can be found in the License.md file of the CCDM GitHUB repository
The following files are considered to be part of the CCDM package and are included under the applications license:
    - This file
    - CCDM_config.py
    - CCDM_config_email_default.py
    - CC_class.py
    - CC_UI_class.py


The following external dependancies are required for the CCDM package and are included under the license:
    - BLT_Misc.py
    
The following third party software is used in the CCDM package:
    - pyModbusTCP: available at https://github.com/sourceperl/pyModbusTCP.git

A fork of this software package has been made availible on the Charge-Controller-Data-Manager-CCDM Repository
'''

#----------------------------------------------------------------------------------------------------------------


#----------------------------------------------------- Imports --------------------------------------------------
import datetime
import time
from BLT_Misc import *

#Import custom config if created, otherwise use default
try: 
    from CCDM_config import *
except:
    print("No custom config file found, importing default file")
    from CCDM_config_default import *

#Import custom email config if created, otherwise use default
try: 
    from CCDM_config_email import *
except:
    print("No custom email config file found, importing default file")
    from CCDM_config_email_default import *
    
from CCDM_UI_class import *
from CC_class import *
from threading import Thread

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#Global vars
BackGround_Thread = []
path_to_lastdailylog = None
CCDM_build_level = "20231020"

#-------------------------------------- Main Definition----------------------------------------------------------

def main(config_file):

    #Declare local vars
    CC = []
    UI = []
    daily_log_written = False
    daily_email_sent = False
    test_log_written = False
    test_email_sent = False
    

#add find cc routine here later for number of ccs found on network

    #Check CC count vs system maximum
    if CC_COUNT > MAX_CC_COUNT:
        print("Found more Charge Controllers than CCDM is capable of handling")
        print("(see CCDM_config.py file)")
        print("Found: "+str(CC_COUNT)+" Maximum Allowed: "+str(MAX_CC_COUNT))
        exit()
    else:
        print("Configuring CCDM for "+str(CC_COUNT)+" charge controller(s).......")
	
        
    
    #Build array of Charge Controllers
    for cc_index in range(CC_COUNT):
        #Instantiate new list of CC_class objects
        CC.insert(cc_index, CC_class(VERBOSE_MODE, CC_NAMES[cc_index], CC_OEM_TYPES[cc_index], CC_IP_ADDRS[cc_index], CC_PORTS[cc_index], CC_TIMEOUTS[cc_index], CC_EXPECTED_MAX_POWER[cc_index]))
        #Create a new list of UI_class objects and initilize
        UI.insert(cc_index, CCDM_UI_class(UI_TITLE, UI_VIEW_STYLES, UI_SHOW_CONFIGURATION, IMAGES_PATH, CCDM_build_level, VERBOSE_MODE))
    
        if UI[cc_index].init_new_UI():
            UI[cc_index].init_UI_tabs(CC[cc_index])
        else:
            print("    -> Failed to create UI root")
            exit()
            
        #Create seperate Back Ground thread for each charge controller communication tasks
        BackGround_Thread.insert(cc_index, Thread(target = BackGround_Tasks, args = (CC, UI, daily_log_written, daily_email_sent,)))
        #Run as background Daemon (IE independant of main loop flow)
        BackGround_Thread[cc_index].Daemon = True         
        #Start BackGround Tasks thread
        BackGround_Thread[cc_index].start()
	
    #Start UI Loop
    #NOTE: Only 1 controller UI for now
    UI[0].run()
 
#----------------------------------- Master While Loop ----------------------------------------------------------
def BackGround_Tasks(CC, UI, daily_log_written, daily_email_sent):
    while True:

        #Update Current Date and Time
        currentDateTime = datetime.datetime.now()

        for cc_index in range(CC_COUNT):
            #Check for exiting request from any UI, break for loop if so
            if UI[cc_index].UI_closing:
                break
            
            #Transfer data between CC <-> UI -----------------
            CC_To_UI_Exchange(CC[cc_index], UI[cc_index], VERBOSE_MODE)
            #Update UI dynamic images with updated CC data
            if UI_VIEW_STYLES["UI_Mode"] == "graphics":
                UI[cc_index].update_dynamic_images(CC[cc_index])
            #Update UI control elements    
            enable_email_testPB = ENABLE_DAILY_LOGS and ENABLE_DAILY_EMAILS and CC[cc_index].conn_state   
            UI[cc_index].update_control_elements(enable_email_testPB)

            #Connect if not already done ----------------
            #NOTE: for future seperate each controller connection to different threads
            if CC[cc_index].conn_state == None or CC[cc_index].conn_state == 0 or not CC[cc_index].TCP_Mod_Client.open():
                #Attempt Connection
                CC[cc_index].connect(UI[cc_index])
                

            #Read holding regs if connected -----------------
            if CC[cc_index].conn_state and CC[cc_index].TCP_Mod_Client.open():
                CC[cc_index].read_data()
            else:
                UI[cc_index].blank_all_datawidgets()
                if VERBOSE_MODE:
                    print("   -> Connection to "+CC[cc_index].name+" failed")

            #Logging and Email processes at end of day ------------
            if ((currentDateTime.hour == 23) and (currentDateTime.minute == 30)) or UI[cc_index].email_test_req:
                UI[cc_index].update_control_elements(enable_email_testPB)
                #Write Log Files if enabled
                if ENABLE_DAILY_LOGS:
                    if daily_log_written == False:
                        if VERBOSE_MODE:
                            print("Attempting to create daily log file....")
                        daily_log_written = write_log_files(CC[cc_index], currentDateTime)
                        if VERBOSE_MODE and daily_log_written:
                            print("New daily log file created")
                #Send daily email if enabled
                if ENABLE_DAILY_EMAILS:
                    if daily_email_sent == False:
                        if VERBOSE_MODE:
                            print("Attempting to send daily email....")
                        daily_email_sent = send_daily_email(currentDateTime)
                        if VERBOSE_MODE and daily_email_sent:
                            print("Daily email sent")
                        UI[cc_index].reset_email_req()
                       
            else:
                daily_log_written = False
                daily_email_sent = False

 
        #Check for exiting request from any UI, break while loop if so    
        if UI[cc_index].UI_closing:
            #NOTE: Add exit handling function call here (save data logging files etc)
            print("Exiting request has been made, breaking background loop")
            #Break from while loop
            break

        #While loop restart delay
        if VERBOSE_MODE:
            print("Sleeping on Controller Polling Rate ("+str(CC_POLLING_RATE)+"s)\n")
        time.sleep(CC_POLLING_RATE)                   

#-------------------------------------- CC <-> UI Data Exchange ------------------------------------------------
def CC_To_UI_Exchange(CC, UI, local_verbose_mode = None):
    #Function to Bind CC data to UI elements
 
    if local_verbose_mode:
        print("Data exchange with UI for "+CC.name)

    
#Bind Data to proper Entry widgets in UI

#Connection Widget Group on General Tab, Misc Tab and Configuration Tab
    #General Tab
    UI.widget_group[0].entry_text[0].set(CC.oem_series)
    UI.widget_group[0].entry_text[1].set(CC.ip_addr)
    UI.widget_group[0].entry_text[2].set(CC.port)
    if CC.conn_state == 0:
        UI.widget_group[0].entry_text[3].set("Not Connected")
    elif CC.conn_state == 1:
        UI.widget_group[0].entry_text[3].set("Connected")
    elif CC.conn_state ==10:    
        UI.widget_group[0].entry_text[3].set("Attempting Connection.....")
    else:
        UI.widget_group[0].entry_text[3].set("Unknown.....")
    #Configuration Tab
    UI.misc_widget_group[0].entry_text[0].set(CC.oem_series)
    UI.misc_widget_group[0].entry_text[1].set(CC.ip_addr)
    UI.misc_widget_group[0].entry_text[2].set(CC.port)
    if CC.conn_state == 0:
        UI.misc_widget_group[0].entry_text[3].set("Not Connected")
    elif CC.conn_state == 1:
        UI.misc_widget_group[0].entry_text[3].set("Connected")
    elif CC.conn_state ==10:    
        UI.misc_widget_group[0].entry_text[3].set("Attempting Connection.....")
    else:
        UI.misc_widget_group[0].entry_text[3].set("Unknown.....")
    #Configuration Tab
    if UI_SHOW_CONFIGURATION:
        UI.conf_widget_group[0].entry_text[0].set(CC.oem_series)
        UI.conf_widget_group[0].entry_text[1].set(CC.ip_addr)
        UI.conf_widget_group[0].entry_text[2].set(CC.port)
        if CC.conn_state == 0:
            UI.conf_widget_group[0].entry_text[3].set("Not Connected")
        elif CC.conn_state == 1:
            UI.conf_widget_group[0].entry_text[3].set("Connected")
        elif CC.conn_state ==10:    
            UI.conf_widget_group[0].entry_text[3].set("Attempting Connection.....")
        else:
            UI.conf_widget_group[0].entry_text[3].set("Unknown.....")
        #Application config data
        if ENABLE_DAILY_LOGS:
            UI.conf_widget_group[3].entry_text[0].set("Yes")
        else:
            UI.conf_widget_group[3].entry_text[0].set("No")
        if ENABLE_DAILY_EMAILS:
            UI.conf_widget_group[3].entry_text[1].set("Yes")
        else:
            UI.conf_widget_group[3].entry_text[1].set("No")
            
        UI.conf_widget_group[3].entry_text[2].set(UI_VIEW_STYLES["UI_Mode"])
        UI.conf_widget_group[3].entry_text[3].set(UI_VIEW_STYLES["Tab_BG_Color"])
        UI.conf_widget_group[3].entry_text[4].set(UI_VIEW_STYLES["Widget_Group_Type"])
        UI.conf_widget_group[3].entry_text[5].set(UI_VIEW_STYLES["Widget_Group_BG"])
        UI.conf_widget_group[3].entry_text[6].set(UI_VIEW_STYLES["Base_Font_Size"])
        UI.conf_widget_group[3].entry_text[7].set(str(CC_POLLING_RATE) + "    s")
        UI.conf_widget_group[3].entry_text[8].set(CCDM_VERSION)
                


#Begin sorting data by Configured Charge Controller OEM and Type

#Data Common to all CC types
    if CC.oem_series == "Midnite - Classic" or CC.oem_series == "Tristar - MPPT 60":
        #General Tab Elements --------------------------------
        #Controller Display Widgets (General Tab)
        #Column 1
        if CC.MAC_addr != None:
            UI.widget_group[1].entry_text[0].set(CC.MAC_addr)
        if CC.Unit_Type != None:
            UI.widget_group[1].entry_text[1].set(CC.Unit_Type)
        if CC.Serial != None:
            UI.widget_group[1].entry_text[2].set(CC.Serial)
        if CC.HW_Rev != None:
            UI.widget_group[1].entry_text[3].set(CC.HW_Rev)
        if CC.FW_Rev != None:
            UI.widget_group[1].entry_text[4].set(CC.FW_Rev)
        if UI_TEMPERATURE_TYPE == "C":
            if CC.PCB_Temperature != None:
                UI.widget_group[1].entry_text[5].set(CC.PCB_Temperature+"    deg.C")
            if CC.FET_Temperature != None:
                UI.widget_group[1].entry_text[6].set(CC.FET_Temperature+"    deg.C")
        if UI_TEMPERATURE_TYPE == "F":
            if CC.PCB_Temperature_DegF != None:
                UI.widget_group[1].entry_text[5].set(CC.PCB_Temperature_DegF+"    deg.F")
            if CC.FET_Temperature_DegF != None:
                UI.widget_group[1].entry_text[6].set(CC.FET_Temperature_DegF+"    deg.F")

        #Column 2
        if CC.Charge_Stage_Message != None:
            UI.widget_group[1].entry_text[7].set(CC.Charge_Stage_Message)
            if CC.Charge_Stage_Message[0:6] == "Absorb" or CC.Charge_Stage_Message[0:5] == "Float":
                UI.widget_group[1].generic_entry[7].config(bg = "green2")
            elif CC.Charge_Stage_Message[0:9] == "Bulk MPPT":
                UI.widget_group[1].generic_entry[7].config(bg = "yellow")
            else:
                UI.widget_group[1].generic_entry[7].config(bg = UI_VIEW_STYLES["EntryWidget_BG"])

        if CC.MPPT_Mode_Message != None:
            UI.widget_group[1].entry_text[8].set(CC.MPPT_Mode_Message)
        if CC.KWh_Lifetime != None:
            UI.widget_group[1].entry_text[9].set(CC.KWh_Lifetime+"    KWh")
        if CC.Ahr_Lifetime != None:
            UI.widget_group[1].entry_text[10].set(CC.Ahr_Lifetime+"    Ahr")
        if False: #Spare
            UI.widget_group[1].entry_text[11].set("")
        if False: #Spare
            UI.widget_group[1].entry_text[12].set("")
        if CC.InfoData_Flags != None and CC.Fault_FlagsBin == None:
            UI.widget_group[1].entry_text[13].set(CC.InfoData_Flags)
        if CC.InfoData_Flags == None and CC.Fault_FlagsBin != None:
            UI.widget_group[1].entry_text[13].set(CC.Fault_FlagsBin)

   
        #Source Data Display Widgets (General Tab)
        if CC.Input_Voltage != None:
            UI.widget_group[2].entry_text[0].set(CC.Input_Voltage+"    Vdc")
        if CC.Input_Current != None:
            UI.widget_group[2].entry_text[1].set(CC.Input_Current+"    A")
        if CC.Input_Watts != None:
            UI.widget_group[2].entry_text[2].set(CC.Input_Watts+"    Watts")
        if CC.Peak_Input_Watts != None:
            UI.widget_group[2].entry_text[3].set(CC.Peak_Input_Watts+"    Watts")

        #Conversion Data Display Widgets (General Tab)
        if CC.Output_Voltage != None:
            UI.widget_group[3].entry_text[0].set(CC.Output_Voltage+"    Vdc")
        if CC.Output_Current != None:
            UI.widget_group[3].entry_text[1].set(CC.Output_Current+"    A")
        if CC.Output_Watts != None:
            UI.widget_group[3].entry_text[2].set(CC.Output_Watts+"    Watts")
        if CC.Calced_CC_Eff != None:
            UI.widget_group[3].entry_text[3].set(CC.Calced_CC_Eff+"    %")
        if CC.KWh != None:
            UI.widget_group[3].entry_text[4].set(CC.KWh+"    KWh")
        if CC.Ahr != None:
            UI.widget_group[3].entry_text[5].set(CC.Ahr+"    Ahr")
        if CC.Peak_Output_Watts != None:
            UI.widget_group[3].entry_text[6].set(CC.Peak_Output_Watts+"    Watts")

        #Shunt Data Display Widgets (General Tab)
        if CC.Shunt_Installed == True:
            UI.widget_group[4].entry_text[0].set("Yes")
            if UI_TEMPERATURE_TYPE == "C":
                if CC.Shunt_Temperature != None:
                    UI.widget_group[4].entry_text[1].set(CC.Shunt_Temperature+"    deg.C")
            if UI_TEMPERATURE_TYPE == "F":
                if CC.Shunt_Temperature_DegF != None:
                    UI.widget_group[4].entry_text[1].set(CC.Shunt_Temperature_DegF+"    deg.F")
            if CC.Shunt_Current != None:
                UI.widget_group[4].entry_text[2].set(CC.Shunt_Current+"    A")
            if CC.Calced_Load_Current != None:
                UI.widget_group[4].entry_text[3].set(CC.Calced_Load_Current+"    A")
            if CC.Calced_Load_Power != None:
                UI.widget_group[4].entry_text[4].set(CC.Calced_Load_Power+"    Watts")
            if CC.Shunt_Net_Ahr != None:
                UI.widget_group[4].entry_text[5].set(CC.Shunt_Net_Ahr+"    Ahr")
        elif CC.Shunt_Installed == False:
            UI.widget_group[4].entry_text[0].set("No")
            UI.widget_group[4].entry_text[1].set("No Shunt")
            UI.widget_group[4].entry_text[2].set("No Shunt")
            UI.widget_group[4].entry_text[3].set("No Shunt")
            UI.widget_group[4].entry_text[4].set("No Shunt")
            UI.widget_group[4].entry_text[5].set("No Shunt")

        #Battery Data Display Widgets (General Tab)
        if CC.Battery_Voltage != None:
            UI.widget_group[5].entry_text[0].set(CC.Battery_Voltage+"    Vdc")
        if UI_TEMPERATURE_TYPE == "C":
            if CC.Battery_Temperature != None:
                UI.widget_group[5].entry_text[1].set(CC.Battery_Temperature+"    deg.C")
        if UI_TEMPERATURE_TYPE == "F":
            if CC.Battery_Temperature_DegF != None:
                UI.widget_group[5].entry_text[1].set(CC.Battery_Temperature_DegF+"    deg.F")
        if CC.Shunt_Installed == True:
            if CC.Battery_SOC != None:
                UI.widget_group[5].entry_text[2].set(CC.Battery_SOC+"    %")
            if CC.Battery_Capacity != None:
                UI.widget_group[5].entry_text[3].set(CC.Battery_Capacity+"    Ahr")
            if CC.Battery_Remaining != None:
                UI.widget_group[5].entry_text[4].set(CC.Battery_Remaining+"    Ahr")
            if CC.Calced_TimeTo_Batt50 != None:
                UI.widget_group[5].entry_text[5].set(CC.Calced_TimeTo_Batt50+"    Hours")
            if UI_TEMPERATURE_TYPE == "C":
                if CC.Calced_Batt_FreezeEstimate != None:
                    UI.widget_group[5].entry_text[6].set(CC.Calced_Batt_FreezeEstimate+"    deg.C")
            if UI_TEMPERATURE_TYPE == "F":
                if CC.Calced_Batt_FreezeEstimate_DegF != None:
                    UI.widget_group[5].entry_text[6].set(CC.Calced_Batt_FreezeEstimate_DegF+"    deg.F")
        elif CC.Shunt_Installed == False:
            UI.widget_group[5].entry_text[2].set("No Shunt")
            UI.widget_group[5].entry_text[3].set("No Shunt")
            UI.widget_group[5].entry_text[4].set("No Shunt")
            UI.widget_group[5].entry_text[5].set("No Shunt")
            UI.widget_group[5].entry_text[6].set("No Shunt")
        
        #Misc Tab Elements ----------------------
        if CC.Peak_Input_Watts != None:
            UI.misc_widget_group[1].entry_text[0].set(CC.Peak_Input_Watts+"    Watts")
        if CC.Peak_Output_Watts != None:
            UI.misc_widget_group[1].entry_text[1].set(CC.Peak_Output_Watts+"    Watts")
        if CC.Peak_Output_Voltage != None:
            UI.misc_widget_group[1].entry_text[2].set(CC.Peak_Output_Voltage+"    Vdc")
        if CC.Peak_Output_Current != None:
            UI.misc_widget_group[1].entry_text[3].set(CC.Peak_Output_Current+"    A")
        if UI_TEMPERATURE_TYPE == "C":
            if CC.Peak_CC_Temperature != None:
                UI.misc_widget_group[1].entry_text[4].set(CC.Peak_CC_Temperature+"    deg.C")
            if CC.Max_Batt_Temperature != None:
                UI.misc_widget_group[1].entry_text[5].set(CC.Max_Batt_Temperature+"    deg.C")
            if CC.Min_Batt_Temperature != None:
                UI.misc_widget_group[1].entry_text[6].set(CC.Min_Batt_Temperature+"    deg.C")
        if UI_TEMPERATURE_TYPE == "F":
            if CC.Peak_CC_Temperature_DegF != None:
                UI.misc_widget_group[1].entry_text[4].set(CC.Peak_CC_Temperature_DegF+"    deg.F")
            if CC.Max_Batt_Temperature_DegF != None:
                UI.misc_widget_group[1].entry_text[5].set(CC.Max_Batt_Temperature_DegF+"    deg.F")
            if CC.Min_Batt_Temperature_DegF != None:
                UI.misc_widget_group[1].entry_text[6].set(CC.Min_Batt_Temperature_DegF+"    deg.F")
        if CC.Max_Batt_Voltage != None:
            UI.misc_widget_group[1].entry_text[7].set(CC.Max_Batt_Voltage+"    Vdc")
        if CC.Min_Batt_Voltage != None:
            UI.misc_widget_group[1].entry_text[8].set(CC.Min_Batt_Voltage+"    Vdc")
        if CC.Event_Absorb_Reached != None:
            UI.misc_widget_group[1].entry_text[9].set(CC.Event_Absorb_Reached)
        if CC.Event_TimeIn_Absorb != None:
            UI.misc_widget_group[1].entry_text[10].set(CC.Event_TimeIn_Absorb+"    h")
        if CC.Event_Float_Reached != None:
            UI.misc_widget_group[1].entry_text[11].set(CC.Event_Float_Reached)
        if CC.Event_TimeIn_Float != None:
            UI.misc_widget_group[1].entry_text[12].set(CC.Event_TimeIn_Float+"    h")
        

        #Configuration Tab Elements-------------------
        if UI_SHOW_CONFIGURATION:
            #Controller Configuration Data Display Widgets (Configuration Tab)
            if CC.Conf_Nominal_Voltage != None:
                UI.conf_widget_group[1].entry_text[0].set(CC.Conf_Nominal_Voltage+"    V")
            if CC.Conf_Absorb_Setpoint != None:
                UI.conf_widget_group[1].entry_text[1].set(CC.Conf_Absorb_Setpoint+"    V")
            if CC.Conf_Absorb_Time != None:
                UI.conf_widget_group[1].entry_text[2].set(CC.Conf_Absorb_Time+"    h")
            if CC.Conf_End_Amps != None and CC.Shunt_Installed == True:
                UI.conf_widget_group[1].entry_text[3].set(CC.Conf_End_Amps+"    A")
            elif CC.Shunt_Installed == False:
                UI.conf_widget_group[1].entry_text[3].set("No Shunt")
            if CC.Conf_Float_Setpoint != None:
                UI.conf_widget_group[1].entry_text[4].set(CC.Conf_Float_Setpoint+"    V")
            if CC.Conf_EQ_Setpoint != None:
                UI.conf_widget_group[1].entry_text[5].set(CC.Conf_EQ_Setpoint+"    V")
            if CC.Conf_EQ_Time != None:
                UI.conf_widget_group[1].entry_text[6].set(CC.Conf_EQ_Time+"    h")
            #Temp Comp unit in Midnite Classic controllers is Voltage, unit in Tristar Controllers is deg C
            if CC.oem_series == "Midnite - Classic":
                temp_comp_unit = "V"
            elif CC.oem_series == "Tristar - MPPT 60":
                temp_comp_unit = "degC"
            if CC.Conf_MaxTemp_Comp != None:
                UI.conf_widget_group[1].entry_text[7].set(CC.Conf_MaxTemp_Comp+"    "+temp_comp_unit)
                
            if CC.Conf_MinTemp_Comp != None:
                UI.conf_widget_group[1].entry_text[8].set(CC.Conf_MinTemp_Comp+"    "+temp_comp_unit)
            if CC.Conf_TempComp_Value != None:
                UI.conf_widget_group[1].entry_text[9].set(CC.Conf_TempComp_Value+"    mv/DegC/Cell")
				
            if CC.Shunt_Installed == True:
                if CC.Battery_Capacity != None:
                    UI.conf_widget_group[2].entry_text[0].set(CC.Battery_Capacity+"    Ahr")
                if CC.Battery_EFF != None:
                    UI.conf_widget_group[2].entry_text[1].set(CC.Battery_EFF+"    %")
            elif CC.Shunt_Installed == False:
                UI.conf_widget_group[2].entry_text[0].set("No Shunt")
                UI.conf_widget_group[2].entry_text[1].set("No Shunt")



#Data conditional based upon Charge Controller Type ----------------
    if CC.oem_series == "Midnite - Classic":
            #Controller Info Flags Display Widgets (Misc Tab)
            if CC.InfoData_FlagsBin != None and (len(CC.InfoData_FlagsBin) == 32):
                #Over Temperature
                if CC.InfoData_FlagsBin[31] == "1":
                    UI.misc_widget_group[2].generic_entry[0].config(bg="red")
                elif CC.InfoData_FlagsBin[31] == "0":
                    UI.misc_widget_group[2].generic_entry[0].config(bg="white")
                #EEPROM Error
                if CC.InfoData_FlagsBin[30] == "1":
                    UI.misc_widget_group[2].generic_entry[1].config(bg="red")
                elif CC.InfoData_FlagsBin[30] == "0":
                    UI.misc_widget_group[2].generic_entry[1].config(bg="white")
                #Serial Write Lock
                if CC.InfoData_FlagsBin[29] == "1":
                    UI.misc_widget_group[2].generic_entry[2].config(bg="green")
                elif CC.InfoData_FlagsBin[29] == "0":
                    UI.misc_widget_group[2].generic_entry[2].config(bg="white")
                #EQ in progress
                if CC.InfoData_FlagsBin[28] == "1":
                    UI.misc_widget_group[2].generic_entry[3].config(bg="green")
                elif CC.InfoData_FlagsBin[28] == "0":
                    UI.misc_widget_group[2].generic_entry[3].config(bg="white")
                #EQ MPPT
                if CC.InfoData_FlagsBin[24] == "1":
                    UI.misc_widget_group[2].generic_entry[4].config(bg="yellow")
                elif CC.InfoData_FlagsBin[24] == "0":
                    UI.misc_widget_group[2].generic_entry[4].config(bg="white")
                #In V Lower than Out
                if CC.InfoData_FlagsBin[23] == "1":
                    UI.misc_widget_group[2].generic_entry[5].config(bg="yellow")
                elif CC.InfoData_FlagsBin[23] == "0":
                    UI.misc_widget_group[2].generic_entry[5].config(bg="white")
                #Current Limit
                if CC.InfoData_FlagsBin[22] == "1":
                    UI.misc_widget_group[2].generic_entry[6].config(bg="red")
                elif CC.InfoData_FlagsBin[22] == "0":
                    UI.misc_widget_group[2].generic_entry[6].config(bg="white")
                #HyperVOC
                if CC.InfoData_FlagsBin[21] == "1":
                    UI.misc_widget_group[2].generic_entry[7].config(bg="red")
                elif CC.InfoData_FlagsBin[21] == "0":
                    UI.misc_widget_group[2].generic_entry[7].config(bg="white")
                #Battery Temp Sens Installed
                if CC.InfoData_FlagsBin[18] == "1":
                    UI.misc_widget_group[2].generic_entry[8].config(bg="green")
                elif CC.InfoData_FlagsBin[18] == "0":
                    UI.misc_widget_group[2].generic_entry[8].config(bg="white")
                #Aux 1 State
                if CC.InfoData_FlagsBin[17] == "1":
                    UI.misc_widget_group[2].generic_entry[9].config(bg="green")
                elif CC.InfoData_FlagsBin[17] == "0":
                    UI.misc_widget_group[2].generic_entry[9].config(bg="white")
                #Aux 2 State
                if CC.InfoData_FlagsBin[16] == "1":
                    UI.misc_widget_group[2].generic_entry[10].config(bg="green")
                elif CC.InfoData_FlagsBin[16] == "0":
                    UI.misc_widget_group[2].generic_entry[10].config(bg="white")
                #Ground Fault Detected
                if CC.InfoData_FlagsBin[15] == "1":
                    UI.misc_widget_group[2].generic_entry[11].config(bg="red")
                elif CC.InfoData_FlagsBin[15] == "0":
                    UI.misc_widget_group[2].generic_entry[11].config(bg="white")
                #Hardware Over Current Protection
                if CC.InfoData_FlagsBin[14] == "1":
                    UI.misc_widget_group[2].generic_entry[12].config(bg="red")
                elif CC.InfoData_FlagsBin[14] == "0":
                    UI.misc_widget_group[2].generic_entry[12].config(bg="white")
                #Arc Fault Detected
                if CC.InfoData_FlagsBin[13] == "1":
                    UI.misc_widget_group[2].generic_entry[13].config(bg="red")
                elif CC.InfoData_FlagsBin[13] == "0":
                    UI.misc_widget_group[2].generic_entry[13].config(bg="white")
                #Negative Battery Current
                if CC.InfoData_FlagsBin[12] == "1":
                    UI.misc_widget_group[2].generic_entry[14].config(bg="red")
                elif CC.InfoData_FlagsBin[12] == "0":
                    UI.misc_widget_group[2].generic_entry[14].config(bg="white")
                #Extra Info to Display
                if CC.InfoData_FlagsBin[10] == "1":
                    UI.misc_widget_group[2].generic_entry[15].config(bg="yellow")
                elif CC.InfoData_FlagsBin[10] == "0":
                    UI.misc_widget_group[2].generic_entry[15].config(bg="white")
                #PV Partial Shaded
                if CC.InfoData_FlagsBin[9] == "1":
                    UI.misc_widget_group[2].generic_entry[16].config(bg="yellow")
                elif CC.InfoData_FlagsBin[9] == "0":
                    UI.misc_widget_group[2].generic_entry[16].config(bg="white")
                #Watchdog Reset
                if CC.InfoData_FlagsBin[8] == "1":
                    UI.misc_widget_group[2].generic_entry[17].config(bg="yellow")
                elif CC.InfoData_FlagsBin[8] == "0":
                    UI.misc_widget_group[2].generic_entry[17].config(bg="white")
                #Battery <8.0V
                if CC.InfoData_FlagsBin[7] == "1":
                    UI.misc_widget_group[2].generic_entry[18].config(bg="red")
                elif CC.InfoData_FlagsBin[7] == "0":
                    UI.misc_widget_group[2].generic_entry[18].config(bg="white")
                #Stack Jumper NOT Installed
                if CC.InfoData_FlagsBin[6] == "1":
                    UI.misc_widget_group[2].generic_entry[19].config(bg="green")
                elif CC.InfoData_FlagsBin[6] == "0":
                    UI.misc_widget_group[2].generic_entry[19].config(bg="white")
                #EQ Done
                if CC.InfoData_FlagsBin[5] == "1":
                    UI.misc_widget_group[2].generic_entry[20].config(bg="green")
                elif CC.InfoData_FlagsBin[5] == "0":
                    UI.misc_widget_group[2].generic_entry[20].config(bg="white")
                #Temperature Compensation Shorted
                if CC.InfoData_FlagsBin[4] == "1":
                    UI.misc_widget_group[2].generic_entry[21].config(bg="red")
                elif CC.InfoData_FlagsBin[4] == "0":
                    UI.misc_widget_group[2].generic_entry[21].config(bg="white")
                #Unlock Jumper NOT Installed
                if CC.InfoData_FlagsBin[3] == "1":
                    UI.misc_widget_group[2].generic_entry[22].config(bg="green")
                elif CC.InfoData_FlagsBin[3] == "0":
                    UI.misc_widget_group[2].generic_entry[22].config(bg="white")
                #Extra Jumper NOT Installed
                if CC.InfoData_FlagsBin[2] == "1":
                    UI.misc_widget_group[2].generic_entry[23].config(bg="green")
                elif CC.InfoData_FlagsBin[2] == "0":
                    UI.misc_widget_group[2].generic_entry[23].config(bg="white")
                #Input Shorted
                if CC.InfoData_FlagsBin[1] == "1":
                    UI.misc_widget_group[2].generic_entry[24].config(bg="red")
                elif CC.InfoData_FlagsBin[1] == "0":
                    UI.misc_widget_group[2].generic_entry[24].config(bg="white")

    if CC.oem_series == "Tristar - MPPT 60":
            #Controller Info Flags Display Widgets (Configuration Tab)
            if CC.Fault_FlagsBin != None:
                #Over Current
                if CC.Fault_FlagsBin[15] == "1":
                    UI.misc_widget_group[2].generic_entry[0].config(bg="red")
                elif CC.Fault_FlagsBin[15] == "0":
                    UI.misc_widget_group[2].generic_entry[0].config(bg="white")
                #FETs Shorted
                if CC.Fault_FlagsBin[14] == "1":
                    UI.misc_widget_group[2].generic_entry[1].config(bg="red")
                elif CC.Fault_FlagsBin[14] == "0":
                    UI.misc_widget_group[2].generic_entry[1].config(bg="white")
                #Software bug
                if CC.Fault_FlagsBin[13] == "1":
                    UI.misc_widget_group[2].generic_entry[2].config(bg="red")
                elif CC.Fault_FlagsBin[13] == "0":
                    UI.misc_widget_group[2].generic_entry[2].config(bg="white")
                #Battery HVD
                if CC.Fault_FlagsBin[12] == "1":
                    UI.misc_widget_group[2].generic_entry[3].config(bg="red")
                elif CC.Fault_FlagsBin[12] == "0":
                    UI.misc_widget_group[2].generic_entry[3].config(bg="white")
                #Array HVD
                if CC.Fault_FlagsBin[11] == "1":
                    UI.misc_widget_group[2].generic_entry[4].config(bg="red")
                elif CC.Fault_FlagsBin[11] == "0":
                    UI.misc_widget_group[2].generic_entry[4].config(bg="white")
                #Settings Switch Changed
                if CC.Fault_FlagsBin[10] == "1":
                    UI.misc_widget_group[2].generic_entry[5].config(bg="red")
                elif CC.Fault_FlagsBin[10] == "0":
                    UI.misc_widget_group[2].generic_entry[5].config(bg="white")
                #Custom Settings Edit
                if CC.Fault_FlagsBin[9] == "1":
                    UI.misc_widget_group[2].generic_entry[6].config(bg="red")
                elif CC.Fault_FlagsBin[9] == "0":
                    UI.misc_widget_group[2].generic_entry[6].config(bg="white")
                #RTS Shorted
                if CC.Fault_FlagsBin[8] == "1":
                    UI.misc_widget_group[2].generic_entry[7].config(bg="red")
                elif CC.Fault_FlagsBin[8] == "0":
                    UI.misc_widget_group[2].generic_entry[7].config(bg="white")
                #RTS Disconnected
                if CC.Fault_FlagsBin[7] == "1":
                    UI.misc_widget_group[2].generic_entry[8].config(bg="red")
                elif CC.Fault_FlagsBin[7] == "0":
                    UI.misc_widget_group[2].generic_entry[8].config(bg="white")
                #EEPROM Retry Limit
                if CC.Fault_FlagsBin[6] == "1":
                    UI.misc_widget_group[2].generic_entry[9].config(bg="red")
                elif CC.Fault_FlagsBin[6] == "0":
                    UI.misc_widget_group[2].generic_entry[9].config(bg="white")
                #!!!!!!!BIT 10 RESERVED!!!!!!!!!!!!!!!    
                #Slave Control Timeout
                if CC.Fault_FlagsBin[4] == "1":
                    UI.misc_widget_group[2].generic_entry[11].config(bg="red")
                elif CC.Fault_FlagsBin[4] == "0":
                    UI.misc_widget_group[2].generic_entry[11].config(bg="white")

#-------------------------------------------------------------------------------------------------------------------------------
def write_log_files(CC, currentDateTime):
    #Function to write a simple text file with some information about the day
    date_time_stamp = str(currentDateTime.year)+str(currentDateTime.month).zfill(2)+str(currentDateTime.day).zfill(2)+"_"+str(currentDateTime.hour).zfill(2)+str(currentDateTime.minute).zfill(2)
    #Assemble Path
    path_to_dailylog = LOGS_PATH+"CCDM_DailyLog_"+date_time_stamp+".txt"
    #Create blank log file
    new_log_file = open(path_to_dailylog, "w")
    new_log_file.close()
    #Open to append
    new_log_file = open(LOGS_PATH+"CCDM_DailyLog_"+date_time_stamp+".txt", "a")

    #Header
    new_log_file.write("Daily Log file generated by CCDM (Charge Controller Data Manager) \n")
    new_log_file.write("File created on: "+str(currentDateTime.year)+"-"+str(currentDateTime.month).zfill(2)+"-"+str(currentDateTime.day).zfill(2)+"   "+str(currentDateTime.hour).zfill(2)+":"+str(currentDateTime.minute).zfill(2)+" \n")
    new_log_file.write("\n\n\n")

    #CC Information:
    new_log_file.write("Charge Controller / System Information: \n")
    new_log_file.write("    CC Name: "+str(CC.name)+"\n")
    new_log_file.write("    CC Type: "+str(CC.oem_series)+"\n")
    new_log_file.write("    IP: "+str(CC.ip_addr)+"\n")
    new_log_file.write("    Port: "+str(CC.port)+"\n")
    new_log_file.write("    Connection State: "+str(CC.conn_state)+"\n")
    new_log_file.write("    Expected Max. CC Input Power: "+str(CC.expected_max_power)+" Watts \n")
    new_log_file.write("\n\n\n")
    
    #Actual Process Data:
    new_log_file.write("Daily Process Data: \n")
    #write notice in the event of a bad connection state during logging
    if CC.conn_state !=1:
        new_log_file.write("    NOTE:  -> Connection State to CC was not 1 (connected) at time of logging \n")
        new_log_file.write("              therefore some data values will not be valid \n")
            
    new_log_file.write("    Peak CC Input Power: "+str(CC.Peak_Input_Watts)+" Watts \n\n")
    new_log_file.write("    Peak CC Output Power: "+str(CC.Peak_Output_Watts)+" Watts \n")
    new_log_file.write("    Peak CC Output Voltage: "+str(CC.Peak_Output_Voltage)+" Vdc \n")
    new_log_file.write("    Peak CC Output Current: "+str(CC.Peak_Output_Current)+" A \n\n")
    if UI_TEMPERATURE_TYPE == "C":
        new_log_file.write("    Peak CC Temperature: "+str(CC.Peak_CC_Temperature)+" deg.C \n\n")
    if UI_TEMPERATURE_TYPE == "F":
        new_log_file.write("    Peak CC Temperature: "+str(CC.Peak_CC_Temperature_DegF)+" deg.F \n\n")
    new_log_file.write("    KWh harvested today: "+str(CC.KWh)+" KWh \n")
    new_log_file.write("    Ahr harvested today: "+str(CC.Ahr)+" Ahr \n\n")

    if UI_TEMPERATURE_TYPE == "C":
        new_log_file.write("    Max Battery Temperature: "+str(CC.Max_Batt_Temperature)+" deg.C \n")
        new_log_file.write("    Min Battery Temperature: "+str(CC.Min_Batt_Temperature)+" deg.C \n")
    if UI_TEMPERATURE_TYPE == "F":
        new_log_file.write("    Max Battery Temperature: "+str(CC.Max_Batt_Temperature_DegF)+" deg.F \n")
        new_log_file.write("    Min Battery Temperature: "+str(CC.Min_Batt_Temperature_DegF)+" deg.F \n")
    new_log_file.write("    Max Battery Voltage: "+str(CC.Max_Batt_Voltage)+" Vdc \n")
    new_log_file.write("    Min Battery Voltage: "+str(CC.Min_Batt_Voltage)+" Vdc \n\n")

    new_log_file.write("    Absorb reached today: "+str(CC.Event_Absorb_Reached)+" \n")
    new_log_file.write("    Time in absorb today: "+str(CC.Event_TimeIn_Absorb)+" h \n")
    new_log_file.write("    Float reached today: "+str(CC.Event_Float_Reached)+" \n")
    new_log_file.write("    Time in float today: "+str(CC.Event_TimeIn_Float)+" h \n")

    #Close File when complete
    new_log_file.close()
    return 1
#-------------------------------------------------------------------------------------------------------------------------------------------
def send_daily_email(currentDateTime):
    #Create a secure SSL context
    SSL_context = ssl.create_default_context()
    
    #Start the connection
    if VERBOSE_MODE:
        print("Creating SMTP Server.....")
    with smtplib.SMTP_SSL(host = EMAIL_config["smtp_host"], port = EMAIL_config["smtp_port"], context = SSL_context) as SMTP_server:
        if VERBOSE_MODE:
            print("Logging in to SMTP Server.....")
        try:
            #Login to mail server
            SMTP_server.login(EMAIL_config["username"], EMAIL_config["password"])


        except:
            if VERBOSE_MODE:
                print("    -> Login failed, check username and password")
                SMTP_server.quit()
                return 0

        #Create a blank MIME type email
        email = MIMEMultipart()   
        #Setup the parameters of the email
        email['From'] = EMAIL_config["from"]
        email['To'] = EMAIL_config["to"]
        email['Subject'] = EMAIL_config["subject"]

        #Create new email body section ------------
        email_body_template = read_templatefile_content(TEMPLATES_PATH+"CCDM_email_template.txt")
        #Generate Date Time Stamp        
        date_time_stamp = str(currentDateTime.year)+str(currentDateTime.month).zfill(2)+str(currentDateTime.day).zfill(2)+"_"+str(currentDateTime.hour).zfill(2)+str(currentDateTime.minute).zfill(2)
        #Assemble Path
        path_to_dailylog = LOGS_PATH+"CCDM_DailyLog_"+date_time_stamp+".txt"
        body_content = read_file_content(path_to_dailylog)
        #Assemble the template and log file content, add version stamp
        if email_body_template and body_content:
            email_body = email_body_template.substitute(BODY_MAIN_CONTENT = body_content, CCDM_CURR_VERSION = CCDM_VERSION)
        else:
            email_body = "This email is blank because Email Template or Daily Log file failed to open"
        #Add in the email body
        email.attach(MIMEText(email_body, 'plain'))

        #Finally, try to send complete email via the SMTP host set up above
        try:
            SMTP_server.send_message(email)
        except:
            if VERBOSE_MODE:
                print("Could not send email, check email configuration")
            del email
            SMTP_server.quit()
            return 0
     
        #If all was successful, close SMTP connection, delete email and return 1
        del email
        SMTP_server.quit()
        return 1
        
            
#---------------------------------- Main Call -------------------------------------------------------------------

if __name__=='__main__':
    main('config.txt')

	

#-----------------------------------------------------------------------------------------------------------------


