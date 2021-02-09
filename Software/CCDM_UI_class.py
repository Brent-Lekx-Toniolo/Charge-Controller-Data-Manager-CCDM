#----------------------------------------------------- Header ---------------------------------------------------

#CC UI class

#Original author: Brent Lekx-Toniolo
	#S.H.H.D.I.
	#Fort-Wisers
	#OoR Tech
   
	
    #Version 0.0.1 - beta:      
		#first trial beta release, b.lekx-toniolo
    #Version 0.0.2 - beta
                #second trial beta release (see release notes), b.lekx-toniolo



#----------------------------------------------------- Imports --------------------------------------------------

import tkinter as tk
from tkinter import ttk, Canvas, messagebox
from tkinter.ttk import *
import datetime

try:
    from PIL import ImageTk,Image
except:
    print("Could not import from Pillow (PIL), you may be missing Pillow Package")
    print("Pillow/PIL installation example (Linux Bash / Terminal):")
    print("python3 -m pip install -–upgrade pip")
    print("python3 -m pip install -–upgrade Pillow")
    print("Pillow/PIL installation example (Windows Comand Prompt):")
    print("pip3 install pillow")

    input("Press Enter key to exit....")
    exit()
from BLT_Misc import BLT_UI_DataDisplayGroup_Class2
 



#----------------------------------------------------------------------------------------------------------------


#------------------------------------- Class definition for Charge Controller Data Manager UI object ----------------------------------

