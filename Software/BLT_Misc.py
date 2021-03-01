#----------------------------------------------------- Header ---------------------------------------------------
#------------- Misc functions for general use -------------
#
#Original author: Brent Lekx-Toniolo
	#S.H.H.D.I.
	#Fort-Wisers
	#OoR Tech
	

#Rev Log:
   
	
    #Version 0.0.1 - beta:      
		#first trial beta release, b.lekx-toniolo
<<<<<<< HEAD:Software/BLT_Misc.py
=======
    #Version 0.0.2 - beta:      
		#second trial beta release, b.lekx-toniolo

>>>>>>> dev:Software Package_20201222/BLT_Misc.py


#----------------------------------------------------- Imports --------------------------------------------------

import tkinter as tk
from tkinter import ttk, Canvas
from tkinter.ttk import *

try:
    from PIL import ImageTk,Image
except:
    print("Could not import from Pillow (PIL), you may be missing Pillow Package")
    print("Pillow/PIL installation example (Linux Bash/Terminal):")
    print("python3 -m pip install -–upgrade pip")
    print("python3 -m pip install -–upgrade Pillow")
    print("Pillow/PIL installation example (Windows Command Prompt):")
    print("pip3 install pillow")
    
    input("Press Enter key to exit......")    
    exit()

from string import Template

#----------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------
# General use linear scaling function

def linear_scaling(unscaled_data, unscaled_upperlimit, unscaled_lowerlimit, scaled_upperlimit, scaled_lowerlimit):

    #Init some vars
    scaled_span = 0
    unscaled_span = 0
    scaling_factor = 0
    offset = 0
    scaled_data = 0
        
    #Calc Span of Scaled Input Values
    scaled_span = scaled_upperlimit - scaled_lowerlimit

    #Calc Span of Unscaled Input Values
    unscaled_span = unscaled_upperlimit - unscaled_lowerlimit


    #Calc Scaling Factor between two scales
    if unscaled_span != 0:
        scaling_factor = scaled_span / unscaled_span
	
    #Calc Offset using data above using  y = mx+b with b unknown for offset
    #Scaled_LowerLimit = Scaling_Factor  * Unscaled_LowerLimit + b
    offset = 0 - ((scaling_factor * unscaled_lowerlimit) - scaled_lowerlimit)
	

    #Return Scaled Data Based on above spans and offset value
    scaled_data = ((scaling_factor * unscaled_data) + offset)
    
    #Finally, return the scaled data
    return scaled_data

#--------------------------------------------------------------------------------------------------------------------
#General function for converting Temperature data from DegC to Deg F
def DegC_to_DegF(Temp_In_DegC):
    Temp_In_DegF = (Temp_In_DegC * 9/5) + 32

    #Round to 1 dec place
    Temp_In_DegF = round(Temp_In_DegF, 1)
    
    return Temp_In_DegF


#------------------------------------------------------------------------------------------------------------------
# General function for returning longest length (in chars) in a list
def find_longest_length(list):
    if list != None:
        longest_found = 0
        for entries in range(len(list)):
            length = len(list[entries])
            if length > longest_found:
                longest_found = length
    else:
        return 0
    return longest_found

#--------------------------------------------------------------------------------------------------------------------
#General function for returning a given 32 bit integer value as signed data
def int_to_signed32(data_to_sign):
    if data_to_sign & 0x80000000: #Signed bit is on (32nd bit)
        signed_data = ((data_to_sign & 0x7FFFFFFF)-2147483648)
    else:
         signed_data= data_to_sign
         
    return signed_data
#--------------------------------------------------------------------------------------------------------------------
#General function for returning a given 16 bit integer value as signed data
def int_to_signed(data_to_sign):
    if data_to_sign & 0x8000: #Signed bit is on (16th bit)
        signed_data = ((data_to_sign & 0x7FFF)-32768)
    else:
         signed_data= data_to_sign
         
    return signed_data

