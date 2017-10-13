#function for filtering and sorting stalls based of Canteen or Cuisine

import os
from urllib import parse
import psycopg2

def findstall(option, choice):

    if (option == "Canteen"):
        #Canteen input of each rating is stored in the 1st column(index 0)
        select = 0
        #Cuisine type of each rating is stored in the 2nd column(index 1)
        sel = 1
    elif (option == "Cuisine"):
        #Cuisince tyoe of each rating is stored in the 2nd column(index 1)
        select = 1
        #Canteen input of each rating is stored in the 1st column(index 0)
        sel = 0
    #conn_string = "host='155.69.160.69' dbname='postgres' user='postgres' password='Password1'"
    conn_string = "host='ec2-54-225-237-64.compute-1.amazonaws.com' dbname='d7dkk1sep0usei' user='gdzxodktfaiogm' password='a4ad4ecd6b25911c8eea09b601378a27e0a00210b42a27f9d2b953a69f81f43c'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM store")
    data_as1 = list(cursor.fetchall())
    cursor.execute("SELECT * FROM reviews")
    data_as_list = list(cursor.fetchall())
    data_as = [list(row) for row in data_as1]
    
    counter = 0
    plist = []

    
    for i in range(0, len(data_as_list)):
        #find reviews of stalls matching selected canteen/cuisine
        if (data_as_list[i][select] == choice):
            plist.append(data_as_list[i])
        i = i + 1

    mlist = []

    for i in range(0, len(data_as)):
        #find stalls matching selected canteen/cuisine
        if (data_as[i][select] == choice):
            mlist.append(data_as[i])
        i = i + 1
    

    #compute average ratings of particular store
    for i in range (0,len(mlist)):
        mlist[i][4] = float(mlist[i][4])
        mlist[i][5] = float(mlist[i][5])
        for k in range (0,len(plist)):
            #match each review to stall by checking both location and store name matches
            if ((mlist[i][0] == plist[k][0])&(mlist[i][2] == plist[k][2])):
                #add particular rating to overall rating of stall
                mlist[i][4] = (mlist[i][4]) + float(plist[k][3])
                #increase number of people that rated for the particular stall
                mlist[i][5] = (mlist[i][5]) + 1
        #for stalls that people have rated on, we divide overall rating by number of people to obtain average ratings
        if(mlist[i][5] != 0):
            mlist[i][4] = mlist[i][4] / mlist[i][5]
    #sort the list of stalls by average rating in descending order
    sorted_mlist = sorted(mlist,key=lambda x: x[4],reverse=True)

    #output of function is a string containing list of stalls with info such as stall name, canteen, opening hours, cuisine and average ratings
    outmsg = "List of filtered Stalls (Highest rating to Lowest rating) \n \n" 

    for i in range (0,len(sorted_mlist)):
        outmsg = outmsg + "Stall Name: " + str(sorted_mlist[i][2]) +"\n" + "Location: " + str(sorted_mlist[i][0]) + "\n" + "Opening Hours: " + str(sorted_mlist[i][3])+ "\n" + "Cuisine: " + str(sorted_mlist[i][1]) + "\n" + "Avg Rating: " + str(sorted_mlist[i][4]) + "\n \n"

    return(outmsg)
