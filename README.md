# sleep_analysis

### Shiny App
* https://karolcichewicz.shinyapps.io/shinyr-dam/
* git - https://github.com/KarolCichewicz/ShinyR-DAM/


## Locomotor activity
1. Put the settings exactly like in Main_settings.png
2. Run and make sure numbers match Locomotor_activity_mean.png
3. Use Monitor9.xlsx to see how we got it
4. Should be 29 alive flies, 3 dead flies, and a mean of 10190.11


## Sleep_analysis_settings
1. Make sure settings match Sleep_analysis_settings.png


## Psuedo-code for initial upload and statistics
* Read in the monitor file and give the following column names when read in file or create dataframe:
* Index,Date,Time,LD-DD,Status,Extras,Monitor_Number,Tube_Number,Data_Type,Unused,Light_Sensor,data_1,data_2,data_3,data_4,data_5,data_6,data_7,data_8,data_9,data_10,data_11,data_12,data_13,data_14,data_15,data_16,data_17,data_18,data_19,data_20,data_21,data_22,data_23,data_24,data_25,data_26,data_27,data_28,data_29,data_30,data_31,data_32
* Set variables - LD_start = 06:00, counts_per_day_alive = 100, LD_DD_anlysis = 'LD', start_date = 2/24/2024, end_date = 2/27/2024
* Create column called LD_DD with LD_start + 18:00 = LD else DD
Filter on date between start_date & end_date
Filter on LD_DD based on LD_DD_analysis
Create column called date_LD_DD based on concat of date + LD_DD
Group by date_LD_DD and sum each column of data_1 - data_32
Loop through data_1 .. data_32 and determine the alive flies & dead flies - any fly with less than counts_per_day_alive is removed from the analysis - remove from the dataframe and keep number_of_dead_flies
Calculate number of alive flies, number of dead flies, Mean, SD, SEM - stats only on alive flies
Make sure the output is the same as the shiny app


## Excel logic
* read in file - 7352 rows
* filter by date - 24-27 - now have 5760 rows
* filter by time and then call everything before 6:00 DD, everything between 6:00 - 18:00 LD, 18-24 is DD
* filter where LD_DD = LD --> 2880 rows
* make sure the Monitor_Number column is correct - might be adding support for multiple monitor files together
