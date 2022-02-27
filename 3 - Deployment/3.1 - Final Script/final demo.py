# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 16:42:06 2021

@author: henri
"""

import pandas as pd
import pickle
from geopy.distance import geodesic

amenities = pd.read_csv("data/amenities_df.csv")

latitude = 53.347209
longitude= -6.271167
new_house = 0
second_hand_house = 1
VAT = 0


def predict_price(latitude,longitude,new_house,second_hand_house,VAT):
    #Create new dataframe.
    df = pd.DataFrame(columns = ['Luas_quantity', 'Bus_quantity','Train_quantity','PS_quantity','SS_quantity','Garda_quantity','Latitude','Longitude','New_Dwelling_House_Apartment','Second_Hand_Dwelling_House_Apartment','VAT_Exclusive'])


    #Set the counter variables.
    luas = 0
    bus = 0
    train = 0
    PS = 0
    SS = 0
    garda = 0
    
    #Loop through the blts dataset.
    for label1, row1 in amenities.iterrows():
        #Calculate the distance from the property to the current blts row.
        distance_in_km = geodesic((latitude,longitude),(row1['Latitude'],row1['Longitude'])).km
        #Set if statements to add to counter if certain type and smaller or equal to 1km.
        if distance_in_km <= 1 and row1['Type'] == "Bus Stop":
            bus += 1
        
        elif distance_in_km <= 1 and row1['Type'] == "Luas Stop":
            luas += 1
            
            
        elif distance_in_km <= 1 and row1['Type'] == "Train Stop":
            train += 1
            
        elif distance_in_km <= 1 and row1['Type'] == "Primary School":
            PS += 1
            
        elif distance_in_km <= 1 and row1['Type'] == "Secondary School":
            SS += 1
        
        elif distance_in_km <= 1 and row1['Type'] == "Garda Station":
            garda += 1
            
            
    #Append in the end to our dataframe.
    df = df.append({'Luas_quantity': luas,'Bus_quantity':bus, 'Train_quantity':train, 'PS_quantity':PS,'SS_quantity':SS, 'Garda_quantity':garda,
                    'VAT_Exclusive':VAT,
                    'Latitude':latitude, 'Longitude': longitude,
                   'New_Dwelling_House_Apartment': new_house, 'Second_Hand_Dwelling_House_Apartment':second_hand_house}, ignore_index = True)
    
    #Loading the model.
    filename = 'model/random_forest_model.sav'
    random_forest_loaded_model = pickle.load(open(filename, 'rb'))
    
    #Predicting the value.
    prediction = random_forest_loaded_model.predict(df)
    
    #Return value of the prediction.
    return prediction[0]


house_prediction = predict_price(latitude,longitude,new_house,second_hand_house,VAT)



import folium

map_pickup = folium.Map( location=[53.347409, -6.272184])

folium.Marker(location=[latitude, longitude], popup="Price: € " + str(house_prediction)  ).add_to(map_pickup)

map_pickup

map_pickup.save('final_map_test.html')