class CCDM_UI_class:

    """CCDM UI Class"""

    def __init__(self, title, view_styles, show_conf, image_storage_location, verbose_mode=None):
        """Constructor

        verbose_mode: used to enable all methods to annunciation during runtime 
        (see also Local_Verbose_Mode arg in each method)
        type: bool

        title: used to set main title of UI container
        type: string

        tab_count: amount of tabs to build into UI
        type: int

        view_styles: various UI style information
        type: dictionary

        show_conf: set high to show charge controller programming values (extra detail, setpoints etc) in controller section of UI and this applications configuration
        type: bool

        image_storage_location: relative path from location of this python file to access images used in the UI
        type: string

        """
        #Init self variables with constructor params
        self.verbose_mode = verbose_mode
        self.title = title
        self.view_styles = view_styles
        self.show_conf = show_conf
        self.image_storage_location = image_storage_location

 
        #Init interals
        #General
        self.UI_opening_size = None
        self.currentDateTime = datetime.datetime.now()
        self.UI_root = tk.Tk()
        self.tab_control = ttk.Notebook(self.UI_root)
        self.tab_style = ttk.Style()
        self.tab = []
        self.UI_root_initiaized = 0
        self.UI_closing = 0
        self.AutoScroll_State = tk.IntVar()
        self.datetimestamp_lastautoscroll = self.currentDateTime #preload to get things started
        #Setup UI Root Width and Height Values
        if self.view_styles["Width_Override"] > 0:
            self.Detected_Screen_Width = self.view_styles["Width_Override"]
        else:
            self.Detected_Screen_Width = self.UI_root.winfo_screenwidth()
        if self.view_styles["Height_Override"] > 0:
            self.Detected_Screen_Height = self.view_styles["Height_Override"]
        else:
            self.Detected_Screen_Height = self.UI_root.winfo_screenheight()

        self.pad_x = 10
        self.pad_y = 10
        self.pad_y_bottom = 90         #Used to take into account general OS taskbar when task bar overlays this UI class instances

        self.widget_group = []          #widget group list for General Tab
        self.wg_width = []              #widget group widths
        self.wg_height = []             #widget group heights
        self.misc_widget_group = []     #widget group list for Misc Tab
        self.misc_wg_width = []         #widget group widths
        self.misc_wg_height = []        #widget group heights
        self.conf_widget_group = []     #widget group list for Configuration Tab
        self.conf_wg_width = []         #widget group widths
        self.conf_wg_height = []        #widget group heights

    
        #Create instances of images that will be dynamically updated

        self.image_file_solar = Image.open(self.image_storage_location + "Solar_Array.png")
        self.source_image_solar = ImageTk.PhotoImage(self.image_file_solar)

        self.image_file_wind = Image.open(self.image_storage_location + "wind_icon.png")
        self.source_image_wind = ImageTk.PhotoImage(self.image_file_wind)
        
        self.image_file_none = Image.open(self.image_storage_location + "none.png")
        self.weather_image_none = ImageTk.PhotoImage(self.image_file_none)

        self.image_file_night = Image.open(self.image_storage_location + "night_icon.png")
        self.weather_image_night = ImageTk.PhotoImage(self.image_file_night)

        self.image_file_cloudy = Image.open(self.image_storage_location + "cloudy_icon.png")
        self.weather_image_cloudy = ImageTk.PhotoImage(self.image_file_cloudy)

        self.image_file_partly_cloudy = Image.open(self.image_storage_location + "partly_cloudy_icon.png")
        self.weather_image_partly_cloudy = ImageTk.PhotoImage(self.image_file_partly_cloudy)

        self.image_file_sunny = Image.open(self.image_storage_location + "sunny_icon.png")
        self.weather_image_sunny = ImageTk.PhotoImage(self.image_file_sunny)

        self.image_file_sunny_shaded = Image.open(self.image_storage_location + "sunny_icon_shaded.png")
        self.weather_image_sunny_shaded = ImageTk.PhotoImage(self.image_file_sunny_shaded)

        self.weather_image_label = None


        #------------------------------------------------------------------------------------------------------------------------------
    def init_new_UI(self):
        #Initalize the empty UI and populate with widgets etc
        #Check / set screen resolution
        if self.Detected_Screen_Width >= 1024 and self.Detected_Screen_Height >= 768:
            self.UI_opening_size ="{0}x{1}+0+0".format(self.Detected_Screen_Width, self.Detected_Screen_Height)
            
            #Override Exit Event
            self.UI_root.protocol("WM_DELETE_WINDOW", self.on_exit)
            #Set Opening State
            self.UI_root.wm_state("normal")
            #Set UI Title
            self.UI_root.title(self.title)
            #Set size of UI_root
            self.UI_root.geometry(self.UI_opening_size)
            
            #Annunciate in verbose mode
            if self.verbose_mode:
                print("Created new UI root of size: "+self.UI_opening_size)
                
            self.UI_root_initialized = 1
            return self.UI_root_initialized
        else:
            print("    -> Your device does not support minimum screen resolution of 1024x768")
            input("Press Enter key to exit....")
            self.UI_root_initialized = 0
            return self.UI_root_initialized

    #------------------------------------------------------------------------------------------------------------------------------
    def init_UI_tabs(self, CC):

        #Place constraints around configured font size ----------------
        if self.verbose_mode:
            print("Checking constraints on font sizing vs screen resolution....")

        if self.view_styles["Base_Font_Size"] < 8:
            self.view_styles["Base_Font_Size"] = 8
            if self.verbose_mode:
                print("Font size configured is lower than valid value, font size has been limtied to "+str(self.view_styles["Base_Font_Size"]))
        elif self.view_styles["Base_Font_Size"] > 14:
            self.view_styles["Base_Font_Size"] = 14
            if self.verbose_mode:
                print("Font size configured is lower than valid value, font size has been limtied to "+str(self.view_styles["Base_Font_Size"]))
        elif (self.Detected_Screen_Width < 1920 or self.Detected_Screen_Height < 1080) and (self.Detected_Screen_Width >= 1600 and self.Detected_Screen_Height >= 900):
            self.view_styles["Base_Font_Size"] = 12
            if self.verbose_mode:
                print("Font size configured is lower than valid value, font size has been limtied to "+str(self.view_styles["Base_Font_Size"]))
        elif (self.Detected_Screen_Width < 1600 or self.Detected_Screen_Height < 900) and (self.Detected_Screen_Width >= 1280 and self.Detected_Screen_Height >= 800):
            self.view_styles["Base_Font_Size"] = 10
            if self.verbose_mode:
                print("Font size configured is lower than valid value, font size has been limtied to "+str(self.view_styles["Base_Font_Size"]))
        elif (self.Detected_Screen_Width < 1280 or self.Detected_Screen_Height < 800):
            self.view_styles["Base_Font_Size"] = 9
            if self.verbose_mode:
                print("Font size configured is too large for screen resolution, font size being limited to "+str(self.view_styles["Base_Font_Size"]))
            
        #Set Tab Styles
        self.tab_style.configure("TNotebook.Tab", font=("Ariel", self.view_styles["Base_Font_Size"] - 3))
        

        #Create Tabs required -----------------------------
        if self.verbose_mode:
            print("Creating UI Tabs")

        #Create General Tab
        self.tab.insert(0, ttk.Frame(self.tab_control))
        self.tab_control.add(self.tab[0], text="Overview")

        #Create Misc Tab
        self.tab.insert(1, ttk.Frame(self.tab_control))
        self.tab_control.add(self.tab[1], text="Misc")

        #Create Configuration Tab (conditional)
        if self.show_conf:
            self.tab.insert(2, ttk.Frame(self.tab_control))
            self.tab_control.add(self.tab[2], text="Configuration")

        #Create About Tab
        self.tab.append(ttk.Frame(self.tab_control))
        if self.show_conf:
            self.tab_control.add(self.tab[3], text="About")
        else:
            self.tab_control.add(self.tab[2], text="About")


        #Create widgets and graphics on General Tab -------------
        #Create static background graphics
        if self.view_styles["UI_Mode"] == "graphics":
            self.init_static_graphics(self.tab[0])
        #Create connection information area for Controller Tab
        self.init_connection_display(self.tab[0])
        #Create controller information area for Controller Tab
        self.init_controller_display(self.tab[0], CC.oem_series)
        #Create main display area for Controller Tab
        self.init_main_display(self.tab[0], CC)

        #Create connection information area for Controller Tab
        self.init_misc_display(self.tab[1], CC)

        #Create widgets and graphics on Configuration Tab ----------
        if self.show_conf:
            self.init_config_display(self.tab[2], CC.oem_series)
            
               
        #Create widgets and graphics on About Tab ----------
        if self.show_conf:
            self.init_about_display(self.tab[3])
        else:
            self.init_about_display(self.tab[2])
 
        #Finally, pack tabs
        self.tab_control.pack(expand = 1, fill = "both") #Fill container in both x and y directions

    #------------------------------------------------------------------------------------------------------------------------------
    def init_connection_display(self, target_tab):
        #Connection Widget Group
        connection_widgetgroup_labels =    [
                    "OEM - Series:",
                    "IP Address:",
                    "Port:",
                    "Connection State:"]

        #Instantiate new widget group and then get dims
        self.widget_group.insert(0, BLT_UI_DataDisplayGroup_Class2(target_tab, 22, connection_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.wg_width.insert(0, self.widget_group[0].get_width())
        self.wg_height.insert(0, self.widget_group[0].get_height())
        
        #Show Widget Group
        self.widget_group[0].show_group("Connection Information", self.pad_x, self.pad_y, frame_type = self.view_styles["Widget_Group_Type"],
                                        bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])
               
    #-----------------------------------------------------------------------------------------------------------------------------
    def init_controller_display(self, target_tab, CC_type):
        #Controller Widget Group

        #Create variable labels based on changes betwen different controllers
        if CC_type == "Midnite - Classic":
            variable_label_1 = "PCB Temperature:"
            variable_label_2 = "FET Temperature:"
            variable_label_3 = "InfoDataFlags:"
            
        elif CC_type =="Tristar - MPPT 60":
            variable_label_1 = "Heatsink Temperature:"
            variable_label_2 = "Spare:"
            variable_label_3 = "Fault Bits:"
            

        if self.view_styles["UI_Mode"] == "graphics":
            controller_widgetgroup_labels_col1 =    [
                    "MAC address:",
                    "Model:",
                    "Serial",
                    "HW Rev:",
                    "FW Rev:",
                    variable_label_1,
                    variable_label_2,
                    ]
            controller_widgetgroup_labels_col2 =    [
                    "Charge Stage:",
                    "MPPT Mode:",
                    "Lifetime KWh:",
                    "Lifetime Ahr:",
                    "Spare:",
                    "Spare:",
                    variable_label_3]
            #Instantiate new widget group and then get dims 
            self.widget_group.insert(1, BLT_UI_DataDisplayGroup_Class2(target_tab,20, controller_widgetgroup_labels_col1, controller_widgetgroup_labels_col2 , base_font_size = self.view_styles["Base_Font_Size"]))
            self.wg_width.insert(1, self.widget_group[1].get_width())
            self.wg_height.insert(1, self.widget_group[1].get_height())
            
            #Set group location
            group_x = (self.Detected_Screen_Width - self.wg_width[1]) / 2
            #Check for overrun into connection group
            if group_x < self.pad_x + self.wg_width[0] + self.pad_x:
                group_x = self.pad_x + self.wg_width[0] + self.pad_x    
            group_y = self.pad_y

            
        elif self.view_styles["UI_Mode"] == "lists-only":
            group_y = self.pad_y
            controller_widgetgroup_labels_col1 =    [
                    "MAC address:",
                    "Model:",
                    "Serial:",
                    "HW Rev:",
                    "FW Rev:",
                    variable_label_1,
                    variable_label_2,
                    "Charge Stage:",
                    "MPPT Mode:",
                    "Lifetime KWh:",
                    "Lifetime Ahr:",
                    "Spare",
                    "Spare:",
                    variable_label_3]
            controller_widgetgroup_labels_col2 = None
            #Instantiate new widget group and then get dims
            self.widget_group.insert(1, BLT_UI_DataDisplayGroup_Class2(target_tab,20, controller_widgetgroup_labels_col1, controller_widgetgroup_labels_col2 , base_font_size = self.view_styles["Base_Font_Size"]))
            self.wg_width.insert(1, self.widget_group[1].get_width())
            self.wg_height.insert(1, self.widget_group[1].get_height())
            
            #Set group location
            group_x = self.Detected_Screen_Width - (self.wg_width[1] + self.pad_x)
            group_y = self.pad_y + 30 #Add 30 to push down below Auto Scroll check box
            
        
        #Show Widget Group
        self.widget_group[1].show_group("Charge Controller Details", group_x, group_y, frame_type = self.view_styles["Widget_Group_Type"],
                                        bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])

    #------------------------------------------------------------------------------------------------------------------------------
    def init_main_display(self, target_tab, CC):

        #-------------------------------------------
        #Instantiate widget groups and then get dimensions
        
        #Source Data Widget Group
        harvest_widgetgroup_labels =    [
                    "Input Voltage:",
                    "Input Current:",
                    "Input Power:",
                    "Peak Input Power Today:"]
        self.widget_group.insert(2, BLT_UI_DataDisplayGroup_Class2(target_tab,15, harvest_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.wg_width.insert(2, self.widget_group[2].get_width())
        self.wg_height.insert(2, self.widget_group[2].get_height())
        
        #Controller Output Widget Group
        conversion_widgetgroup_labels =    [
                    "Output Voltage:",
                    "Output Current:",
                    "Output Power:",
                    "Calculated CC Efficiency:",
                    "KWh Harvested Today:",
                    "Ahr Harvested Today:",
                    "Peak Output Power Today:"]
        self.widget_group.insert(3, BLT_UI_DataDisplayGroup_Class2(target_tab,  15, conversion_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.wg_width.insert(3, self.widget_group[3].get_width())
        self.wg_height.insert(3, self.widget_group[3].get_height())

        
        #Shunt Widget Group
        shunt_widgetgroup_labels =    [
                    "Shunt Installed:",
                    "Shunt Temperature:",
                    "Shunt Current:",
                    "Calculated Load Current:",
                    "Calculated Load Power:",
                    "Net Ahr:"]
        self.widget_group.insert(4, BLT_UI_DataDisplayGroup_Class2(target_tab, 15, shunt_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.wg_width.insert(4, self.widget_group[4].get_width())
        self.wg_height.insert(4, self.widget_group[4].get_height())


        #Battery Widget Group
        battery_widgetgroup_labels =    [
                    "Battery Voltage:",
                    "Battery Temperature:",
                    "Battery SoC:",
                    "Battery Capacity:",
                    "Battery Remaining:",
                    "Estimated time to 50% SoC:",
                    "Estimated Battery freeze point:"]
        self.widget_group.insert(5, BLT_UI_DataDisplayGroup_Class2(target_tab, 15, battery_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.wg_width.insert(5, self.widget_group[5].get_width())
        self.wg_height.insert(5, self.widget_group[5].get_height())


        #-------------------------------------------
        #Set-up positional data based upon screen width, UI_Mode type and widget group widths
        if self.view_styles["UI_Mode"] == "graphics":
            #Init static images / graphics
            self.init_static_images(target_tab, CC.oem_series)
            #Set base locations for widget groups
            Widgetgroup2_x = self.pad_x
            Widgetgroup2_y = self.Detected_Screen_Height - (self.wg_height[2] + self.pad_y_bottom)        
            Widgetgroup3_x = (self.Detected_Screen_Width - self.wg_width[3]) / 2
            Widgetgroup3_y = self.Detected_Screen_Height - (self.wg_height[3] + self.pad_y_bottom)        
            Widgetgroup4_x = self.Detected_Screen_Width - (self.wg_width[4] + self.pad_x)                
            Widgetgroup4_y = self.pad_y + self.wg_height[1] + self.pad_y
            Widgetgroup5_x = self.Detected_Screen_Width - (self.wg_width[5] + self.pad_x)                
            Widgetgroup5_y = self.Detected_Screen_Height - (self.wg_height[5] + self.pad_y_bottom)        
            #Check for group overruns
            if Widgetgroup3_x + self.wg_width[3] >= Widgetgroup5_x:
                Widgetgroup3_x = (((self.Detected_Screen_Width - (self.pad_x + self.wg_width[2] + self.pad_x + self.wg_width[3] + self.pad_x + self.wg_width[5] + self.pad_x)) / 2) + self.pad_x + self.wg_width[2] + self.pad_x)
                print(Widgetgroup3_x)
        elif self.view_styles["UI_Mode"] == "lists-only":
            #Set base locations for widget groups
            Widgetgroup2_x = (self.Detected_Screen_Width - self.wg_width[2]) /2          
            Widgetgroup2_y = self.pad_y
            Widgetgroup3_x = (self.Detected_Screen_Width - self.wg_width[3]) /2          
            Widgetgroup3_y = self.pad_y + self.wg_height[2] + self.pad_y
            Widgetgroup4_x = (self.Detected_Screen_Width - self.wg_width[4]) /2          
            Widgetgroup4_y = self.pad_y + self.wg_height[2] + self.pad_y + self.wg_height[3] + self.pad_y
            Widgetgroup5_x = (self.Detected_Screen_Width - self.wg_width[5]) /2          
            Widgetgroup5_y = self.pad_y + self.wg_height[2] + self.pad_y + self.wg_height[3] + self.pad_y + self.wg_height[4] + self.pad_y

        else:
            print("   -> No main display created due to invalid UI_VIEW_TYPE, see CCDM_config.py")



        #-------------------------------------------
        #Show Widget Groups
            
        #Source Data Widget Group
        self.widget_group[2].show_group("Source", Widgetgroup2_x, Widgetgroup2_y, frame_type = self.view_styles["Widget_Group_Type"],
                                        bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])
        #Controller Output Widget Group
        self.widget_group[3].show_group("Controller Output", Widgetgroup3_x, Widgetgroup3_y, frame_type = self.view_styles["Widget_Group_Type"],
                                        bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])

        #Shunt Widget Group
        self.widget_group[4].show_group("Shunt / Load Data", Widgetgroup4_x, Widgetgroup4_y, frame_type = self.view_styles["Widget_Group_Type"],
                                        bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])


        #Battery Widget Group
        self.widget_group[5].show_group("Battery Data",  Widgetgroup5_x, Widgetgroup5_y, frame_type = self.view_styles["Widget_Group_Type"],
                                        bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])
        

        #Place initial input source image
        self.source_image_label = Label(self.tab[0], image = self.source_image_solar)
        self.source_image_label.place(x = self.pad_x, y = (self.Detected_Screen_Height / 2) - self.pad_y_bottom)

        #Place initial default dynamic weather image (night moon)
        self.weather_image_label = Label(self.tab[0], image = self.weather_image_night)
        self.weather_image_label.place(x = 45, y = (self.pad_y + self.wg_height[0] + self.pad_y))

        #-------------------------------------------
        #Show Auto scroll check box
        AutoScroll_Checkbox = Checkbutton(target_tab, text = "Auto Scroll", variable = self.AutoScroll_State)
        AutoScroll_Checkbox.place(x = self.Detected_Screen_Width - 100, y = self.pad_y)
 

    #------------------------------------------------------------------------------------------------------------------------------
    def init_static_images(self, target_tab, CC_type):

        #Midnite Classic Image
        #First set proper image file name for Charge Controller configured
        if CC_type == "Midnite - Classic":
            cc_image_filename = "Midnite - Classic.png"
        elif CC_type == "Tristar - MPPT 60":
            cc_image_filename = "Tristar - MPPT 60.png"
        image_file = Image.open(self.image_storage_location + cc_image_filename)
        charge_controller_image = ImageTk.PhotoImage(image_file)
        cc_image_label = Label(target_tab, image=charge_controller_image)
        cc_image_label.image = charge_controller_image
        cc_image_label.place(x = self.Detected_Screen_Width / 2, y = (self.Detected_Screen_Height / 2) - self.pad_y_bottom + 25)


        #Battery Image
        image_file = Image.open(self.image_storage_location +"Rolls Battery.png")
        battery_image = ImageTk.PhotoImage(image_file)
        battery_image_label = Label(target_tab, image=battery_image)
        battery_image_label.image = battery_image
        battery_image_label.place(x = self.Detected_Screen_Width - 300, y = (self.Detected_Screen_Height / 2) - self.pad_y_bottom + 150)

        
    #-----------------------------------------------------------------------------------------------------------------------------
    def init_static_graphics(self, target_tab):

        #Create new Canvas object
            graphics_canvas = tk.Canvas(target_tab)                #weather_image = ImageTk.PhotoImage(image_file)
                #weather_image_label = Label(self.tab[0], image=weather_image)


        #Calculate base locations for items
            horiz_negwire_base_y = self.Detected_Screen_Height / 2 + 9
            horiz_poswire_base_y = self.Detected_Screen_Height / 2 + 36
            horiz_padwires_y = 90
            vert_negwire_base_y1 = self.Detected_Screen_Width - 250
            vert_negwire_base_y2 = self.Detected_Screen_Width - 205
            
        #Create 3D Wires
            #Horizontal Neg
            graphics_canvas.create_line(50, horiz_negwire_base_y-2, self.Detected_Screen_Width - horiz_padwires_y, horiz_negwire_base_y-2, width = 1, fill = "gray60")
            graphics_canvas.create_line(50, horiz_negwire_base_y-1, self.Detected_Screen_Width - horiz_padwires_y, horiz_negwire_base_y-1, width = 1, fill = "gray50")
            graphics_canvas.create_line(50, horiz_negwire_base_y, self.Detected_Screen_Width - horiz_padwires_y, horiz_negwire_base_y, width = 1, fill = "gray33")
            graphics_canvas.create_line(50, horiz_negwire_base_y+1, self.Detected_Screen_Width - horiz_padwires_y, horiz_negwire_base_y+1, width = 1, fill = "gray33")
            graphics_canvas.create_line(50, horiz_negwire_base_y+2, self.Detected_Screen_Width - horiz_padwires_y, horiz_negwire_base_y+2, width = 2, fill = "black")
            #Horizontal Pos
            graphics_canvas.create_line(50, horiz_poswire_base_y-2, self.Detected_Screen_Width - horiz_padwires_y, horiz_poswire_base_y-2, width = 1, fill = "light coral")
            graphics_canvas.create_line(50, horiz_poswire_base_y-1, self.Detected_Screen_Width - horiz_padwires_y, horiz_poswire_base_y-1, width = 1, fill = "orange red")
            graphics_canvas.create_line(50, horiz_poswire_base_y, self.Detected_Screen_Width - horiz_padwires_y, horiz_poswire_base_y, width = 1, fill = "red")
            graphics_canvas.create_line(50, horiz_poswire_base_y+1, self.Detected_Screen_Width - horiz_padwires_y, horiz_poswire_base_y+1, width = 1, fill = "red")
            graphics_canvas.create_line(50, horiz_poswire_base_y+2, self.Detected_Screen_Width - horiz_padwires_y, horiz_poswire_base_y+2, width = 2, fill = "red4")

            #Battery Neg
            graphics_canvas.create_line(vert_negwire_base_y1-2, horiz_negwire_base_y, vert_negwire_base_y1-2, horiz_negwire_base_y+57, width = 1, fill = "gray60")
            graphics_canvas.create_line(vert_negwire_base_y1-1, horiz_negwire_base_y, vert_negwire_base_y1-1, horiz_negwire_base_y+57, width = 1, fill = "gray50")
            graphics_canvas.create_line(vert_negwire_base_y1, horiz_negwire_base_y, vert_negwire_base_y1, horiz_negwire_base_y+57, width = 1, fill = "gray33")
            graphics_canvas.create_line(vert_negwire_base_y1+1, horiz_negwire_base_y, vert_negwire_base_y1+1, horiz_negwire_base_y+57, width = 1, fill = "gray33")
            graphics_canvas.create_line(vert_negwire_base_y1+2, horiz_negwire_base_y, vert_negwire_base_y1+2, horiz_negwire_base_y+57, width = 2, fill = "black")
            #Battery Pos
            graphics_canvas.create_line(vert_negwire_base_y2-2, horiz_poswire_base_y, vert_negwire_base_y2-2, horiz_poswire_base_y+30, width = 1, fill = "light coral")
            graphics_canvas.create_line(vert_negwire_base_y2-1, horiz_poswire_base_y, vert_negwire_base_y2-1, horiz_poswire_base_y+30, width = 1, fill = "orange red")
            graphics_canvas.create_line(vert_negwire_base_y2, horiz_poswire_base_y, vert_negwire_base_y2, horiz_poswire_base_y+30, width = 1, fill = "red")
            graphics_canvas.create_line(vert_negwire_base_y2+1, horiz_poswire_base_y, vert_negwire_base_y2+1, horiz_poswire_base_y+30, width = 1, fill = "red")
            graphics_canvas.create_line(vert_negwire_base_y2+2, horiz_poswire_base_y, vert_negwire_base_y2+2, horiz_poswire_base_y+30, width = 2, fill = "red4")

            #To Load Text
            graphics_canvas.create_text(self.Detected_Screen_Width - 63, horiz_negwire_base_y, anchor="w", font = ("Arial", self.view_styles["Base_Font_Size"]), text = "To")
            graphics_canvas.create_text(self.Detected_Screen_Width - 70, horiz_poswire_base_y, anchor="w", font = ("Arial", self.view_styles["Base_Font_Size"]), text = "Load")

            #Finally pack canvas items
            graphics_canvas.pack(expand = 1, fill = "both")
    #------------------------------------------------------------------------------------------------------------------------------
    def update_dynamic_images(self, CC):
        
        #---------- Input Source Image (Solar Array / Wind Turbine) ----------------
        if CC.oem_series != None and CC.MPPT_Mode != None:
            if CC.oem_series == "Midnite - Classic":
                #Solar Mode
                if CC.MPPT_Mode == "1" or CC.MPPT_Mode == "3" or CC.MPPT_Mode == "9" or CC.MPPT_Mode == "11":  
                    self.source_image_label.configure(image = self.source_image_solar)
                #Wind Mode
                elif CC.MPPT_Mode == "5" or CC.MPPT_Mode == "7":
                    self.source_image_label.configure(image = self.source_image_wind)
        
            elif CC.oem_series == "Tristar - MPPT 60":
                #Solar Array Image
                self.source_image_label.configure(image = self.source_image_solar)


        #------------ Weather Images (Sunny / Partly Cloudy / Cloudy / Night)------------------
        if CC.oem_series != None and CC.Input_Watts != None and CC.expected_max_power != None and CC.Charge_Stage_Message != None and CC.MPPT_Mode != None:
            fCC_Input_Power = float(CC.Input_Watts)

            #Only update weather images for CCs in solar mode
            if CC.MPPT_Mode == "1" or CC.MPPT_Mode == "3" or CC.MPPT_Mode == "9" or CC.MPPT_Mode == "11":     
                #PV Partially Shaded    
                if CC.oem_series == "Midnite - Classic" and CC.InfoData_FlagsBin[9] != None and CC.InfoData_FlagsBin[9] == "1":
                    self.weather_image_label.configure(image = self.weather_image_sunny_shaded)

                else:
                    if CC.Charge_Stage_Message[0:6] == "Absorb" or CC.Charge_Stage_Message[0:5] == "Float" or CC.Charge_Stage_Message[0:5] == "Equalize" :
                        self.weather_image_label.configure(image = self.weather_image_sunny)
                            
                    elif CC.Charge_Stage_Message[0:9] == "Bulk MPPT" and (fCC_Input_Power / float(CC.expected_max_power)) >= 0.7:
                        self.weather_image_label.configure(image = self.weather_image_sunny)
                            
                    elif CC.Charge_Stage_Message[0:9] == "Bulk MPPT" and (fCC_Input_Power / float(CC.expected_max_power)) < 0.7 and (fCC_Input_Power / float(CC.expected_max_power)) >= 0.2:
                        self.weather_image_label.configure(image = self.weather_image_partly_cloudy)
                            
                    elif CC.Charge_Stage_Message[0:9] == "Bulk MPPT" and (fCC_Input_Power / float(CC.expected_max_power)) < 0.2:
                        self.weather_image_label.configure(image = self.weather_image_cloudy)
                            
                    else:
                        self.weather_image_label.configure(image = self.weather_image_night)
                        
            #Blank weather images in wind mode
            elif CC.MPPT_Mode == "5" or CC.MPPT_Mode == "7":
                self.weather_image_label.configure(image = self.weather_image_none)
                
        #-----------------------
        #Process Auto scroll feature
        if self.AutoScroll_State.get() == 1:
            self.auto_scroll()

    #------------------------------------------------------------------------------------------------------------------------------
    def init_misc_display(self, target_tab, CC):
        #Create Widgets and Graphics on Misc Tab

        #Connection Widget Group
        CCconnection_widgetgroup_labels =    [
                    "OEM - Series:",
                    "IP Address:",
                    "Port:",
                    "Connection State:"]

        #Instantiate new widget group and then get dims
        self.misc_widget_group.insert(0, BLT_UI_DataDisplayGroup_Class2(target_tab, 22, CCconnection_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.misc_wg_width.insert(0, self.misc_widget_group[0].get_width())
        self.misc_wg_height.insert(0, self.misc_widget_group[0].get_height())

        #Show Widget Group
        self.misc_widget_group[0].show_group("Connection Information", self.pad_x, self.pad_y, frame_type = self.view_styles["Widget_Group_Type"],
                                             bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])

        #Peaks and events group
        CCpeaks_widgetgroup_labels =    [
                    "Peak Input Watts:",
                    "Peak Output Watts:",
                    "Peak Output Voltage:",
                    "Peak Output Current:",
                    "Peak CC Temperature:",
                    "Maximum Battery Temperature:",
                    "Minimum Battery Temperature:",
                    "Maximum Battery Voltage:",
                    "Minimum Battery Voltage:",
                    "Absorb Reached Today:",
                    "Time in Absorb Today",
                    "Float Reached Today:",
                    "Time in Float Today:"]
        #Instantiate new widget group and then get dims
        self.misc_widget_group.insert(1, BLT_UI_DataDisplayGroup_Class2(target_tab, 20, CCpeaks_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.misc_wg_width.insert(1, self.misc_widget_group[1].get_width())
        self.misc_wg_height.insert(1, self.misc_widget_group[1].get_height())

        #Set position
        Widgetgroup1_x = self.pad_x          
        Widgetgroup1_y = self.pad_y + self.misc_wg_height[0] + self.pad_y

        #Show Widget Group
        self.misc_widget_group[1].show_group("Peaks and Events (today)", Widgetgroup1_x, Widgetgroup1_y , frame_type = self.view_styles["Widget_Group_Type"],
                                             bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])



        #Charge Controller Flags Widget Group
        if CC.oem_series == "Midnite - Classic":
            #Controller Info Flags Group
            CCinfoflags_widgetgroup_labels =    [
                        "Over Temperature:",
                        "EEPROM Error:",
                        "Serial Write Lock:",
                        "EQ In Progress:",
                        "EQ MPPT:",
                        "In V is Lower than Out:",
                        "Output Current Limit:",
                        "Hyper VOC:",
                        "Battery Temp Sens Installed:",
                        "Aux1 On:",
                        "Aux2 On:",
                        "Ground Fault Detected:",
                        "HW Over Current Protection On:",
                        "Arc Fault Detected:",
                        "Negative Battery Current:",
                        "Extra Info to Display:",
                        "PV Partial Shading Detected:",
                        "Watch Dog Reset:",
                        "Battery is < 8.0 VDC:",
                        "Stack Jumper NOT Installed:",
                        "EQ Done:",
                        "Temp Comp Sens Shorted:",
                        "Unlock Jumper NOT Installed:",
                        "Xtra Jumper NOT Installed:",
                        "CC Input Shorted:"]
            
            #Instantiate new widget group then get width
            self.misc_widget_group.insert(2, BLT_UI_DataDisplayGroup_Class2(target_tab, 2, CCinfoflags_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
            self.misc_wg_width.insert(2, self.misc_widget_group[2].get_width())
            self.misc_wg_height.insert(2, self.misc_widget_group[2].get_height())
            
            #Set Position of Info Flags widget group based on screen size and widget group width
            Widgetgroup2_x = (self.Detected_Screen_Width - self.misc_wg_width[2]) / 2
            #Check of group overruns other groups
            if Widgetgroup2_x <= self.pad_x + self.misc_wg_width[1] + self.pad_x:
                Widgetgroup2_x = self.pad_x + self.misc_wg_width[1] + self.pad_x
            Widgetgroup2_y = self.pad_y
            
            #Show Widget Group
            self.misc_widget_group[2].show_group("Charge Controller Info Flags", Widgetgroup2_x, Widgetgroup2_y, frame_type = self.view_styles["Widget_Group_Type"],
                                                 bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])

        elif CC.oem_series == "Tristar - MPPT 60":
            #Controller Fault Bits Group
            CCfaultbits_widgetgroup_labels =    [
                        "Overcurrent:",
                        "FETs shorted:",
                        "Software bug:",
                        "Battery HVD:",
                        "Array HVD:",
                        "Settings Switch Changed:",
                        "Custom Settings Edit:",
                        "RTS Shorted",
                        "RTS Disconnected:",
                        "EEPROM Retry Limit:",
                        "Reserved:",
                        "Slave Control Timeout:"]
            
            #Instantiate new widget group then get width
            self.misc_widget_group.insert(2, BLT_UI_DataDisplayGroup_Class2(target_tab, 2, CCfaultbits_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
            self.misc_wg_width.insert(2, self.misc_widget_group[2].get_width())
            self.misc_wg_height.insert(2, self.misc_widget_group[2].get_height())
            
            #Set Position of Info Flags widget group based on screen size and widget group width
            Widgetgroup2_x = (self.Detected_Screen_Width - self.misc_wg_width[2]) / 2
            #Check of group overruns other groups
            if Widgetgroup2_x <= self.pad_x + self.misc_wg_width[1] + self.pad_x:
                Widgetgroup2_x = self.pad_x + self.misc_wg_width[1] + self.pad_x
            Widgetgroup2_y = self.pad_y
            
            #Show Widget Group
            self.misc_widget_group[2].show_group("Charge Controller Fault Bits", Widgetgroup2_x, Widgetgroup2_y, frame_type = self.view_styles["Widget_Group_Type"],
                                                 bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])



        #-------------------------------------------
        #Show Auto scroll check box
        AutoScroll_Checkbox = Checkbutton(target_tab, text = "Auto Scroll", variable = self.AutoScroll_State)
        AutoScroll_Checkbox.place(x = self.Detected_Screen_Width - 100, y = self.pad_y)


    #------------------------------------------------------------------------------------------------------------------------------
    def init_config_display(self, target_tab, CC_type):
        #Create Widgets and Graphics on Configuration Tab
        
        #Connection Widget Group
        CCconnection_widgetgroup_labels =    [
                    "OEM - Series:",
                    "IP Address:",
                    "Port:",
                    "Connection State:"]

        #Instantiate new widget group and then get dims
        self.conf_widget_group.insert(0, BLT_UI_DataDisplayGroup_Class2(target_tab, 22, CCconnection_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.conf_wg_width.insert(0, self.conf_widget_group[0].get_width())
        self.conf_wg_height.insert(0, self.conf_widget_group[0].get_height())

        #Show Widget Group
        self.conf_widget_group[0].show_group("Connection Information", self.pad_x, self.pad_y, frame_type = self.view_styles["Widget_Group_Type"],
                                             bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])

        
        #Controller Configuration Group
        CCconf_widgetgroup_labels =    [
                    "Nominal Battery Voltage:",
                    "Absorb Voltage Setpoint:",
                    "Absorb Time Setpoint:",
                    "Absorb End Amps:",
                    "Float Voltage Setpoint:",
                    "EQ Voltage Setpoint:",
                    "EQ Time Setpoint:",
                    "Maximum Temp Comp:",
                    "Minimum Temp Comp:",
                    "Temperature Comp Coeff:"]
        #Instantiate new widget group and then get dims
        self.conf_widget_group.insert(1, BLT_UI_DataDisplayGroup_Class2(target_tab, 20, CCconf_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.conf_wg_width.insert(1, self.conf_widget_group[1].get_width())
        self.conf_wg_height.insert(1, self.conf_widget_group[1].get_height())

        #Set position
        Widgetgroup1_x = self.pad_x          
        Widgetgroup1_y = self.pad_y + self.conf_wg_height[0] + self.pad_y

        #Show Widget Group
        self.conf_widget_group[1].show_group("Charge Controller General Configuration", Widgetgroup1_x, Widgetgroup1_y , frame_type = self.view_styles["Widget_Group_Type"],
                                             bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])



        #CCDM Application Configuration Group
        CCDMconf_widgetgroup_labels =    [
                    "Enable Daily Logs:",
                    "Enable Daily Emails:",
                    "UI Mode:",
                    "UI Tab BG Color:",
                    "Widget Group Type:",
                    "Widget Group Color:",
                    "Base Font Size:",
                    "Polling Rate:",
                    "CCDM Version:"]
        #Instantiate new widget group and then get dims
        self.conf_widget_group.insert(2, BLT_UI_DataDisplayGroup_Class2(target_tab, 20, CCDMconf_widgetgroup_labels, base_font_size = self.view_styles["Base_Font_Size"]))
        self.conf_wg_width.insert(2, self.conf_widget_group[2].get_width())
        self.conf_wg_height.insert(2, self.conf_widget_group[2].get_height())

        #Set position
        Widgetgroup2_x = self.Detected_Screen_Width - self.conf_wg_width[2] - self.pad_x          
        Widgetgroup2_y = self.pad_y + self.conf_wg_height[0] + self.pad_y

        #Show Widget Group
        self.conf_widget_group[2].show_group("CCDM Configuration", Widgetgroup2_x, Widgetgroup2_y , frame_type = self.view_styles["Widget_Group_Type"],
                                             bg_color = self.view_styles["Widget_Group_BG"], entry_bg_color = self.view_styles["EntryWidget_BG"])


        #-------------------------------------------
        #Show Auto scroll check box
        AutoScroll_Checkbox = Checkbutton(target_tab, text = "Auto Scroll", variable = self.AutoScroll_State)
        AutoScroll_Checkbox.place(x = self.Detected_Screen_Width - 100, y = self.pad_y)
            

    #------------------------------------------------------------------------------------------------------------------------------
    def init_about_display(self, target_tab):
        #Create Widgets and Graphics on About Tab

        #Create new Canvas object
        graphics_canvas = tk.Canvas(target_tab)
        #Set dimensions and location of about box tile / frame        
        box_width = 1000
        box_height = 668
        box_x_start = (self.Detected_Screen_Width - box_width) / 2
        box_y_start = 50
        box_x1 = box_x_start
        box_y1 = box_y_start
        box_x2 = box_x1 + box_width
        box_y2 = box_y_start
        box_x3 = box_x1 + box_width
        box_y3 = box_y1 + box_height
        box_x4 = box_x_start
        box_y4 = box_y1 + box_height
        text_start_x = box_x_start + 60
        text_start_y = box_y_start + 50
        base_font_size = self.view_styles["Base_Font_Size"]

        if self.view_styles["Widget_Group_Type"]  == "tile":
            #Create tile
            graphics_canvas.create_rectangle(box_x1, box_y1, box_x3, box_y3, fill = self.view_styles["Widget_Group_BG"], outline = self.view_styles["Widget_Group_BG"])
        else: 
            #Create box
            graphics_canvas.create_line(box_x1, box_y1, box_x2, box_y2, width = 1, fill = "white")
            graphics_canvas.create_line(box_x2, box_y2, box_x3, box_y3, width = 1, fill = "gray60")
            graphics_canvas.create_line(box_x3, box_y3, box_x4-1, box_y4, width = 1, fill = "gray60")
            graphics_canvas.create_line(box_x4, box_y4-2, box_x1, box_y1, width = 1, fill = "white")

            graphics_canvas.create_line(box_x1-1, box_y1-1, box_x2+1, box_y2-1, width = 1, fill = "gray60")
            graphics_canvas.create_line(box_x2+1, box_y2-1, box_x3+1, box_y3+1, width = 1, fill = "white")
            graphics_canvas.create_line(box_x3+1, box_y3+1, box_x4-1, box_y4+1, width = 1, fill = "white")
            graphics_canvas.create_line(box_x4-1, box_y4, box_x1-1, box_y1-1, width = 1, fill = "gray60")

                
        #Create Title
        graphics_canvas.create_text(text_start_x, text_start_y, text ="About Charge Controller Data Manager (CCDM):",
                                    font = ("arial", base_font_size + 3), anchor = "w")
        #CCDM Information
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 40, text = "Version:    "+ self.view_styles["Application_Version"] ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 70, text = "Created by and licensed (GNU AGPL V3) to: b.lekx-toniolo of S.H.H.D.I., Fort-Wisers, OoR Tech" ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 100, text = "Latest version available at: https://github.com/Brent-Lekx-Toniolo/Charge-Controller-Data-Manager-CCDM-" ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 130, text = "Requires: Python 3.8+, Tkinter (should come with python), Pillow (PIL fork) package" ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 160, text = "Tested on OSs: Win10, Linux Mint 17, Raspbian Stretch (on Pi 3B+) " ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 190, text = "Tested on the following Charge Controllers:" ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 180, text_start_y + 220, text = "- Midnite Solar, Classic Series" ,
                                    font = ("arial", base_font_size), anchor = "w")

        #Third party software title
        graphics_canvas.create_text(text_start_x, text_start_y + 400, text ="Third Party Software used in this application:",
                                    font = ("arial", base_font_size + 3), anchor = "w")

        graphics_canvas.create_text(text_start_x + 10, text_start_y + 440, text = "pyModbusTCP (v 0.1.8): created by and licensed (MIT lic.) to: l.lefebvre" ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 470, text = "pyModbusTCP is available at: https://github.com/sourceperl/pyModbusTCP" ,
                                    font = ("arial", base_font_size), anchor = "w")
        graphics_canvas.create_text(text_start_x + 10, text_start_y + 500, text = "Modifications made to pyModbusTCP for working in this application: NONE (as of CCDM "+ self.view_styles["Application_Version"]+")",
                                    font = ("arial", base_font_size), anchor = "w")
   


        #Finally pack canvas items
        graphics_canvas.pack(expand = 1, fill = "both")


        #-------------------------------------------
        #Show Auto scroll check box
        AutoScroll_Checkbox = Checkbutton(target_tab, text = "Auto Scroll", variable = self.AutoScroll_State)
        AutoScroll_Checkbox.place(x = self.Detected_Screen_Width - 100, y = self.pad_y)


    #------------------------------------------------------------------------------------------------------------------------------
    def blank_all_datawidgets(self):
        #Routine to blank out entry widgets if required

        #Blank General Tab widgets
        for widget_group in range(len(self.widget_group)):                                   #determine amount of widget groups in tab
            if widget_group >=1:
                for entry_in_group in range(len(self.widget_group[widget_group].generic_entry)):                   #detemine amount of entry widgets in widget group
                    self.widget_group[widget_group].entry_text[entry_in_group].set("")        #blank
                    
        #Blank Configuration Tab widgets, if tab exists
        if self.show_conf:
            for widget_group in range(len(self.conf_widget_group)):                                   #determine amount of widget groups in tab
                if widget_group ==1:
                    for entry_in_group in range(len(self.conf_widget_group[widget_group].generic_entry)):                   #detemine amount of entry widgets in widget group
                        self.conf_widget_group[widget_group].entry_text[entry_in_group].set("")        #blank
                elif widget_group==2:
                    for entry_in_group in range(len(self.conf_widget_group[widget_group].generic_entry)):                   #detemine amount of entry widgets in widget group
                        self.conf_widget_group[widget_group].generic_entry[entry_in_group].config(bg = self.view_styles["EntryWidget_BG"])       #blank
                
    #------------------------------------------------------------------------------------------------------------------------------
    def on_exit(self):
        self.UI_closing = 1
        if messagebox.showinfo("CCDM", "Thanks for using CCDM!"):
            self.UI_root.destroy()
          
    #------------------------------------------------------------------------------------------------------------------------------
    def run(self):
        #Run the UI
        self.UI_root.mainloop()

    #------------------------------------------------------------------------------------------------------------------------------
    def get_tab(self, which_tab = None):
        #Return Tab Array
        if which_tab == None:
            return self.tab
        else:
            return self.tab[which_tab]
    #------------------------------------------------------------------------------------------------------------------------------
    def auto_scroll(self, scroll_dwell = 15):
        #Scroll through all tabs

        #Gather current datetime
        datetime_current = datetime.datetime.now()


        #Evaluate current datetime vs the previous scroll datetimestamp + dwell (in seconds)
        if datetime_current >= self.datetimestamp_lastautoscroll + datetime.timedelta(seconds = scroll_dwell):
            #Gather which tab is the currently selected tab
            current_tab = self.tab_control.index(self.tab_control.select())

            
            #Evaluate if we can increment to the next tab or must reset back to the first tab
            if (current_tab + 1) <= (len(self.tab) - 1):          
                self.tab_control.select(self.tab[current_tab + 1])
                self.datetimestamp_lastautoscroll = datetime.datetime.now()
            else:
                self.tab_control.select(self.tab[0])
                self.datetimestamp_lastautoscroll = datetime.datetime.now()

    #------------------------------------------------------------------------------------------------------------------------------
    