#--------------------------------------------------------------------------------------------------------------------
#General function for creating a circle in a more intuative manner than typical Tkinter create oval method
def create_circle(x_loc, y_loc, radius, target_canvas): #center coordinates, radius
    oval_x0 = x_loc - radius
    oval_y0 = y_loc - radius
    oval_x1 = x_loc + radius
    oval_y1 = y_loc + radius
    return target_canvas.create_oval(oval_x0, oval_y0, oval_x1, oval_y1)

#---------------------------------------------------------------------------------------------------------------------
#General function for opening and reading the contents of a file
def read_file_content(filename):
    try:
        target_file = open(filename, 'r', encoding='utf-8')
        file_content = target_file.read()
        return file_content
    except:
        print("    -> Could not open file")
        return 0

#---------------------------------------------------------------------------------------------------------------------
#General function for opening and reading the contents of a template type file
def read_templatefile_content(filename):
    try:
        target_template_file = open(filename, 'r', encoding='utf-8')
        template_file_content = target_template_file.read()
        return Template(template_file_content)
    except:
        print("    -> Could not open template file")
        return 0
    
#------------------------------------------------------------------------------------------------------------------------------
# Widget group Class (uses grid manager)
class BLT_UI_DataDisplayGroup_Class:

    """UI Class"""

    def __init__(self, UI_parent_target, ):
        """Constructor
  
        UI_parent_target: tkinter UI parent this widget group will belong to
        type: tkinter UI container (only tested on tabs so far)
        
        """
        #Init self variables with constructor params
        self.UI_parent_target = UI_parent_target
        #Init interals
        #General
        self.generic_label = []
        self.generic_entry = []
        self.entry_text = []

    #--------------------------------------------------------------------------------------
    def add_group(self, title, base_loc_col, base_loc_row, sticky, entry_width, first_widget_labels, second_widget_labels = None, group_padx = 5, group_pady = 5):
        """
 
        title: used to set main title of widget group label frame
        type: string
 
        base_loc_col: grid location manager, column location of this object
        type: int

        base_loc_row: grid location manager, row location of this object
        type: int

        sticky: sticky location of this object
        type: string values valid for tkinter sticky args

        entry_width: sets width of entry widgets
        type = int

        first_widget_labels: an array of strings to act as labels for widgets, also sets the count of widgets to be created in the group
        type: array of strings

        second_widget_labels (optional arg): an array of strings to act as labels for widgets, also sets the count of widgets to be created in the group
        this arg is optional, if the user passes an argument here it will create a SECOND column of lables and entries into the group
        type: array of strings

        group_padx and group_pady (optional arg): if argument is passed by user the passed value will over-ride the default values of 5
        type: int

        """
        #Label Frame
        self.generic_label_frame = tk.LabelFrame(self.UI_parent_target, text=title)
        self.generic_label_frame.grid(column = base_loc_col, row = base_loc_row, padx = group_padx, pady = group_pady, sticky = sticky)
        first_column_count = 0
        #Add Widgets in Label Frame
        if first_widget_labels != None:
            for widget in range(len(first_widget_labels)):
                self.generic_label.insert(widget, tk.Label(self.generic_label_frame, text = first_widget_labels[widget]))
                self.generic_label[widget].grid(column = 1, row = (widget+1), sticky = "W")
                self.entry_text.insert(widget, tk.StringVar()) #Create tkinter StringVar Array to allow .set() method to be used to update entry widgets
                self.generic_entry.insert(widget, tk.Entry(self.generic_label_frame, textvariable=self.entry_text[widget], width = entry_width))
                self.generic_entry[widget].grid(column = 2, row = (widget+1), padx = 20, pady = 2)
                first_column_count = widget
        else:
            print("I need an initialized widget_labels array argument to work, widget_labels given = "+widget_labels)
            return 0
        #If a second array of labels is passed, create a second column
        if second_widget_labels != None:
           for widget in range(len(second_widget_labels)):
                col2_widget = widget + first_column_count + 1
                self.generic_label.insert(col2_widget, tk.Label(self.generic_label_frame, text = second_widget_labels[widget]))
                self.generic_label[col2_widget].grid(column = 3, row = (widget+1), sticky = "W")
                self.entry_text.insert(col2_widget, tk.StringVar()) #Create tkinter StringVar Array to allow .set() method to be used to update entry widgets
                self.generic_entry.insert(col2_widget, tk.Entry(self.generic_label_frame, textvariable=self.entry_text[col2_widget], width = entry_width))
                self.generic_entry[col2_widget].grid(column = 4, row = (widget+1), padx = 20, pady = 2)
        return 1
    #----------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------------------------------
