import pandas as pd
import folium
import webbrowser as wb
import geopandas as gpd
import numpy as np

class map_generator():
    """"
        This class can generate several types of maps

    Functions
    ---------

    __init__:
        Constructor
    coords: Coordinates of the center of the map
    Zoom: Starting zoom map

    reset_map:
        Resets the map to generate another

    heat_map:
        Generates a pixel map
    DDBB_name: Database name
    Var_to_represent: Var that will be represent

    marker_map:
        Generates a map with markers
    DDBB_name: Database name

    product_printer:
        Generates markers with custom icons
    Coords: Array with latitud, longitud, product

    hover_func:
        This function allow to see the data while the mouse is on the pixel
    Dataframe: Geojson dataframe with all the coords and data info

    icon_marker_map:
        Generate an icon map with all products
    DDBB_Name: Database name
    Resolution: Inversely proportional to the number of icons on the map

    set_shapes:
        Generate the shapes of the provinces
    DDBB: Geo DDBB With province shapes

    open_map:
        Save and open the map
    

    """

    def __init__(self,zoom=6,coords=[40.133932434766733, -3.103938729508073]):

        self.zoom = zoom
        self.coords = coords
    
        #create the maps object
        self.spain_map = folium.Map(
            zoom_start=self.zoom,
            location=self.coords)

        #read the provinces map
        self.map_provincias =  pd.read_csv("provincias-espanolas.csv",sep=';',encoding='latin-1')

    def reset_map(self):
        #create a blank map
        self.spain_map = folium.Map(
            zoom_start=self.zoom,
            location=self.coords)        


    
    def heat_map(self,DDBB_name,var_to_represent):
        self.reset_map()
        df = DDBB_name
        crop_name = df["Cultivo"].iloc[0]#get the crop_name
        df[df ["Prediction"]< 0] = 0# if the value is less than 0 set to 0
        df = df[["id", var_to_represent,"Temperatura","Precipitaciones","Irradiancia"]]#select the variables to represent
        state_geo = "mapa_cuadriculas.geojson"
        geoJSON_df = gpd.read_file(state_geo)#load the geojsonfile
        final_df = geoJSON_df.merge(df, on = "id")#merge the data DDBB with the geojson DDBB
        color_scale=['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']#set the color scale to represent
        endpts = list(np.linspace(1, 12, len(color_scale) - 1))

        self.hover_func(final_df)

        folium.Choropleth(#create the pixel map object
        geo_data=final_df,
        data=final_df,
        columns=["id", var_to_represent],#var to represent and id of the grid
        binning_endpoints=endpts, colorscale=color_scale,
        key_on="feature.properties.id",
        fill_color='YlOrRd',#grid color
        fill_opacity=0.8,
        line_opacity=0,
        legend_name=crop_name,
        smooth_factor=0.5,
        Highlight= True,
        line_color = "#0000",
        name = "Prediction",
        highlight=True,
        show=True,
        overlay=True,
        nan_fill_color = "Yellow"
        ).add_to(self.spain_map)


        self.set_shapes(self.map_provincias)
        self.open_map()




    def marker_map(self,DDBB_name):
        self.reset_map()
        df = DDBB_name 
        i=0
        while i < (len(df)):#iterate the items on the DDBB creating a marker on each one
            item = df.iloc[i]    
            longitude = (item["left"]+item["right"])/2 #get the center of the longitude
            latitude = (item["top"]+item["bottom"])/2 #get the center of the latitude
            i=i+5#jump over the items to minimize the resolution
            folium.Marker(
                location=[latitude, longitude],
            ).add_to(self.spain_map)
            
        self.set_shapes(self.map_provincias)     
        self.open_map()
        
        
    def product_printer(self,coords):
        for item in coords:#iter all the array
            longitud = item[0]
            latitud = item[1]
            product = item[2]
            icon = folium.features.CustomIcon('Images/'+product+'.png', icon_size=(20,20))#get the png correspondign to the product
            html = '''{}<br>'''.format(product)
            folium.Marker([latitud, longitud],#create the icon marker object
                                    popup=html,
                                    icon=icon
                                    ).add_to(self.spain_map)    

    def hover_func(self,final_df):

        style_function = lambda x: {'fillColor': '#ffffff', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.1, 
                                    'weight': 0.1}
        highlight_function = lambda x: {'fillColor': '#000000', 
                                        'color':'#000000', 
                                        'fillOpacity': 0.50, 
                                        'weight': 0.1}
        NIL = folium.features.GeoJson(
            data = final_df,
            style_function=style_function, 
            control=False,
            highlight_function=highlight_function, 
            tooltip=folium.features.GeoJsonTooltip(
                fields=["Prediction","Temperatura","Precipitaciones","Irradiancia"],
                aliases=["Predicción (kg/hectárea)","Temperatura (K)","Precipitaciones (mm/h)","Irradiancia (W/m2)"],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
        self.spain_map.add_child(NIL)
        self.spain_map.keep_in_front(NIL)


    def icon_marker_map(self,DDBB_name,resolution=3):
        self.reset_map()
        df = DDBB_name 
        coords = []
        i=0
        while i < (len(df)):#iter the DDBB and get the data
            item = df.iloc[i]    
            product=item["Producto"]
            longitude = (item["left"]+item["right"])/2 
            latitude = (item["top"]+item["bottom"])/2
            coords.append([longitude,latitude,product])
            i=i+resolution
        
        
        self.product_printer(coords)    
        self.set_shapes(self.map_provincias)     
        self.open_map()   

    def set_shapes(self,DDBB):
   
        for item in DDBB.iloc():
            folium.GeoJson(data=item["Geo Shape"]).add_to(self.spain_map)#create the province shapes
            pass
    
    def open_map(self):

        self.spain_map.save('index.html')#save map
        wb.open_new("index.html")#open map
        
if __name__ == '__main__':
    map = map_generator()
    
    df = pd.read_excel("prediction_DDBB_Verano.xlsx")
    
    map.icon_marker_map(df)
    map.open_map()