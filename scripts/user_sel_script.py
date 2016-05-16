# coding: utf-8

import datetime
from heapq import nlargest
from operator import itemgetter
from collections import defaultdict


def run_split():
    print('Preparing arrays...')
    f = open("../data/train.csv", "r")
    f.readline()
    best_hotels_od_ulc = defaultdict(lambda: defaultdict(int))
    hits = defaultdict(int)
    tp = defaultdict(float)

    total = 0
    # Calc counts
    while 1:
        line = f.readline().strip()
        total += 1
        if total % 10000000 == 0:
            print('Read {} lines...'.format(total))
        if line == '':
            break
        arr = line.split(",")
        user_location_city = arr[5]
        orig_destination_distance = arr[6]
        user_id = int(arr[7])
        hotel_cluster = arr[23]

        
        #populate the data leak dictionary
        if user_location_city != '' and orig_destination_distance != '':
            best_hotels_od_ulc[(user_location_city, orig_destination_distance)][hotel_cluster] += 1

        
    f.close()
    ###########################
    print('Splitting...')
    f = open("../data/train.csv", "r")
    
    
    now = datetime.datetime.now()
    path_match    = 'train_match_' + str(now.strftime("%Y-%m-%d-%H-%M")) + '.csv'
    path_nomatch = 'train_nomatch_' + str(now.strftime("%Y-%m-%d-%H-%M")) + '.csv'

    out_match = open(path_match, "w")
    out_nomatch = open(path_nomatch, "w")
    
    f.readline()
    total = 0
    totalv = 0
    #out.write("id,hotel_cluster\n")
   
    while 1:
        line = f.readline().strip()
        total += 1
        if total % 10000000 == 0:
            print('Write {} lines...'.format(total))

        if line == '':
            break

        arr = line.split(",")
        user_location_city = arr[5]
        orig_destination_distance = arr[6]
            
        s1 = (user_location_city, orig_destination_distance)
        if s1 in best_hotels_od_ulc:
            out_match.write(line)
            out_match.write("\n")
            
        else:
            out_nomatch.write(line)
            out_nomatch.write("\n")                

    out_match.close()
    out_nomatch.close()

    print('Completed!')

run_split()
