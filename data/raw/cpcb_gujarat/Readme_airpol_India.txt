This readme.txt file was generated on 2021-01-13 by Disha Sharma


GENERAL INFORMATION
1. Data generated for the research paper titled "Air Quality in India: Analysis of Surface Air Pollutant Measurements from 2015-2019"


2. Author Information
	A. First Author Contact Information
		Name: Dr. Disha Sharma
		Institution: Princeton University and Peking University
		Email: dishas@princeton.edu

	B. Corresponding Author Contact Information
		Name: Prof. Denise L. Mauzerall
		Institution: Princeton University
		Email: mauzerall@princeton.edu

DATA & FILE OVERVIEW
The dataset is a compilation of open source data on key criteria pollutants PM10, PM2.5, SO2, NO2 and O3, between 2015-2019. The data is originally available at the Central Pollution Control Board (CPCB)  website - https://app.cpcbccr.com/ccr/. 

1. Folder information and file variables: 
- Dataset for each individual species is stored in respective folders in .csv files (e.g., pm25_ccr). Each .csv files provides information on all other criteria pollutants but is best used for the pollutant used in the filename. This is a filtered format where stations that do not include data on a particular pollutant have been excluded.  

- Each folder contains data for every individual monitoring station in a given state. The file name follows the state_city_stationname.csv format for most of the files (e.g., Karnataka_Bangalore_Peenya.csv file contains data for station Peenya, in city of Bangalore, in the state of Karnataka). (For Delhi, as the state and city name are the same, the file format followed is city_stationname.csv).

- Variables included in .csv files:
1. From Date - To Date* = interval of archived data
2. Air pollutant species name = PM10, PM25, SO2, NO2, O3
3. State, City, Station = Descriptive spatial location information of a monitor with state name, city name and station location. 
4. Lat, Lon = latitude and longitude information (additionally added to the open source dataset using Google Maps). 


DATA PROCESSING
The data requires datetime and numerical formatting. Depending on the usage, the datafiles can be appended for different species, time periods and locations. Detailed information on data processing is provided in the methodology section of the publication. 

These data were analyzed using PYTHON. 

