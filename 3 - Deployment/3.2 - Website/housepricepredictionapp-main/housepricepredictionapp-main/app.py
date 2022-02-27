from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import pickle
import folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="housepriceapp")
amenities = pd.read_csv("data/amenities_df.csv")
app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'ahsuyafstfatrfshahjhd'


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    
    #Gets the address from the form.
    address = request.form["address"]
    #Gets info from the geolocator API and returns info about the address (latitude and longitude)
    location = geolocator.geocode(address)
    #If the location is not valid, shows a message and returns the user to the main page.
    if location is None:
        flash('Unfortunately we could not find that address. Please enter another one: ')
        return(redirect(url_for('home')))
    #Else get the location latitude and longitude.
    else:
        latitude = float(location.latitude)
        longitude = float(location.longitude)
        #Latitude and longitude needs to be in the right range, if it not redirect the user to the menu again and asks for a Dublin address.
        if latitude > 54 or latitude < 53 or longitude > -6 or longitude < -7:
            flash(
                'We found an address outside of Dublin. Please enter a Dublin address: ')
            return(redirect(url_for('home')))
        #Else it gets the form value for the house type and set the variables.
        else:
            house_type = request.form['house-type']

            if house_type == "new-house":
                new_house = 1
                second_hand_house = 0
                VAT = 1

            else:
                new_house = 0
                second_hand_house = 1
                VAT = 0

            # Create new dataframe.
            df = pd.DataFrame(columns=['Luas_quantity', 'Bus_quantity', 'Train_quantity', 'PS_quantity', 'SS_quantity', 'Garda_quantity',
                                       'Latitude', 'Longitude', 'New_Dwelling_House_Apartment', 'Second_Hand_Dwelling_House_Apartment', 'VAT_Exclusive'])

            # Set the counter variables.
            luas = 0
            bus = 0
            train = 0
            PS = 0
            SS = 0
            garda = 0

            # Loop through the blts dataset.
            for label1, row1 in amenities.iterrows():
                # Calculate the distance from the property to the current blts row.
                distance_in_km = geodesic(
                    (latitude, longitude), (row1['Latitude'], row1['Longitude'])).km
                # Set if statements to add to counter if certain type and smaller or equal to 1km.
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

            # Append in the end to our dataframe.
            df = df.append({'Luas_quantity': luas, 'Bus_quantity': bus, 'Train_quantity': train, 'PS_quantity': PS, 'SS_quantity': SS, 'Garda_quantity': garda,
                            'VAT_Exclusive': VAT,
                            'Latitude': latitude, 'Longitude': longitude,
                            'New_Dwelling_House_Apartment': new_house, 'Second_Hand_Dwelling_House_Apartment': second_hand_house}, ignore_index=True)

            # Loading the model.
            filename = 'model/random_forest_model.sav'
            random_forest_loaded_model = pickle.load(open(filename, 'rb'))

            # Predicting the value.
            prediction = random_forest_loaded_model.predict(df)
            #Creates the map with the center on the entered coordinates (center of Dublin).
            map_pickup = folium.Map(location=[53.347409, -6.272184])
            #Adds a marker with the location coordinates and adds the prediction value to the market.
            folium.Marker(location=[latitude, longitude],
                          popup="Price: € " + str(prediction[0])).add_to(map_pickup)
            #Save the map to the templates folder.
            map_pickup.save('templates/final_map_test.html')
            #Render the map.
            return render_template("final_map_test.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == "__main__":
    # app.run(debug=True)
    app.run()
