#function that writes user ratings of stores into a file

import os
from urllib import parse
import psycopg2

def rate(can, stall, rating, userid):
    conn_string = "host='ec2-54-225-237-64.compute-1.amazonaws.com' dbname='d7dkk1sep0usei' user='gdzxodktfaiogm' password='a4ad4ecd6b25911c8eea09b601378a27e0a00210b42a27f9d2b953a69f81f43c'"
    #conn_string = "host='155.69.160.69' dbname='postgres' user='postgres' password='Password1'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM store")
    data_as = cursor.fetchall()
    cursor.execute("SELECT * FROM reviews")
    data_as_list = cursor.fetchall()
    plist = []
    check = 1

    #user validation. check that for the selected stall from the selected canteen, the user do not already have a previous rating
    for i in range(0, len(data_as_list)):
        if ((data_as_list[i][0] == can) & (data_as_list[i][2] == stall) & (data_as_list[i][4] == userid)):
            check = 0
            
    #if user passes validation test, we allow ratings to be stored into file
    if (check):
        #find the cuisine type and operating hours of selected stall from selected canteen
        for i in range(0, len(data_as)):
            if ((data_as[i][0] == can) & (data_as[i][2] == stall)):
                cuisine = data_as[i][1]
        #add all relevant data(canteen, cuisine, stall name, operating hours, user rating, user id) into existing file
        row = [can, cuisine, stall, rating, userid]
        cursor.execute("INSERT INTO reviews VALUES(%s, %s, %s, %s, %s)", row)
        conn.commit()

        return("Thank you, your rating has been recorded!")
    #if user validation fail, as user already had a previous rating for selected stall, output of the function is a string informing the user of his error
    else:
        return("You have already entered rating for this stall. Multiple ratings are not allowed!")
            
