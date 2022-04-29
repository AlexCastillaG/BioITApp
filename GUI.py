import PySimpleGUI as sg
import machine_learning


class interface():
    """
        Custom GUI for BioIT APP
              
        Functions
        ---------

        __init__ ()
            Contructor

        start_GUI()
            Start the BioIT GUI


    """
    def __init__ (self):

        
        self.product_list = []  #empty product list
        self.product_list_summer = ["Todos los cultivos",'Manzano', 'Tomate', 'Arroz']  #List of crops planted in summer
        self.product_list_fall = ["Todos los cultivos",'Cebada', 'Coliflor'] #List of crops planted in fall
        self.product_list_spring = ["Todos los cultivos",'Maíz', 'Melocotón', 'Cebolla', 'Pimiento', 'Calabaza']#List of crops planted in spring
        self.product_list_winter = ["Todos los cultivos",'Avena', 'Naranja', 'Uva', 'Fresa', 'Lechuga', 'Oliva aceite',
       'Banano']#List of crops planted in winter
        
        
        self.year_list = [2018,2100]#List of the avalaible years to predict
        
        self.season = ["Invierno","Primavera","Verano","Otoño"] #List of all seasons
    
        self.DDBB_processor = machine_learning.DDBB_processor() #Initializate the DDBB processor object
        
        sg.theme('DarkBrown1')#set the GUI theme
        
        
        self.layout = [  [sg.Image("")],    #Create the layout of the GUI
                    [sg.Text("Elige el año")],
                    [sg.Combo(self.year_list,key="year_list")],
                    [sg.Text("Elige la estación:")],
                    [sg.Combo(self.season,key="season",enable_events=True)],
                    [sg.Text("Elige el cultivo")],
                    [sg.Combo(self.product_list,key="product_list",enable_events=True,size=[50,30])],
                    [sg.Button("Run"),sg.Text("",key="Loading")]
                
                ]

        # Create the Window
        self.window = sg.Window('BioIT App', self.layout,size=[800,200])#Initializate the app windows
        
        

    
    def start_GUI(self):
        
        """
        Start the BioIT GUI
        """

        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read(timeout=100)
            
            
            
            if event == "season": #Select the right crop list depending of the selected season
                if values["season"] == "Verano":
                    self.window["product_list"].update(values=self.product_list_summer) #if season is summer update the crop list
                    self.window.Refresh()
                elif values["season"] == "Invierno":
                    self.window["product_list"].update(values=self.product_list_winter)#if season is winter update the crop list
                    self.window.Refresh()               
                elif values["season"] == "Primavera":
                    self.window["product_list"].update(values=self.product_list_spring)#if season is spring update the crop list
                    self.window.Refresh()               
                elif values["season"] == "Otoño":
                    self.window["product_list"].update(values=self.product_list_fall)#if season is fall update the crop list
                    self.window.Refresh()             
                else:
                    self.window["product_list"].update(values=self.product_list)#if season is blank update the crop list
                    self.window.Refresh() 
            
            
            
            if event == "Run": #when clicking run start the algorythm
                self.window['Loading'].Update("Cargando... Espere por favor... Esto tardará unos minutos... No cierres la app...") #print the message on the GUI
                self.window.Refresh()
                
                if values["product_list"] == "Todos los cultivos": # if the user select all crops print all_product_map
                    self.DDBB_processor.all_products_map(5,values["year_list"],values["season"])
                else: # else print heatmap/pixelmap
                    self.DDBB_processor.heatmap_DDBB_creator(values["year_list"],values["season"],values["product_list"])
                    
                self.window['Loading'].Update("")
                
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel the app closes
                break


        self.window.close()


