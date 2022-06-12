import streamlit as st
import pandas as pd
import statsmodels.api as sm

# folder for data models
model_folder = "Data/"

# folder for brands and models
brands_models = "Data/Brands_and_models.csv"

# path for variable summaries
variable_summaries_path = 'Data/variable_summaries.csv'

# set up wide screen for streamlit
st.set_page_config(layout="wide", page_title="Car costs", page_icon="🚗")
st.title("Car prices and costs of ownership")

# load the underlying dataset
df = pd.read_csv(brands_models)

# convert countries
dict_countries = {
    "DE":"Germany",
    "ES":"Spain",
    "FR":"France",
    "NL":"Netherlands",
    "BE":"Belgium",
    "IT":"Italy",
    "AT":"Austria",
    "LU":"Luxembourg"
}
def convert_country(abbr):
    return dict_countries[abbr]

col1, col2 = st.columns(2)
brand = col1.selectbox(options = df["brand"].unique(), label = "Select your car brand:")
model = col2.selectbox(options = df[df["brand"] == brand]["model"].sort_values().unique(), label = "Select your car model:")

# parameter input in two columns
with st.form(key = "Specify your car"):
    
    # place_holder_model = col2.empty()
    # if brand:
    #     model = col2.selectbox(options = df[df["brand"] == brand]["model"].sort_values().unique(), label = "Select your car model:")
    col1, col2 = st.columns(2)

    # set standard values by using average values from data frame
    df_variable_summaries = pd.read_csv(variable_summaries_path, index_col = [0,1], header = [0,1])
    # same for the selected car
    df_car_variables = df_variable_summaries.loc[(brand, model)]

    year_registration = col1.slider(label = "Select year of first car registration:", max_value = 2022-int(df_car_variables[("age", "min")])+1, min_value = 2022-int(df_car_variables[("age", "max")])-1, value = 2022-int(df_car_variables[("age", "mean")]))
    mileage = col2.number_input(label = "Select total car mileage (in km)", min_value = 0, max_value = 1000000, step = 2000, value = int((df_car_variables[("mileage", "mean")]/1000).round(0)*1000))

    power = col1.slider(label = "Select power (in hp):", min_value = 20, max_value = 1000, step = 10, value = int(df_car_variables[("power", "mean")]))
    transmission = col2.selectbox(options = ["Automatic", "Manual", "Semi-automatic"], label = "Select the type of transmission:")
    
    fuelcategory = col1.selectbox(options = ["Gasoline", "Diesel"], label = "Select the fuel type:")
    fuelconsumption = col2.slider(label = "Select fuel consumption (in l/100km):", min_value = 1.0, max_value = 40.0, step = 0.2, value = float(round(df_car_variables[("fuelConsumption","mean")],1)))

    country = col1.selectbox(options = dict_countries.keys(), label = "Select your country", format_func = convert_country)
    #annual_mileage = col2.slider(label = "Select annual mileage (in km):", min_value = 100, max_value = 200000, step = 100, value = 10000)
    
    submit_button = st.form_submit_button(label = "Submit")


if submit_button:

    st.write(f"Results for {brand} {model}")

    # modify df to test
    model_file_name_temp = brand.replace(" ","_")+"#"+model.replace(" ","_").replace("/","_or_")

    # load regression model
    regression_model = sm.load(f'{model_folder}{model_file_name_temp}.pickle')

    age = 2022 - year_registration

    # convert user input to prediction input (df)
    user_df = dict(zip(["age", "mileage", "power", "transmissionType", "fuelCategory", "country"],
                        [age, mileage, power, transmission, fuelcategory, country]))

    predicted_price = regression_model.predict(user_df).loc[0]

    st.title(f"The predicted price is {int(predicted_price)}€")
    st.markdown(f"Number of cars in data set: *{int(regression_model.nobs)}*")

    # Calculate costs of ownership
    initial_price = predicted_price

    # with 100 more km
    add_km = 100
    user_df_new_mileage = dict(zip(["age", "mileage", "power", "transmissionType", "fuelCategory", "country"], [age, mileage + add_km, power, transmission, fuelcategory, country]))
    predicted_price_new_mileage = regression_model.predict(user_df_new_mileage).loc[0]
    mileage_diff = round(initial_price - predicted_price_new_mileage,2)

    # with 1 year older
    add_year = 1/12
    user_df_new_age = dict(zip(["age", "mileage", "power", "transmissionType", "fuelCategory", "country"], [age + add_year, mileage, power, transmission, fuelcategory, country]))
    predicted_price_new_age = regression_model.predict(user_df_new_age).loc[0]
    age_diff = round(initial_price - predicted_price_new_age,2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Costs of an additional 100km", f"{mileage_diff}€")
    col2.metric("Costs of an additional one month of age (depreciation)", f"{age_diff}€")



    # # calculate fuel costs
    # # get fuel prices
    # df_fuel = pd.read_html("https://www.cargopedia.net/europe-fuel-prices")[0]
    # df_fuel.columns = df_fuel.columns.droplevel(-1)
    # df_fuel = df_fuel.set_index("Country")
    # df_fuel.columns = ["Gasoline", "Diesel", "LPG"]
    # df_fuel = df_fuel.apply(pd.to_numeric, errors = "coerce")

    # # work with parameters
    # gas_price = df_fuel.loc[dict_countries[country],fuelcategory]
    # gas_costs = round(gas_price * annual_mileage * fuelconsumption / 100,2)

    # # write gasoline output
    # st.write("Here is the fuel consumption per year:")
    # col1, col2, col3 = st.columns(3)
    # col1.metric("Annual costs for gasoline", f"{gas_costs}€")
    # col2.metric("Fuel", fuelcategory)
    # col3.metric("Current fuel price", f"{gas_price}€ per liter")    