# Widget group Class (uses xy place manager)
class BLT_UI_DataDisplayGroup_Class2:

    """UI Class"""

    def __init__(self, UI_parent_target, entry_width_inchars, first_widget_labels, second_widget_labels = None, base_font_size = 10 ):
        """Constructor
  
        UI_parent_target: tkinter UI parent this widget group will belong to
        type: tkinter UI container (only tested on tabs so far)

        entry_width: sets width of entry widgets, in characters
        type = int

        first_widget_labels: an array of strings to act as labels for widgets, also sets the count of widgets to be created in the group
        type: array of strings

        second_widget_labels (optional arg): an array of strings to act as labels for widgets, also sets the count of widgets to be created in the group
        this arg is optional, if the user passes an argument here it will create a SECOND column of lables and entries into the group
        type: array of strings

        base_font_size: set font size for labels and widget data
        type: uint
        
        """
        #Init self variables with constructor params
        self.UI_parent_target = UI_parent_target
        self.entry_width_inchars = entry_width_inchars
        self.first_widget_labels = first_widget_labels
        self.second_widget_labels = second_widget_labels
        self.base_font_size = base_font_size
        
        #Init interals
        #General
        self.generic_label = []
        self.generic_entry = []
        self.generic_indicator = []
        self.entry_text = []


        #Find longest (in chars) label width requirements for column 1 labels
        self.first_longest = find_longest_length(self.first_widget_labels)
                    
        #Find longest (in chars) label width requirements for column 2 labels (if applicable)
        self.second_longest = find_longest_length(self.second_widget_labels)
        
            
        #Calculate some geometry
        self.child_pad_x = 10        #x padding for child widgets
        self.child_pad_y = 10        #y padding for child widgets
        self.frame_title_fontsize = self.base_font_size + 2
        self.frame_title_pady = 6    #y padding under frame title (between frame title and first widget pair)
        self.label_col1_width = self.first_longest * (self.base_font_size - 3)
        self.label_col2_width = self.second_longest * (self.base_font_size - 3)
        self.entry_width = self.entry_width_inchars * (self.base_font_size - 3)   
        self.label_entry_height = self.base_font_size * 2
        
        #Calculate x locations for col 1 labels and entries
        self.label_col1_loc_x = self.child_pad_x        
        self.entry_col1_loc_x = self.label_col1_loc_x + self.label_col1_width + self.child_pad_x 
   
        #Calculate x locations for col 2 labels and entries (if applicable)
        self.label_col2_loc_x = (self.child_pad_x + self.label_col1_width + self.child_pad_x + self.entry_width + self.child_pad_x)       
        self.entry_col2_loc_x = self.label_col2_loc_x + self.label_col2_width + self.child_pad_x 
        
        #Calulate Parent Label Frame dimensions
        if second_widget_labels != None:
            self.label_frame_width = (self.child_pad_x + self.label_col1_width + self.child_pad_x + self.entry_width + self.child_pad_x) + (self.child_pad_x + self.label_col2_width + self.child_pad_x + self.entry_width + self.child_pad_x)
            self.label_frame_height = self.child_pad_y + self.frame_title_fontsize + self.frame_title_pady + ((self.label_entry_height + 5) * len(first_widget_labels)) + self.child_pad_y
        else:
            self.label_frame_width = self.child_pad_x + self.label_col1_width + self.child_pad_x + self.entry_width + self.child_pad_x 
            self.label_frame_height = self.child_pad_y + self.frame_title_fontsize + self.frame_title_pady + ((self.label_entry_height + 5) * len(first_widget_labels)) + self.child_pad_y

    #--------------------------------------------------------------------------------------
    def get_width(self):
        return self.label_frame_width
    
    #--------------------------------------------------------------------------------------
    def get_height(self):
        return self.label_frame_height

    #--------------------------------------------------------------------------------------
    def show_group(self, title, base_loc_x, base_loc_y, frame_type = None, bg_color = None, entry_bg_color = None):
        """
 
        title: used to set main title of widget group label frame
        type: string

        base_loc_x: x base location of group
        type: int

        base_loc_y: y base location of group
        type: int

        frame_type: toggle between traditional label frame type of group container or tile type group container
        type: int, valid values = None, "tile"

        bg_color: background color of group tile if "tile" frame_type is selected
        type: string, valid values are all tkinter colors or color hex values
        
        entry_bg_color: background color of entry widgets
        type: string, valid values are all tkinter colors or color hex values

        base_font_size: set font size for labels and widget data
        type: uint

        """
                    
        #Add Parent Label Frame, 2 types possible, traditional or tile type
        if frame_type == "tile":
            self.generic_label_frame = tk.LabelFrame(self.UI_parent_target, text=title, bg=bg_color, bd=0, font = ("Arial", self.frame_title_fontsize))
            self.generic_label_frame.place(x = base_loc_x, y = base_loc_y, width=self.label_frame_width, height=self.label_frame_height)
            label_bg_color = bg_color
        else:
            self.generic_label_frame = tk.LabelFrame(self.UI_parent_target, text=title, bd=2, font = ("Arial", self.frame_title_fontsize))
            self.generic_label_frame.place(x = base_loc_x, y = base_loc_y, width=self.label_frame_width, height=self.label_frame_height)
            label_bg_color = None

        first_column_count = 0
        #Add first column of Widgets in Label Frame
        if self.first_widget_labels != None:
            for widget in range(len(self.first_widget_labels)):
                all_loc_y = (self.label_entry_height + 5) * widget + self.frame_title_pady
                self.generic_label.insert(widget, tk.Label(self.generic_label_frame, text = self.first_widget_labels[widget], bg = label_bg_color, font = ("Arial", self.base_font_size)))
                self.generic_label[widget].place(x = self.label_col1_loc_x, y = all_loc_y, width = self.label_col1_width, height = self.label_entry_height)
                self.entry_text.insert(widget, tk.StringVar()) #Create tkinter StringVar Array to allow .set() method to be used to update entry widgets
                self.generic_entry.insert(widget, tk.Entry(self.generic_label_frame, textvariable=self.entry_text[widget], width = self.entry_width, bg = entry_bg_color, font = ("Arial", self.base_font_size)))
                self.generic_entry[widget].place(x = self.entry_col1_loc_x, y = all_loc_y, width = self.entry_width, height = self.label_entry_height)
                first_column_count = widget
        else:
            print("I need an initialized widget_labels list argument to work, widget_labels given = "+widget_labels)
            return 0
        #If a second array of labels is passed, create a second column
        if self.second_widget_labels != None:
           for widget in range(len(self.second_widget_labels)):
                col2_widget = widget + first_column_count + 1
                all_loc_y = (self.label_entry_height + 5) * widget + self.frame_title_pady
                self.generic_label.insert(col2_widget, tk.Label(self.generic_label_frame, text = self.second_widget_labels[widget], bg = label_bg_color, font = ("Arial", self.base_font_size)))
                self.generic_label[col2_widget].place(x = self.label_col2_loc_x, y = all_loc_y, width = self.label_col2_width, height = self.label_entry_height)
                self.entry_text.insert(col2_widget, tk.StringVar()) #Create tkinter StringVar Array to allow .set() method to be used to update entry widgets
                self.generic_entry.insert(col2_widget, tk.Entry(self.generic_label_frame, textvariable=self.entry_text[col2_widget], width = self.entry_width, bg = entry_bg_color, font = ("Arial", self.base_font_size)))
                self.generic_entry[col2_widget].place(x = self.entry_col2_loc_x, y = all_loc_y, width = self.entry_width, height = self.label_entry_height)
        return 1

    #----------------------------------------------------------------------------------------

