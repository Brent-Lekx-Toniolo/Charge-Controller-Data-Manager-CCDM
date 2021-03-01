#----------------------------------------------------- Header ---------------------------------------------------

#Charge Controller class

#Original author: Brent Lekx-Toniolo
	#S.H.H.D.I.
	#Fort-Wisers
	#OoR Tech
	

#Rev Log:
   
	
    #Version 0.0.1 - beta:      
		#first trial beta release, b.lekx-toniolo
<<<<<<< HEAD:Software/CC_class.py
=======
    #Version 0.0.2 - beta
                #second trial beta release (see release notes), b.lekx-toniolo
>>>>>>> dev:Software Package_20201222/CC_class.py


#----------------------------------------------------- Imports --------------------------------------------------

from pyModbusTCP.client import ModbusClient

try:
    from CC_Data_Manager import CC_To_UI_Exchange
    Valid_Dependancy = True
except:
    Valid_Dependancy = False
    
from BLT_Misc import linear_scaling, int_to_signed, int_to_signed32, DegC_to_DegF
import datetime
#----------------------------------------------------------------------------------------------------------------

#------------------------------------- Class definition for Charge Controller object ----------------------------------


class CC_class:

    """Charge Controller Class"""

    def __init__(self, verbose_mode, name, oem_series, ip_addr, port, tcp_timeout, expected_max_power = None):
        """Constructor
    
        verbose_mode param description: used to enable all methods to annunciation during runtime 
        (see also local_verbose_mode arg in each method)
        type: bool

        oem_series param description: sets which OEM and Series of Charge Controller self is
        type: string

        name param description: used as a simple name to describe the charge controller
        type: string

        ip_addr param description: IP Address of Charge Controller
        type: string

        port param description: Port of Server application running on Charge Controller (502 default for Midnite Classics)
        type: string

        tcp_timeout param description: Timeout, in milliseconds, for TCP connection
        type: float

        expected_max_power param description: Expected Maximum Input power for system
        type: int

        """
        #Init self variables with constructor params
        self.verbose_mode = verbose_mode
        self.name = name
        self.oem_series = oem_series
        self.ip_addr = ip_addr
        self.port = port
        self.tcp_timeout = tcp_timeout
        self.expected_max_power = expected_max_power

        #Init Internals
        self.TCP_Mod_Client = ModbusClient()
        self.dataread_DateTime_stamp = datetime.datetime.now()

        #Image of controller read data (Note: for future dev, this should be wrapped up in seperate class)
        self.conn_state = None
        self.MAC_addr = None
        self.Date_Time = None
        self.Unit_Type = None
        self.Serial = None
        self.FW_Rev = None
        self.FW_Build = None
        self.HW_Rev = None
        self.PCB_Temperature = None
        self.FET_Temperature = None
        self.PCB_Temperature_DegF = None
        self.FET_Temperature_DegF = None
        self.Charge_Stage = None
        self.Charge_Stage_Message = None
        self.Last_VoC_Measured = None
        self.Highest_InputV_Logged = None
        self.InfoData_Flags = None
        self.InfoData_FlagsBin = None
        self.Fault_FlagsBin = None
        self.Alarm_FlagsBin = None
        self.KWh_Lifetime = None
        self.Ahr_Lifetime = None
        self.MPPT_Mode = None
        self.MPPT_Mode_Message = None
        self.Aux1_Function = None
        self.Aux2_Function = None
     
        self.Input_Voltage = None
        self.Input_Current = None
        self.Input_Watts = None
        self.Output_Voltage = None
        self.Output_Current = None
        self.Output_Watts = None
        self.KWh = None
        self.Ahr = None
                
        self.Shunt_Installed = None
        self.Shunt_Temperature = None
        self.Shunt_Temperature_DegF = None
        self.Shunt_Current = None
        self.Shunt_Net_Ahr = None

        self.Battery_Voltage = None
        self.Battery_SOC = None
        self.Battery_Temperature = None
        self.Battery_Temperature_DegF = None
        self.Battery_Remaining = None
        self.Battery_Capacity = None

        self.Conf_Nominal_Voltage = None
        self.Conf_Absorb_Setpoint = None
        self.Conf_Absorb_Time = None
        self.Conf_End_Amps = None
        self.Conf_Float_Setpoint = None
        self.Conf_EQ_Setpoint = None
        self.Conf_EQ_Time = None
        self.Conf_MaxTemp_Comp = None
        self.Conf_MinTemp_Comp = None
        self.Conf_TempComp_Value = None
        

        self.Calced_CC_Eff = None
        self.Calced_Load_Current = None
        self.Calced_Load_Power = None
        self.Calced_TimeTo_Batt50 = None
        self.Calced_Batt_50Capacity = None
        self.Calced_Batt_FreezeEstimate = None
        self.Calced_Batt_FreezeEstimate_DegF = None

        #Accumulated Values
        self.Absorb_Time_Count = None
        self.Float_Time_Count = None
        

        #Peaks and other captured events
        self.Peak_Input_Watts = "0"
        self.Peak_Output_Watts = "0"
        self.Peak_Output_Voltage = "0"
        self.Peak_Output_Current = "0"
        self.Peak_CC_Temperature = "0"
        self.Peak_CC_Temperature_DegF = "0"

        self.Max_Batt_Temperature = "-999"
        self.Min_Batt_Temperature = "999"
        self.Max_Batt_Temperature_DegF = "-999"
        self.Min_Batt_Temperature_DegF = "999"
        self.Max_Batt_Voltage = "0"
        self.Min_Batt_Voltage = "999"
        
        self.Event_Absorb_Reached = "No"
        self.Event_TimeIn_Absorb = "0"
        self.Event_Float_Reached = "No"
        self.Event_TimeIn_Float = "0"


    #------------------------------------------------------------------------------------------------------------------------------
    def connect (self, UI=None, local_verbose_vode=None):

        #Annunciate
        if self.verbose_mode or local_verbose_mode:
            print("Attempting connection to "+self.name+" at "+self.ip_addr+":"+self.port+"......")

        #Transfer connection data to Image area
        self.conn_state = 10        #0 = not connected, 1 = connected, 10 = attempting connection
        if UI and Valid_Dependancy:
            CC_To_UI_Exchange(self, UI)
        
        #Set TCP_Mod_Client params
        self.TCP_Mod_Client.host(self.ip_addr)
        self.TCP_Mod_Client.port(self.port)
        self.TCP_Mod_Client.timeout(self.tcp_timeout)

        #Connect and return state
        #Also Update UI object on the fly, if class is being used in CCDM (allows stand alone us of this class)

        #If connection is not open, try to connect------
        if not self.TCP_Mod_Client.is_open():
            if self.TCP_Mod_Client.open():
                if self.verbose_mode or local_verbose_mode:
                    print("   -> Connected")
                self.conn_state = 1
                #Update UI
                if UI and Valid_Dependancy:
                    CC_To_UI_Exchange(self, UI)
                return self.conn_state
                
            else:
                if self.verbose_mode or local_verbose_mode:
                    print("   -> TCP-Modbus client could not connect to server")
                #blank all internal data associated with read    
                self.blank_cc_image()
                self.conn_state = 0
                #Update UI
                if UI and Valid_Dependancy:
                    CC_To_UI_Exchange(self, UI)
                return self.conn_state

        #If connection is already open, annunciate---------
        elif self.TCP_Mod_Client.is_open():
            if self.verbose_mode or local_verbose_mode:
                print("   -> Connected")
            self.conn_state = 1
            #Update UI
            if UI and Valid_Dependancy:
                CC_To_UI_Exchange(self, UI)
            return self.conn_state
             
    #------------------------------------------------------------------------------------------------------------------------------
    def disconnect (self, local_verbose_vode=None):
        if self.verbose_mode or local_verbose_mode:
            print("Disconnecting from "+self.name)
            self.TCP_Mod_Client.close()
            reset_conn_state()

    #------------------------------------------------------------------------------------------------------------------------------
    def reset_conn_state():

        self.conn_state = 0
        return self.conn_state
    
    #------------------------------------------------------------------------------------------------------------------------------
    def read_data (self, local_verbose_mode=None):
        if self.verbose_mode or local_verbose_mode:
            print("Gathering data from "+self.name)


            #Begin reading and storing data based on configured Controller OEM and Type
            
            #------------------------------ Midnite Solar, Clssic Type Charge Controller -----------------------------------
            if self.oem_series == "Midnite - Classic":
                #NOTE: Reg address and actual address are offset by 1 (EXAMPLE: to access Reg4101 you must read at address value 4100)
                
                #Holding Reg4101-4103 = PCB Rev(MSB) / Unit Type (LSB), Software Build Year, Software Build Month (MSB) Software Build Day (LSB)  
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4100, 3)
                if incoming_data:
                    self.HW_Rev = str(incoming_data[0] & 0xFF00 >> 8)
                    self.Unit_Type = "Classic "+str(incoming_data[0] & 0x00FF)
                    self.FW_Rev = str(incoming_data[2] >> 8).zfill(2)+"/"+str((incoming_data[2] & 0x00FF))+"/"+str(incoming_data[1]) #Assembled to M/D/Year (Build level will be added below)
                                
                #Holding Reg4106-4108 = MAC Address
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4105, 3)
                if incoming_data:
                    MAC1 = (str(hex((incoming_data[2] & 0xFF00)>>8)))
                    MAC1 = MAC1[2:].zfill(2)
                    MAC2 = (str(hex((incoming_data[2] & 0x00FF))))
                    MAC2 = MAC2[2:].zfill(2)
                    MAC3 = (str(hex((incoming_data[1] & 0xFF00)>>8)))
                    MAC3 = MAC3[2:].zfill(2)
                    MAC4 = (str(hex((incoming_data[1] & 0x00FF))))
                    MAC4 = MAC4[2:].zfill(2)
                    MAC5 = (str(hex((incoming_data[0] & 0xFF00)>>8)))
                    MAC5 = MAC5[2:].zfill(2)
                    MAC6 = (str(hex((incoming_data[0] & 0x00FF))))
                    MAC6 = MAC6[2:].zfill(2)
                    #Concat the above results
                    self.MAC_addr = MAC1.upper()+":"+MAC2.upper()+":"+MAC3.upper()+":"+MAC4.upper()+":"+MAC5.upper()+":"+MAC6.upper()  #.upper() method used to convert all letters to uppercase
                else:
                        print("   -> Error Reading Reg4106-4108 block of "+self.name)
   
                #Holding Reg4115-4119 = Battery Voltage, CC Input Voltage, Battery Current, KWh, Output Power
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4114, 5)
                if incoming_data:
                    self.Output_Voltage = str(incoming_data[0] / 10)
                    self.Battery_Voltage = self.Output_Voltage
                    self.Input_Voltage = str(incoming_data[1] / 10)
                    self.Output_Current = str(incoming_data[2] / 10)
                    self.KWh = str(incoming_data[3] / 10)
                    self.Output_Watts = str(incoming_data[4])                                                                     
                else:
                        print("   -> Error Reading Reg4115-4119 block of "+self.name)

                #Holding Reg4120-4123 = Charge Stage, Input Current, VoC Last Measured, HighestV Input Log
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4119, 4)
                if incoming_data:
                    self.Charge_Stage = str((incoming_data[0] & 0xFF00) >> 8)
                    #Develop actual charge stage message based upon value
                    if self.Charge_Stage:
                        self.Charge_Stage_Message = self.set_chargestage_msg(self.Charge_Stage)
                    self.Input_Current = str(incoming_data[1] / 10)
                    
                    self.Last_VoC_Measured = str(incoming_data[2] / 10)
                    self.Highest_InputV_Logged = str(incoming_data[3])
                else:
                        print("   -> Error Reading Reg4120-4123 block of "+self.name)

                #Holding Reg4125-4129 = Charge Amp Hours, Lifetime KWh (2 bytes), Lifetime Ahr (2 bytes)
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4124, 5)
                if incoming_data:
                    self.Ahr = str(incoming_data[0])  
                    self.KWh_Lifetime = str(incoming_data[1] + (incoming_data[2] << 16))
                    self.Ahr_Lifetime = str(incoming_data[3] + (incoming_data[4] <<16))
                else:
                        print("   -> Error Reading Reg4125-4129 block of "+self.name)
                        
                #Holding Reg4130-4134 = Info Data Flags (2 bytes), Battery Temperature, FET Temperature, PCB Temperature
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4129, 5)
                if incoming_data:
                    self.InfoData_FlagsBin = str('{0:032b}'.format( int(incoming_data[0] + (int(incoming_data[1]) << 16 ))))
                    self.InfoData_Flags = str(hex(int(incoming_data[0] + (int(incoming_data[1]) << 16)))).translate(str.maketrans("abcdef", "ABCDEF"))
                    #Gather Various Temperatures, sign and also store F values from C
                    self.Battery_Temperature = str(float(int_to_signed(incoming_data[2]) / 10))
                    self.Battery_Temperature_DegF = str(DegC_to_DegF(float(self.Battery_Temperature)))
                    self.FET_Temperature = str(incoming_data[3] / 10)
                    self.PCB_Temperature = str(incoming_data[4] / 10)
                    self.FET_Temperature_DegF = str(DegC_to_DegF(float(self.FET_Temperature)))
                    self.PCB_Temperature_DegF = str(DegC_to_DegF(float(self.PCB_Temperature)))
                    
                else:
                        print("   -> Error Reading Reg4130-4134 block of "+self.name)

                #Holding Reg4138-4139 = Time spent in Float, Time spent in Absorb
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4137, 2)
                if incoming_data:
                            self.Float_Time_Count = str(incoming_data[0] / 3600) #Convert from seconds to hours
                            self.Absorb_Time_Count = str(incoming_data[1] / 3600) #Convert from seconds to hours
                else:
                        print("   -> Error Reading Reg4138-4139 block of "+self.name)

                #Holding Reg4149-4151 = Absorb Voltage SP, Float Voltage SP, EQ Voltage SP
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4148, 3)
                if incoming_data:
                    self.Conf_Absorb_Setpoint = str(incoming_data[0] / 10)
                    self.Conf_Float_Setpoint = str(incoming_data[1] / 10) 
                    self.Conf_EQ_Setpoint = str(incoming_data[2] / 10)
                else:
                        print("   -> Error Reading Reg4149-4151 block of "+self.name)

                #Holding Reg4154-4157 = Absorb Time, Max Temp Compensation , Min Temp Compensation, Temperature Compensation Value
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4153, 4)
                if incoming_data:
                    self.Conf_Absorb_Time = str(incoming_data[0] / 3600) #Convert from seconds to hours
                    self.Conf_MaxTemp_Comp = str(incoming_data[1] / 10) 
                    self.Conf_MinTemp_Comp = str(incoming_data[2] / 10)
                    self.Conf_TempComp_Value = str(incoming_data[3] / 10)
                else:
                        print("   -> Error Reading Reg4154-4157 block of "+self.name)
                        
                #Holding Reg4162-4165 = EQ Time, EQ Interval, MPPT Mode, Aux12 Function
                #(Check for Shunt (WhizBangJr))
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4161, 4)
                if incoming_data:
                    self.Conf_EQ_Time = str(incoming_data[0] / 3600) #Convert from seconds to hours
                    #->Placeholder for adding EQ Interval
                    self.MPPT_Mode = str(incoming_data[2])
                    #Develop MPPT Mode message based upon value
                    if self.MPPT_Mode != None:
                        self.MPPT_Mode_Message = self.set_mpptmode_msg(self.MPPT_Mode)
                    self.Aux1_Function = incoming_data[3] & 0x003F          #Bits 0-5
                    self.Aux2_Function = (incoming_data[3] & 0x3F00) >> 8     #Bits 8-13
                    if self.Aux2_Function == 18:     #Configured as WhizBangJR read
                        self.Shunt_Installed = True
                    else:
                        self.Shunt_Installed = False
                else:
                            print("   -> Error Reading Reg4162-4165 block of "+self.name)

                #Holding Reg4245-4246 = VbatNominal (12, 24, etc), Ending Amps
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4244, 2)
                if incoming_data:
                    self.Conf_Nominal_Voltage = str(incoming_data[0])
                    self.Conf_End_Amps = str(incoming_data[1] / 10) 
                else:
                        print("   -> Error Reading Reg4245-4246 block of "+self.name)
                

                #NOTE the following are only applicable if Shunt is found (WhizBangJr)
                if self.Shunt_Installed:

                    #Holding Reg4369-4370 = Net Amp Hours
                    incoming_data = self.TCP_Mod_Client.read_holding_registers(4368, 3)
                    if incoming_data:
                        #Assemble and Calculate Net Amp Hours
                        self.Shunt_Net_Ahr = str(float(int_to_signed32((incoming_data[1] << 16) + incoming_data[0])))
                    else:
                            print("   -> Error Reading Reg4368-4369 block of "+self.name)

                    #Holding Reg4371-4373 = WhizBangJR (Shunt) Current, WhizBangJr (Shunt) CRC (MSB) and Temperature (LSB), SoC %
                    incoming_data = self.TCP_Mod_Client.read_holding_registers(4370, 3)
                    if incoming_data:
                        #Convert shunt current to signed value
                        self.Shunt_Current = str(float(int_to_signed(incoming_data[0]) / 10))
                        self.Shunt_Temperature = str(((incoming_data[1] & 0xFF00 >>8) - 50))
                        self.Shunt_Temperature_DegF = str(DegC_to_DegF(float(self.Shunt_Temperature)))
                        self.Battery_SOC = str(incoming_data[2])
                        
                    else:
                            print("   -> Error Reading Reg4370-4373 block of "+self.name)

                    #Holding Reg4377 = Battery remaining Ahrs
                    incoming_data = self.TCP_Mod_Client.read_holding_registers(4376, 1)
                    if incoming_data:
                        self.Battery_Remaining = str(incoming_data[0])
                        
                    else:
                            print("   -> Error Reading Reg4377 of "+self.name)

                    #Holding Reg4381 = Battery Capacity Ahrs
                    incoming_data = self.TCP_Mod_Client.read_holding_registers(4380, 1)
                    if incoming_data:
                        self.Battery_Capacity = str(incoming_data[0])
                        
                    else:
                            print("   -> Error Reading Reg4381 of "+self.name)

                #Holding Reg16385-16390 = Release Version, Net Version, Release Build (2 regs), Net Build (2 regs) 
                incoming_data = self.TCP_Mod_Client.read_holding_registers(16384, 6)
                if incoming_data:
                    self.FW_Build = str(incoming_data[2] + (incoming_data[3] << 16))
                else:
                        print("   -> Error Reading Reg16385-16390 block of "+self.name)
                #Assembled Release Ver and Build, final format will be: Build:m/d/year
                if self.FW_Rev != None and self.FW_Build !=None:
                    self.FW_Rev = self.FW_Build+":"+self.FW_Rev

                    

                #Holding Reg28673-28674 = Serial (2 regs) 
                incoming_data = self.TCP_Mod_Client.read_holding_registers(28672, 2)
                if incoming_data:
                    self.Serial = "CL"+str(incoming_data[1] + (incoming_data[0] << 16))
                else:
                        print("   -> Error Reading Reg28673-28674 block of "+self.name)


            #---------------------------- Tristar,  MPPT 60 Type Charge Controller ---------------------------------------- 
            elif self.oem_series == "Tristar - MPPT 60":
                #Call MPPT Mode method to set mode (static in these controllers)
                self.MPPT_Mode = 0x000B
                self.MPPT_Mode_Message = self.set_mpptmode_msg(0)
                #Set Shunt_Installed false as this option does not exist on Tristar MPPT Charge Controllers
                self.Shunt_Installed = False
                
                #Holding 0x0000-0x0004 = V_PU hi, V_PU lo, I_PU hi, I PU lo, Software Version
                incoming_data = self.TCP_Mod_Client.read_holding_registers(0, 5)
                if incoming_data:
                    #Scaling data for Voltage and Current calcs
                    V_PU_hi = incoming_data[0]
                    V_PU_lo = incoming_data[1]
                    I_PU_hi = incoming_data[2]
                    I_PU_lo = incoming_data[3]
                    self.FW_Rev = str(incoming_data[4])
                else:
                        print("   -> Error Reading 0x0000-0x0004 block of "+self.name)

                #Holding 0x0018-0x001D = Batt. Voltage Filtered, Batt. Term Voltage Filtered, Batt. Sense Voltage Filtered, Array Voltage Filtered, Batt. Current Filtered, Array Current Filtered
                incoming_data = self.TCP_Mod_Client.read_holding_registers(24, 6)
                if incoming_data:
                    self.Output_Voltage = str(self.tristar_scaling(V_PU_hi, V_PU_lo, incoming_data[1]))     #Voltage at CC Output terminals
                    self.Battery_Voltage = str(self.tristar_scaling(V_PU_hi, V_PU_lo, incoming_data[2]))    #Voltage at battery sense inputs
                    self.Input_Voltage = str(self.tristar_scaling(V_PU_hi, V_PU_lo, incoming_data[3]))
                    self.Output_Current = str(self.tristar_scaling(I_PU_hi, I_PU_lo, incoming_data[4]))
                    self.Input_Current = str(self.tristar_scaling(I_PU_hi, I_PU_lo, incoming_data[5]))
                    #Calc Nominal voltage as this is not software stored in Tristar
                    if float(self.Output_Voltage) > 9.0 and float(self.Output_Voltage) < 17.0:
                        self.Conf_Nominal_Voltage = "12"
                    elif float(self.Output_Voltage) > 18.0 and float(self.Output_Voltage) < 34.0:
                        self.Conf_Nominal_Voltage = "24"
                    elif float(self.Output_Voltage) > 36.0 and float(self.Output_Voltage) < 68.0:
                        self.Conf_Nominal_Voltage = "48"
                    else:
                        self.Conf_Nominal_Voltage = "??"
                        
                else:
                        print("   -> Error Reading 0x0018-0x001D block of "+self.name)

                #Holding 0x0023-0x0025 = Heatsink Temperature, RTS Temperature, Battery Temperature
                incoming_data = self.TCP_Mod_Client.read_holding_registers(35, 3)
                if incoming_data:
                    self.PCB_Temperature = str(incoming_data[0])
                    self.PCB_Temperature_DegF = str(DegC_to_DegF(float(self.PCB_Temperature)))
                    self.Battery_Temperature = str(incoming_data[2])
                    self.Battery_Temperature_DegF = str(DegC_to_DegF(float(self.Battery_Temperature)))
                else:
                        print("   -> Error Reading 0x0023-0x0025 block of "+self.name)
                
                #Holding 0x002C-0x002F = Fault Bits, Alarm Bits hi, Alarm Bits lo
                incoming_data = self.TCP_Mod_Client.read_holding_registers(45, 3)
                if incoming_data:
                    self.Fault_FlagsBin = str('{0:016b}'.format(int(incoming_data[0])))
                    self.Alarm_FlagsBin = str('{0:032b}'.format(int(incoming_data[1] << 16) + int(incoming_data[2])))
                else:
                        print("   -> Error Reading 0x002C-0x002F block of "+self.name)

                #Holding 0x0032-0x003A = Charger Stage, Target Reg Voltage, AH Total resetable, NA, AH Total, NA, KWh Total Resetable, KWh Total, Output Power
                incoming_data = self.TCP_Mod_Client.read_holding_registers(50, 9)
                if incoming_data:
                    self.Charge_Stage = str(incoming_data[0])
                    #Develop actual charge stage message based upon value
                    if self.Charge_Stage:
                        self.Charge_Stage_Message = self.set_chargestage_msg(self.Charge_Stage)

                    self.Ahr_Lifetime = str(incoming_data[4])
                    self.KWh_Lifetime = str(incoming_data[7])
                    self.Output_Watts = str(incoming_data[8])
                else:
                        print("   -> Error Reading 0x0032-0x003A block of "+self.name)

                #Holding 0x0043-0x0044 = Daily Ahr Total, Daily KWh Total
                incoming_data = self.TCP_Mod_Client.read_holding_registers(67, 2)
                if incoming_data:
                    self.Ahr = str(incoming_data[0])
                    self.KWh = str(incoming_data[1] / 1000)
                else:
                        print("   -> Error Reading 0x0043-0x0044 block of "+self.name)

                #Holding 0x004D-0x004F = Daily time in Absorb, Daily time in EQ, Daily time in Float
                incoming_data = self.TCP_Mod_Client.read_holding_registers(77, 3)
                if incoming_data:
                    self.Absorb_Time_Count = str(incoming_data[0] / 3600) #Convert from seconds to hours
                    self.Float_Time_Count = str(incoming_data[2] / 3600) #Convert from seconds to hours
                else:
                        print("   -> Error Reading 0x004D-0x004F block of "+self.name)

                #Holding 0x1026-0x1028 = MAC Address
                incoming_data = self.TCP_Mod_Client.read_holding_registers(4134, 3)
                if incoming_data:
                    MAC1 = (str(hex((incoming_data[0] & 0xFF00)>>8)))
                    MAC1 = MAC1[2:].zfill(2)
                    MAC2 = (str(hex((incoming_data[0] & 0x00FF))))
                    MAC2 = MAC2[2:].zfill(2)
                    MAC3 = (str(hex((incoming_data[1] & 0xFF00)>>8)))
                    MAC3 = MAC3[2:].zfill(2)
                    MAC4 = (str(hex((incoming_data[1] & 0x00FF))))
                    MAC4 = MAC4[2:].zfill(2)
                    MAC5 = (str(hex((incoming_data[1] & 0xFF00)>>8)))
                    MAC5 = MAC5[2:].zfill(2)
                    MAC6 = (str(hex((incoming_data[1] & 0x00FF))))
                    MAC6 = MAC6[2:].zfill(2)
                    #Concat the above results
                    self.MAC_addr = MAC1.upper()+":"+MAC2.upper()+":"+MAC3.upper()+":"+MAC4.upper()+":"+MAC5.upper()+":"+MAC6.upper()
                else:
                        print("   -> Error Reading 0x1026-0x1028 block of "+self.name)

                #Holding 0xE000-0xE0C02 = Absorb Setpoint, Float Setpoint, Absorb Time
                incoming_data = self.TCP_Mod_Client.read_holding_registers(57344, 3)
                if incoming_data:
                    self.Conf_Absorb_Setpoint = str(self.tristar_scaling(V_PU_hi, V_PU_lo, incoming_data[0]))
                    self.Conf_Float_Setpoint = str(self.tristar_scaling(V_PU_hi, V_PU_lo, incoming_data[1]))
                    self.Conf_Absorb_Time = str(incoming_data[2] / 3600) #Convert from seconds to hours
                else:
                        print("   -> Error Reading 0xE000-0xE002 block of "+self.name)

                #Holding 0xE007-0xE00A = EQ Setpoint, Days Between EQ, EQ Time Above Vreg, EQ Time at Vreg
                incoming_data = self.TCP_Mod_Client.read_holding_registers(57351, 4)
                if incoming_data:
                    self.Conf_EQ_Setpoint = str(self.tristar_scaling(V_PU_hi, V_PU_lo, incoming_data[0]))
                    self.Conf_EQ_Time = str(incoming_data[3] / 3600) #Convert from seconds to hours
                else:
                        print("   -> Error Reading 0xE007-0xE00A block of "+self.name)

                #Holding 0xE011-0xE012 = Maximum Temperature Comp, Minimum Temperature Comp
                incoming_data = self.TCP_Mod_Client.read_holding_registers(57361, 2)
                if incoming_data:
                    self.Conf_MaxTemp_Comp = str(incoming_data[0])
                    self.Conf_MinTemp_Comp = str(incoming_data[1])
                else:
                        print("   -> Error Reading 0xE011-0xE012 block of "+self.name)

                #Holding 0xE0C0-0xE0C3 = Model, Hardware Version
                incoming_data = self.TCP_Mod_Client.read_holding_registers(57536, 3)
                if incoming_data:
                    self.Serial = str((incoming_data[0] & 0x00FF)) + str(incoming_data[0] >> 8) + str((incoming_data[1] & 0x00FF)) + str(incoming_data[1] >> 8) + str((incoming_data[2] & 0x00FF)) + str(incoming_data[2] >> 8) 
                else:
                        print("   -> Error Reading 0xE0C0-0xE0C3 block of "+self.name)

                #Holding 0xE0CC-0xE0CD = Model, Hardware Version
                incoming_data = self.TCP_Mod_Client.read_holding_registers(57547, 2)
                if incoming_data:
                    self.Unit_Type = str(incoming_data[0])
                    self.HW_Rev = str(incoming_data[1])
                else:
                        print("   -> Error Reading 0xE0CC-0xE0CD block of "+self.name)


            #Invlaid OEM - Type configured -------------------------------------------------            
            else:
                if self.verbose_mode or local_verbose_mode:
                    print("   -> Invalid OEM - Type assigned to "+self.name+", see CCDM_config File")


            #Update date and time stamp each read
            self.dataread_DateTime_stamp = datetime.datetime.now()
            #Perform some calculations to further extract information from data points above
            self.misc_calcs()


            return 0
    #------------------------------------------------------------------------------------------------------------------------------
    def misc_calcs(self):

                #Perform some calculations
                #Input Watts
                if self.Input_Voltage and self.Input_Current:
                    self.Input_Watts = str(round(float(self.Input_Voltage) * float(self.Input_Current),2))
    
                #CC Eff
                if self.Input_Watts and self.Output_Watts and (float(self.Input_Watts) > 0):
                    self.Calced_CC_Eff = round((float(self.Output_Watts) / float(self.Input_Watts))*100,2)
                    if self.Calced_CC_Eff > 100:
                        self.Calced_CC_Eff = str(100)
                    else:
                        self.Calced_CC_Eff = str(self.Calced_CC_Eff)
                else:
                        self.Calced_CC_Eff = str(0)
                    

                #Current to Load (Inverter or other load)
                if self.Output_Current and self.Shunt_Current:
                    self.Calced_Load_Current = str(round(float(self.Output_Current) - float(self.Shunt_Current),2))   

                #Power Consumed by Load (Inverter or other load)
                if self.Output_Voltage and self.Calced_Load_Current:
                    self.Calced_Load_Power = str(round(float(self.Output_Voltage) * float(self.Calced_Load_Current),2))

                #Battery Half Capacity and Estimated time to 50% discharge
                if self.Battery_Capacity and (int(self.Battery_Capacity) > 0):
                    self.Calced_Batt_50Capacity = str((int(self.Battery_Capacity) / 2))

                if self.Battery_Capacity and self.Battery_Remaining and self.Calced_Batt_50Capacity:
                    if (float(self.Battery_Remaining) > float(self.Calced_Batt_50Capacity)) and (float(self.Shunt_Current) != 0):
                        if float(self.Shunt_Current) < 0:
                            self.Calced_TimeTo_Batt50 = str(round((float(self.Battery_Remaining) - float(self.Calced_Batt_50Capacity)) / abs(float(self.Shunt_Current)),2))
                        else:
                            self.Calced_TimeTo_Batt50 = "Infinite"
                    else:
                        self.Calced_TimeTo_Batt50 = str(0)
                #Battery Estimated Freezing Point
                if self.Battery_SOC:
                    self.Calced_Batt_FreezeEstimate = str(linear_scaling(int(self.Battery_SOC), 100, 0, -50, 0)) #Current Battery SOC, Upper SOC%, Lower SOC%, Freeze Point @ Upper SOC%, Freeeze Point @ Lower SOC%
                    self.Calced_Batt_FreezeEstimate_DegF = str(DegC_to_DegF(float(self.Calced_Batt_FreezeEstimate)))

                #Capture peaks and other various process Events ----------------------------------
                #Peak Inputs Watts, daily
                if self.Input_Watts and float(self.Input_Watts) > float(self.Peak_Input_Watts):
                    self.Peak_Input_Watts = self.Input_Watts
                #Peak Output Watts, daily
                if self.Output_Watts and float(self.Output_Watts) > float(self.Peak_Output_Watts):
                    self.Peak_Output_Watts = self.Output_Watts
                #Peak Output Voltage, daily
                if self.Output_Voltage and float(self.Output_Voltage) > float(self.Peak_Output_Voltage):
                    self.Peak_Output_Voltage = self.Output_Voltage
                #Peak Output Current, daily
                if self.Output_Current and float(self.Output_Current) > float(self.Peak_Output_Current):
                    self.Peak_Output_Current = self.Output_Current
                #Peak CC Temperature, daily
                if self.FET_Temperature and float(self.FET_Temperature) > float(self.Peak_CC_Temperature):
                    self.Peak_CC_Temperature = self.FET_Temperature
                    self.Peak_CC_Temperature_DegF = str(DegC_to_DegF(float(self.Peak_CC_Temperature)))

                #Maximum Battery Temperature, daily
                if self.Battery_Temperature and float(self.Battery_Temperature) > float(self.Max_Batt_Temperature):
                    self.Max_Batt_Temperature = self.Battery_Temperature
                    self.Max_Batt_Temperature_DegF = str(DegC_to_DegF(float(self.Max_Batt_Temperature)))
                #Minimum Battery Temperature, daily
                if self.Battery_Temperature and float(self.Battery_Temperature) < float(self.Min_Batt_Temperature):
                    self.Min_Batt_Temperature = self.Battery_Temperature
                    self.Min_Batt_Temperature_DegF = str(DegC_to_DegF(float(self.Min_Batt_Temperature)))
                #Maximum Battery Voltage, daily
                if self.Output_Voltage and float(self.Battery_Voltage) > float(self.Max_Batt_Voltage):
                    self.Max_Batt_Voltage = self.Battery_Voltage
                #Minimum Battery Voltage, daily
                if self.Output_Voltage and float(self.Battery_Voltage) < float(self.Min_Batt_Voltage):
                    self.Min_Batt_Voltage = self.Battery_Voltage

                #Absorb Reached Event
                if self.Charge_Stage_Message[0:6] == "Absorb":
                    self.Event_Absorb_Reached = "Yes"
                #Time in Absorb
                if self.oem_series == "Midnite - Classic":
                    if self.Absorb_Time_Count != None and (float(self.Absorb_Time_Count) > 0) and (float(self.Absorb_Time_Count) < float(self.Conf_Absorb_Time)) and self.Conf_Absorb_Time != None:
                        self.Event_TimeIn_Absorb = str(round((float(self.Conf_Absorb_Time) -  float(self.Absorb_Time_Count)), 2))
                elif self.oem_series == "Tristar - MPPT 60":
                    if self.Absorb_Time_Count != None:
                        self.Event_TimeIn_Absorb = str(round(float(self.Absorb_Time_Count), 2))

                #Float Reached Event
                if self.Charge_Stage_Message[0:5] == "Float":
                    self.Event_Float_Reached = "Yes"
                #Time in Float
                if self.oem_series == "Midnite - Classic":
                    if self.Float_Time_Count != None:
                        self.Event_TimeIn_Float = str(round(float(self.Float_Time_Count), 2))
                elif self.oem_series == "Tristar - MPPT 60":
                    if self.Float_Time_Count != None:
                        self.Event_TimeIn_Float = str(round(float(self.Float_Time_Count), 2))
                      
                #Just before midnite, reset all peaks and captured events
                if (self.dataread_DateTime_stamp.hour == 23) and (self.dataread_DateTime_stamp.minute == 59):
                    self.Peak_Input_Watts = "0"
                    self.Peak_Output_Watts = "0"
                    self.Peak_Output_Voltage = "0"
                    self.Peak_Output_Current = "0"
                    self.Peak_CC_Temperature = "0"

                    self.Max_Batt_Temperature = "0"
                    self.Min_Batt_Temperature = "999"

                    self.Max_Batt_Voltage = "0"
                    self.Min_Batt_Voltage = "999"
                    
                    self.Event_Absorb_Reached = "No"
                    self.Event_TimeIn_Absorb = "0"
                    self.Event_Float_Reached = "No"
                    self.Event_TimeIn_Float = "0"
                   

    #------------------------------------------------------------------------------------------------------------------------------
    def tristar_scaling(self, hi, lo, value_to_scale):
        #Scaling for Voltahe and Current as per Morningstar document
        scaler = hi + (lo / 65535)
        scaled_value = (value_to_scale * scaler) / 32768
        return scaled_value
                    
    #------------------------------------------------------------------------------------------------------------------------------
    def name(self):
        return self.name

    #------------------------------------------------------------------------------------------------------------------------------
    def blank_cc_image(self):
        #reset all data back to None (or zero where applicable)
        self.MAC_addr = None
        self.Date_Time = None
        self.FW_Rev = None
        self.Unit_Type = None
        self.HW_Rev = None
        self.FET_Temperature = None
        self.PCB_Temperature = None
        self.Charge_Stage = None
        self.Charge_Stage_Message = None
        self.Last_VoC_Measured = None
        self.Highest_InputV_Logged = None
        self.InfoData_Flags = None
        self.InfoData_FlagsBin = None
        self.KWh_Lifetime = None
        self.Ahr_Lifetime = None
        self.MPPT_Mode = None
        self.MPPT_Mode_Message = None
        self.Aux1_Function = None
        self.Aux2_Function = None
     
        self.Input_Voltage = None
        self.Input_Current = None
        self.Input_Watts = None
        self.Input_Peak_Watts = "0"
        self.Output_Voltage = None
        self.Output_Current = None
        self.Output_Watts = None
        self.KWh = None
        self.Ahr = None
                
        self.Shunt_Installed = None
        self.Shunt_Temperature = None
        self.Shunt_Current = None

        self.Battery_SOC = None
        self.Battery_Temperature = None
        self.Battery_Remaining = None
        self.Battery_Capacity = None

        self.Conf_Nominal_Voltage = None
        self.Conf_Absorb_Setpoint = None
        self.Conf_Absorb_Time = None
        self.Conf_End_Amps = None
        self.Conf_Float_Setpoint = None
        self.Conf_EQ_Setpoint = None
        self.Conf_EQ_Time = None
        self.Conf_MaxTemp_Comp = None
        self.Conf_MinTemp_Comp = None
        self.Conf_TempComp_Value = None
        

        self.Calced_CC_Eff = None
        self.Calced_Load_Current = None
        self.Calced_Load_Power = None
        self.Calced_TimeTo_Batt50 = "0"
        self.Calced_Batt_50Capactiy = "0"
        self.Calced_Batt_FreezeEstimate = "0"
    #------------------------------------------------------------------------------------------------------------------------------

    def set_chargestage_msg(self, charge_stage_value):

        icharge_stage_value = int(charge_stage_value)
        charge_stage_message = None
        
        if self.oem_series == "Midnite - Classic":
            #Develop message based on value
            if icharge_stage_value == 0:
                charge_stage_message = "Resting ("+charge_stage_value+")"
            elif icharge_stage_value == 3:
                charge_stage_message = "Absorb ("+charge_stage_value+")"
            elif icharge_stage_value == 4:
                charge_stage_message = "Bulk MPPT ("+charge_stage_value+")"
            elif icharge_stage_value == 5:
                charge_stage_message = "Float ("+charge_stage_value+")"
            elif icharge_stage_value == 6:
                charge_stage_message = "Float MPPT ("+charge_stage_value+")"
            elif icharge_stage_value == 7:
                charge_stage_message = "Equalize ("+charge_stage_value+")"
            elif icharge_stage_value == 10:
                charge_stage_message = "Hyper Voc ("+charge_stage_value+")"
            elif icharge_stage_value == 18:
                charge_stage_message = "Equalize MPPT ("+charge_stage_value+")"
            else:
                charge_stage_message = "Unknown state (Value given: "+charge_stage_value+")"

        elif self.oem_series == "Tristar - MPPT 60":
            #Develop message based on value
            if icharge_stage_value == 0:
                charge_stage_message = "Start ("+charge_stage_value+")"
            elif icharge_stage_value == 1:
                charge_stage_message = "Night Check ("+charge_stage_value+")"
            elif icharge_stage_value == 2:
                charge_stage_message = "Disconnect ("+charge_stage_value+")"
            elif icharge_stage_value == 3:
                charge_stage_message = "Night ("+charge_stage_value+")"
            elif icharge_stage_value == 4:
                charge_stage_message = "Fault ("+charge_stage_value+")"
            elif icharge_stage_value == 5:
                charge_stage_message = "Bulk MPPT ("+charge_stage_value+")"
            elif icharge_stage_value == 6:
                charge_stage_message = "Absorb ("+charge_stage_value+")"
            elif icharge_stage_value == 7:
                charge_stage_message = "Float ("+charge_stage_value+")"
            elif icharge_stage_value == 8:
                charge_stage_message = "Equalize ("+charge_stage_value+")"
            elif icharge_stage_value == 9:
                charge_stage_message = "Slave ("+charge_stage_value+")"
            else:
                charge_stage_message = "Unknown state (Value given: "+charge_stage_value+")"

        return charge_stage_message
        
    #------------------------------------------------------------------------------------------------------------------------------

    def set_mpptmode_msg(self, mppt_mode_value):

        imppt_mode_value = int(mppt_mode_value)
        mppt_mode_message = None
        
        if self.oem_series == "Midnite - Classic":
            #Develop message based on value
            if imppt_mode_value == 1:
                mppt_mode_message = "PV_Uset ("+mppt_mode_value+")"
            elif imppt_mode_value == 3:
                mppt_mode_message = "Dynamic ("+mppt_mode_value+")"
            elif imppt_mode_value == 5:
                mppt_mode_message = "Wind Track ("+mppt_mode_value+")"
            elif imppt_mode_value == 7:
                mppt_mode_message = "RESERVED ("+mppt_mode_value+")"
            elif imppt_mode_value == 9:
                mppt_mode_message = "Legacy P&O ("+mppt_mode_value+")"
            elif imppt_mode_value == 11:
                mppt_mode_message = "Solar ("+mppt_mode_value+")"
            elif imppt_mode_value == 13:
                mppt_mode_message = "Hydro ("+mppt_mode_value+")"
            elif imppt_mode_value == 15:
                mppt_mode_message = "RESERVED ("+mppt_mode_value+")"
            else:
                mppt_mode_message = "Unknown ("+mppt_mode_value+")"

        elif self.oem_series == "Tristar - MPPT 60":
        #There is no MPPT Mode settings for Tristar, it is fixed solar input type
            mppt_mode_message = "Solar"
            
        return mppt_mode_message




        
        
        
        
        
