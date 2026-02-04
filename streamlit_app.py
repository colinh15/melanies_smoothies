# Import python packages
# ALL import statements must go at the top
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!
  """
)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)

# Convert the Snowpark Dataframe into a Pandas Dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

name_on_order = st.text_input("What is the name for the order?")

ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections = 5)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on_val = my_dataframe.filter(col('FRUIT_NAME') == fruit_chosen).select(col('SEARCH_ON'))
        # Display smoothiefruit nutrition information
        st.subheader (fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on_val)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    

    insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")


