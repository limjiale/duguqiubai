import csv

def rate(can, stall, rating, userid):
    #can = input("Canteen Number: ")
    #food = input("Food type: ")
    #rating = input("Rating: ")
    #userid = input("userid: ")

    with open('reviews.csv') as f:
        reader = csv.reader(f)
        data_as_list = list(reader)

    with open('stalls.csv') as f:
        reader = csv.reader(f)
        data_as = list(reader)
    
    i,counter = 0,0
    plist = []
    check = 1

    for i in range(0, len(data_as_list)):
        if ((data_as_list[i][0] == can) & (data_as_list[i][2] == stall) & (data_as_list[i][4] == userid)):
            check = 0
    for i in range(0, len(data_as)):
        if ((data_as[i][0] == can) & (data_as[i][2] == stall)):
            food = data_as[i][1]

    if (check):
        with open('reviews.csv','a', newline='') as f:
            writer = csv.writer(f)
            row = [[can] + [food] + [stall] + [rating] + [userid]]
            writer.writerows(row)
            return("Thank you, your rating has been recorded!")
    else:
        return("You have already entered rating for this stall. Multiple ratings are not allowed!")
            
