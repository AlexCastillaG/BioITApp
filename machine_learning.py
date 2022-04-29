import pandas as pd
from sklearn.model_selection import train_test_split  # Separar el dataset en entrenamiento y test
from sklearn.metrics import mean_absolute_error  # Mean Absolut Error (MAE) para regresión
from xgboost import XGBRegressor  # Algoritmo de regresión
import map_generator

class DDBB_processor():
    """
        This class process the databases to predict, train and manage the data

        Functions
        ---------

        __init__ ()
            Contructor

        undummify:df
            Convert pd.dummies to dataframe
        df: dummyfied dataframe
        
        csv_reader:
            Allow to read csv
            
        str_to_float:
            Convert all string item dataframe to float
        
        system_training:
            Train the model
        DDBB_Name: Name of the DDBB
        Label: Name of the label to predict
        
        export_to_xls:
            Export dataframe to xls
        output_data: Dataframe to export
        output_name: Name of the xls
        
        manual_check:
            Export prediction result to xls
        DDBB: Input Database
        real_data: Real data of the testing dataset
        predictions: Predicted data
        label_prediction_name: Name label of the predicted data
        
        change_season:
            Change the crop list dependinf of the season
        Season: Season name {Verano, Invierno, Primavera, Otoño}
        
        select_season_product:
            Return crop list depending of the season
        Season: Season name {Verano, Invierno, Primavera, Otoño}
        
        make_all_product_DDBB:
            Process the predicting dataframe
        Year: Year
        Season: Season name {Verano, Invierno, Primavera, Otoño}
            
        all_products_map:
            Represent the data on the general map
        Resolution: Resolution of the map {1,3,5,10}
        Year: Year
        Season: Season name {Verano, Invierno, Primavera, Otoño}
        
        heatmap_DDBB_creator:
            Represent the data on the pixel map
        Year: Year
        Season: Season name {Verano, Invierno, Primavera, Otoño}
        Crop: Crop name to represent
        
        save_train_model:
            Save the model to .json
            
        predict:
            Start the prdicton from dataframe
            
        DDBB_name: Input dataframe to predict

        

    """
    def __init__(self):
        #A continuación se definen todas las columnas de las BBDD
        self.provincias = []
        self.cultivo = []
        self.estacion = []
        self.secano = []
        self.regadio = []
        self.aire_libre = []
        self.invernadero = []
        self.lista_cultivos = ['Avena','Naranja', 'Uva', 'Fresa', 'Lechuga', 'Cebada', 'Maíz',
       'Melocotón', 'Cebolla', 'Pimiento', 'Manzano', 'Tomate',
       'Oliva aceite', 'Coliflor', 'Calabaza', 'Arroz', 'Banano']
        
        self.product_list_summer = ['Manzano', 'Tomate', 'Arroz']
        self.product_list_fall = ['Cebada', 'Coliflor']
        self.product_list_spring = ['Maíz', 'Melocotón', 'Cebolla', 'Pimiento', 'Calabaza']
        self.product_list_winter = ['Avena', 'Naranja', 'Uva', 'Fresa', 'Lechuga', 'Oliva aceite',
       'Banano']
        
        self.map = map_generator.map_generator()#create the map object

    def undummify(self,df, prefix_sep="_"):
        cols2collapse = {
            item.split(prefix_sep)[0]: (prefix_sep in item) for item in df.columns
        }
        series_list = []
        for col, needs_to_collapse in cols2collapse.items():
            if needs_to_collapse:
                undummified = (
                    df.filter(like=col)
                    .idxmax(axis=1)
                    .apply(lambda x: x.split(prefix_sep, maxsplit=1)[1])
                    .rename(col)
                )
                series_list.append(undummified)
            else:
                series_list.append(df[col])
        undummified_df = pd.concat(series_list, axis=1)
        return undummified_df



    def csv_reader(self,DDBB_name):
        index_array = pd.read_excel(DDBB_name)#read the excel
        #extract the columns of the dataframe
        self.provincias = index_array['Provincias'].values  
        self.cultivo = index_array['Cultivo'].values 
        self.estacion = index_array['Estación'].values  
        self.produccion_max = index_array['Produccion_maxima'].values  
        self.etiqueta_tipo = index_array["Etiqueta_max"].values
        self.temperatura = index_array["temperatur"].values
        self.precipitaciones = index_array["precipitac"].values
        self.irradiancia = index_array["radiacion"].values
        

        return self.str_to_float()#return dataframe


    def str_to_float(self):
        
        for item in [self.produccion_max,self.precipitaciones,self.irradiancia,self.temperatura]:#here select the columns to convert
            i=0
            for data in item:        
                item[i] = float(str(data).replace(",","."))#replace , to . to parse
                i=i+1    
        data_dict = {"Provincias":self.provincias,"Cultivo":self.cultivo,"Estacion":self.estacion,"Produccion_maxima":self.produccion_max,"Etiqueta_tipo":self.etiqueta_tipo,"Temperatura":self.temperatura,"Precipitaciones":self.precipitaciones
                     ,"Irradiancia":self.irradiancia}#contruct the dataframe  
        return data_dict

    def system_training(self,DDBB_name,prediction_label):
        DDBB_dict = self.csv_reader(DDBB_name)
        panda_dict = pd.DataFrame(data = DDBB_dict)
        y = panda_dict[prediction_label]  # goal to predict 
        X = panda_dict.drop(labels=[prediction_label,"Etiqueta_tipo"], axis=1)#the rest of the database
        X = pd.get_dummies(X)#using  the one-hot-encoding technique transform the non-numerical variables to numeric
        # Separate the test and training dataset
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=1)
        # Create the model with the parameters to improve the learning      
        self.model = XGBRegressor(base_score=0.5, booster='gbtree', colsample_bylevel=1, colsample_bytree=1, gamma=0,
                                  importance_type='gain', learning_rate=0.3, max_delta_step=0, max_depth=15, min_child_weight=1,
                                  missing=1, n_estimators=50, n_jobs=1, nthread=None, objective='reg:squarederror', random_state=0,
                                  reg_alpha=0, reg_lambda=1, scale_pos_weight=1, seed=None, silent=None, subsample=1) 
               
        self.model.fit(X_train, y_train)  # Train the model
        # Hacemos la predicción sobre el conjunto de test
        predictions = self.model.predict(X_test)
        output = self.manual_check(X_test,y_test,predictions,prediction_label)
        self.export_to_xls(output,"prediction_check.xlsx")
        self.save_train_model()
        # calculation of the precision of the algortyhm (MAE)
        # The lower is the MAE the better is the result
        print("MAE: {:,.0f}".format(mean_absolute_error(predictions, y_test)))

    def export_to_xls(self,output_data,output_name):
        output_data.to_excel(output_name)
        
    def manual_check(self,DDBB,real_data,predictions,label_prediction_name):
        output_data = self.undummify(DDBB)
        output_data[label_prediction_name+" Real Data"] = real_data# add the real data column
        output_data[label_prediction_name+" Predicted Data"] = predictions# add the predicted data column
        return output_data
    
    
    def change_season(self,Estacion):
        if Estacion == "Verano":
            self.lista_cultivos = self.product_list_summer   
        elif Estacion == "Otoño":
            self.lista_cultivos = self.product_list_fall   
        elif Estacion == "Invierno":
            self.lista_cultivos = self.product_list_winter        
        elif Estacion == "Primavera":
            self.lista_cultivos = self.product_list_spring
        elif Estacion == "Default":
            self.lista_cultivos = ['Avena','Naranja', 'Uva', 'Fresa', 'Lechuga', 'Cebada', 'Maíz',
       'Melocotón', 'Cebolla', 'Pimiento', 'Manzano', 'Tomate',
       'Oliva aceite', 'Coliflor', 'Calabaza', 'Arroz', 'Banano']

     
       
        
    def select_season_products(self,Estacion):
        if Estacion == "Verano":
            return self.product_list_summer        
        elif Estacion == "Otoño":
            return self.product_list_fall          
        elif Estacion == "Invierno":
            return self.product_list_winter          
        elif Estacion == "Primavera":
            return self.product_list_spring
        
            
    def make_all_product_DDBB(self,año,Estacion):
        df = pd.read_excel("BBDD_Ambientales/BBDD_corregidas_"+str(año)+"/cuadricula_"+Estacion+"_"+str(año)+".xls")#read the excel
        df["Estación"] = Estacion# set the season
        #rename the columns
        data_info = df.rename(columns={'Nombre': 'Provincias',"precipitac":"Precipitaciones","radiacion":"Irradiancia","temperatur":"Temperatura"})
        data_info_sup = df.rename(columns={'Nombre': 'Provincias',"precipitac":"Precipitaciones","radiacion":"Irradiancia","temperatur":"Temperatura"})
        
        #add the crop to the dataframe and duplicate the values for each crop
        
        data_info["Cultivo"] = self.lista_cultivos[0]
        for item in self.lista_cultivos[1:]:
            data_info_sup["Cultivo"] = item
            data_info = pd.concat([data_info,data_info_sup],ignore_index=True)


        #create 4 more rows to format the dataframe 

        add1 = data_info.iloc[-1]
        add2 = data_info.iloc[-1]
        add3 = data_info.iloc[-1]
        add4 = data_info.iloc[-1]
        
        #each row with a different season so the dataframe has the same length as the training dataset

        add1["Estación"] = "Invierno"
        add2["Estación"] = "Verano"
        add3["Estación"] = "Primavera"
        add4["Estación"] = "Otoño"
        
        data_info = data_info.append([add1,add2,add3,add4], ignore_index = True) #add it to the dataframe

        #divide the dataframe in 2 to predict dataframe and the geo info dataframe
        data = data_info[["Temperatura","Precipitaciones","Irradiancia","Provincias","Cultivo","Estación"]]
        qgis_info = data_info.drop(labels=["Provincias","Estación","Cultivo","Precipitaciones","Irradiancia","Temperatura"], axis=1)
        prediction = self.predict(data)
        prediction_dataframe = pd.DataFrame(prediction,columns=["Prediction"])#add the predicted value to the dataframe
        result = pd.concat([data, qgis_info,prediction_dataframe], axis=1, join="inner") #concat the geo info and the data info
        #self.export_to_xls(result,"prediction_DDBB_"+Estacion+".xlsx") 
        season = self.select_season_products(Estacion)
        final_DDBB = result[result["Cultivo"]==season[0]]    
        for item in season[1:]:#select the product of the season
            final_DDBB = pd.concat([final_DDBB,result[result["Cultivo"]==item]])
        
        return final_DDBB   
    
    def all_products_map(self,resolution,año,Estacion):
        result = self.make_all_product_DDBB(año,Estacion) 
        self.change_season(Estacion)  
        #filter all the product data one by one
        cultivos = result[result["Cultivo"]==self.lista_cultivos[0]]
        maximun = max(cultivos["Prediction"])#obtain the value of the productivity of each product
        normalized_array = cultivos["Prediction"]/maximun#divide all the data by the local maximun

        for item in self.lista_cultivos[1:]:# repeat for each crop            
            cultivos = result[result["Cultivo"]==item]
            maximun = max(cultivos["Prediction"])       
            normalized_array_sup = cultivos["Prediction"]/maximun
            normalized_array = pd.concat([normalized_array,normalized_array_sup],ignore_index=True)#concat all the crop subsets
            
        result = result.assign(Prediction=normalized_array.tolist()) # create a new column with the normalized data
        data_dict = []
        unique_ids = result["id"].unique()#get all unique ids
        

        #create the output database
        for item in unique_ids:#iterate the unique ids
            dict = {"id":"","left":"","top":"","right":"","bottom":"","Producto":[],"Valor":[]}#create the row template and add the values
            dict["id"]=item
            dict["left"] = result[result["id"]==item].iloc[0]["left"]
            dict["top"] = result[result["id"]==item].iloc[0]["top"]
            dict["right"] = result[result["id"]==item].iloc[0]["right"]
            dict["bottom"] = result[result["id"]==item].iloc[0]["bottom"]

            #create a dictionary containing all the values of the normalized prediction
            
            for i in result[result["id"]==item]["Prediction"]:
                dict["Valor"].append(i)
            for i in result[result["id"]==item]["Cultivo"]:
                dict["Producto"].append(i)               
            max_local_value = max(dict["Valor"])#select the maximun value and product between the row with the same ids
            max_index = dict["Valor"].index(max_local_value)#get the index to select the product that correspond to the max prediction value
            dict["Producto"] = dict["Producto"][max_index]#get the product that correspond to the max prediction value
            dict.pop("Valor") #delete the non-normalized value
            
            data_dict.append(dict)

            product_df = pd.DataFrame(data_dict)
        
        self.change_season("Default")
        self.map.icon_marker_map(product_df,resolution)       
        
    def heatmap_DDBB_creator(self,año,Estacion,Cultivo):
        
        result = self.make_all_product_DDBB(año,Estacion)
        filtered_result = result[result.Cultivo==Cultivo]#select the crop to represent
        self.map.heat_map(filtered_result,"Prediction")
        
        
    def save_train_model(self):
        self.model.save_model("model.json")
        
    def predict_model(self,to_predict_DDBB):
        model = XGBRegressor()
        model.load_model("model.json")
        to_predict_DDBB = pd.get_dummies(to_predict_DDBB)
        
        return model.predict(to_predict_DDBB)


 

    
if __name__ == '__main__':
    
    DDBB_processor = DDBB_processor()
    
    DDBB_processor.system_training("BBDD_Produccion/BBDD_Final_2010-18.xls","Produccion_maxima")

    DDBB_processor.heatmap_DDBB_creator(2018,"Verano","Arroz")
    #DDBB_processor.all_products_map(10,2018,"Invierno")

    