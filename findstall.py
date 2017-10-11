import csv

def findstall(option, choice):

    if (option == "Canteen"):
        select = 0
        sel = 1
    elif (option == "Cuisine"):
        select = 1
        sel = 0
              
    with open('reviews.csv') as f:
        reader = csv.reader(f)
        data_as_list = list(reader)

    counter = 0
    plist = []

    for i in range(0, len(data_as_list)):
        if (data_as_list[i][select] == choice):
            plist.append([])
            plist[counter]=(data_as_list[i])
            counter = counter + 1
        i = i + 1

    counter = 0
    mlist = []

    with open('stalls.csv') as f:
        reader = csv.reader(f)
        data_as = list(reader)

    for i in range(0, len(data_as)):
        if (data_as[i][select] == choice):
            mlist.append([])
            mlist[counter]=(data_as[i])
            counter = counter + 1
        i = i + 1



    for i in range (0,len(mlist)):
        mlist[i][4] = float(mlist[i][4])
        mlist[i][5] = float(mlist[i][5])
        for k in range (0,len(plist)):
            if ((mlist[i][sel] == plist[k][sel])&(mlist[i][2] == plist[k][2])):
                mlist[i][4] = (mlist[i][4]) + float(plist[k][3])
                mlist[i][5] = (mlist[i][5]) + 1
        if(mlist[i][5] != 0):
            mlist[i][4] = mlist[i][4] / mlist[i][5]

    sorted_mlist = sorted(mlist,key=lambda x: x[4],reverse=True)

    outmsg = "List of filtered Stalls (Highest rating to Lowest rating) \n \n" 

    for i in range (0,len(sorted_mlist)):
        outmsg = outmsg + "Stall Name: " + str(sorted_mlist[i][2]) +"\n" + "Location: " + str(sorted_mlist[i][0]) + "\n" + "Opening Hours: " + str(sorted_mlist[i][3])+ "\n" + "Cuisine: " + str(sorted_mlist[i][1]) + "\n" + "Avg Rating: " + str(sorted_mlist[i][4]) + "\n \n"

    return(outmsg)
