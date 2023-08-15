import streamlit as st
import pandas as pd
import numpy as np 
import pydeck as pdk
import plotly.express as px

st.title("Motor Vehicles Collision in NYC")
st.subheader("")
st.subheader('A project by Arturo Frisina')
st.markdown("This project was created for educational purposes. Is a streamlit interactive dashboard that can be used to analyze data gathered from a very large and public dataset.")
st.subheader("")
st.subheader('About the dataset')
st.markdown('The Motor Vehicle Collisions crash table contains details on the crash event. Each row represents a crash event. The Motor Vehicle Collisions data tables contain information from all police reported motor vehicle collisions in NYC. The police report (MV104-AN) is required to be filled out for collisions where someone is injured or killed, or where there is at least $1000 worth of damage.')
st.markdown('The dataset contains data gathered from **January 7, 2012** to the last update: **August 12, 2023**. For over 2 million rows and 29 columns.')
st.markdown('The full dataset is available [Here](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)')

st.divider()

dataPath = ('data.csv')

@st.cache_data
def loadData(nrows):
	data = pd.read_csv(dataPath, parse_dates={'dateTime' : ['CRASH.DATE', 'CRASH.TIME']}, nrows = nrows)
	data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace = True)
	data = data[data['LATITUDE'] != 0]
	#data.sort_values(by='dateTime', ascending=False, inplace = True)
	#data.rename(columns={'CRASH_DATE_CRASH_TIME':'dateTime'}, inplace = True)
	return data

nrows = 100000
data = loadData(nrows)




st.subheader('Raw data (first '+ str(nrows) +  '  rows)')
st.markdown('Original dataset has two date column, "CRASH_DATE" and "CRASH_TIME", that I parsed in a single one named "dateTime". Then I remove all the rows with NAN in this column that has just been created.  ')

code = '''data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace = True)'''
st.code(code, language='python')

with st.expander("Show raw data"):
	st.write(data)

st.divider()

injuredPersons = data['NUMBER.OF.PERSONS.INJURED']
maxInjuredPersons = injuredPersons.max()

code = '''injuredPersons = data['NUMBER OF PERSONS INJURED']
maxInjuredPersons = injuredPersons.max()'''

st.header('Where are most people injured in NYC?')
st.markdown("Let's find out the maxinum number of injured persons in a single crash event")
st.code(code, language='python')
st.markdown("The number of injured persons in a single crash event ranges from 0 to " + str(maxInjuredPersons))
st.markdown('Below, you can choose how many collisions there are in a specific hour and filter the data based on the number of people injured. ')
st.header("")

col1, col2, col3, col4 = st.columns([1,0.5, 3, 1])

with col1:
	hour = st.selectbox("Hour to look at", range(0,24))
	check = st.checkbox("All day", True)	
with col3:
	injuredPeople = st.slider("Minimum number of persons injured", 0, maxInjuredPersons, value= 0)

	
if (check == False):
	data = data[data["dateTime"].dt.hour == hour]
	st.subheader("Collisions between %i:00 and %i:00" % (hour, hour + 1))
else :
	data = data
	st.subheader("Collisions during all day")	

filtered = data[data['NUMBER.OF.PERSONS.INJURED'] >= injuredPeople]
st.map(filtered[["LATITUDE","LONGITUDE"]])

with st.expander("Show filtered data"):
	st.write(filtered)

st.divider()

#midpoint = (np.average(filtered["LATITUDE"]), np.average(filtered["LONGITUDE"]) )
#st.pydeck_chart(pdk.Deck(
#	map_style = "mapbox://styles//mapbox/light-v9 ",
#	initial_view_state = pdk.ViewState(
#		latitude = midpoint[0],
#		longitude = midpoint[1],
#		zoom = 11,
#		pitch = 50
#	),	
#))

if (check == False):	
	st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, hour + 1))

	filtered = filtered[(filtered["dateTime"].dt.hour >= hour) & (filtered["dateTime"].dt.hour < hour + 1)]

	hist = np.histogram(filtered["dateTime"].dt.minute, bins=60, range=(0,60) )[0]

	chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
	fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute','crashes'], height=400)
	st.write(fig)
	st.divider()



# make a dropdown search
st.header("Top 5 dangerous streets affected by types")
select = st.selectbox("Affected by type of people", ['Pedestrians', 'Cyclists', 'Motorists'])

with st.container():
	if select == 'Pedestrians':
		st.dataframe(filtered[filtered["NUMBER.OF.PEDESTRIANS.INJURED"] >= 1][['ON.STREET.NAME', 'NUMBER.OF.PEDESTRIANS.INJURED']].sort_values(by=['NUMBER.OF.PEDESTRIANS.INJURED'], ascending=False).dropna(how='any')[:5], use_container_width = True)
	    #st.write(data.query("NUMBER OF PEDESTRIANS INJURED >= 1")[['ON STREET NAME', 'NUMBER OF PEDESTRIANS INJURED']].sort_values(by=['NUMBER OF PEDESTRIANS INJURED'], ascending=False).dropna(how='any')[:5])
	elif select == 'Cyclists':
		st.dataframe(filtered[filtered["NUMBER.OF.CYCLIST.INJURED"] >= 1][['ON.STREET.NAME', 'NUMBER.OF.CYCLIST.INJURED']].sort_values(by=['NUMBER.OF.CYCLIST.INJURED'], ascending=False).dropna(how='any')[:5], use_container_width = True)
	    #st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', 'injured_cyclists']].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])
	elif select == 'Motorists':
	    st.dataframe(filtered[filtered["NUMBER.OF.MOTORIST.INJURED"] >= 1][['ON.STREET.NAME', 'NUMBER.OF.MOTORIST.INJURED']].sort_values(by=['NUMBER.OF.MOTORIST.INJURED'], ascending=False).dropna(how='any')[:5], use_container_width = True)
	    #st.write(original_data.query("injured_motorists >= 1")[['on_street_name', 'injured_motorists']].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])

