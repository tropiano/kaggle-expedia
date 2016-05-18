# coding: utf-8
#################################
#      Simple Validation        #
#################################
# contributors:
# ZFTurbo - idea, main part
# Kagglers - tuning, development
# Grzegorz Sionkowski - simple validation



from datetime import datetime
from heapq import nlargest
from operator import itemgetter
from collections import defaultdict

# validation ###############
validate = 1  # 1 - validation, 0 - submission
N0 = 2        # total number of parts
N1 = 1        # number of part
#--------------------------

def run_solution():
    print('Preparing arrays...')

#   f = open("../data/train.csv", "r")
    f = open("train_nomatch_2016-05-17-15-47.csv","r")
    f.readline()
    best_hotels_od_ulc = defaultdict(lambda: defaultdict(int))
    best_hotels_de_da = defaultdict(lambda: defaultdict(int))

    best_hotels_search_dest = defaultdict(lambda: defaultdict(int))
    
    best_hotels_search_dest1 = defaultdict(lambda: defaultdict(int))
    best_hotel_country = defaultdict(lambda: defaultdict(int))
    best_hotel_month = defaultdict(lambda: defaultdict(int))
    
    best_hotel_mo_id = defaultdict(lambda: defaultdict(int))
    best_hotel_pk_id = defaultdict(lambda: defaultdict(int))
    hits = defaultdict(int)
    tp = defaultdict(float)

    popular_hotel_cluster = defaultdict(int)
    total = 0

    # Calc counts
    while 1:
        line = f.readline().strip()
        total += 1
        if total % 100000 == 0:
            print('Read {} lines...'.format(total))
        if line == '' or total==1000000:
            break
        arr = line.split(",")
        book_year = int(arr[0][:4])
        book_month = int(arr[0][5:7])
        user_location_city = arr[5]
        orig_destination_distance = arr[6]
        user_id = int(arr[7])
        is_package = int(arr[9])
        srch_destination_id = arr[16]
        is_booking = int(arr[18])
        hotel_country = arr[21]
        hotel_market = arr[22]
        hotel_cluster = arr[23]

        #calculate number of days (11,12 in train, 12,13 in test)
        ci = arr[11]
        co = arr[12]
        
        if validate == 1 and user_id % N0 == N1:
            continue

        #append_0 = (book_year - 2012)*12 + book_month
        #append_1 = ((book_year - 2012)*12 + book_month) * (1 + 10*is_booking)
        #append_2 = ((book_year - 2012)*12 + book_month) * (1 + 5*is_booking)
        #print orig_destination_distance
        append_0 = (book_year - 2012)*12 + book_month
        #try a weight based on destination distance 
        #append_0 = float(orig_destination_distance)/24901 if orig_destination_distance != '' else 0
        #print append_0
        append_1 = ((book_year - 2012)*12 + book_month) * (1 + 10*is_booking)
        append_2 = ((book_year - 2012)*12 + book_month) * (1 + 5*is_booking)
		
		
        #zeturbo parameters
        append_0 = 1
        append_1 = 3 + 17*is_booking
        append_2 = 1 + 5*is_booking
	
	'''
        if user_location_city != '' and orig_destination_distance != '':
            best_hotels_od_ulc[(user_location_city, orig_destination_distance)][hotel_cluster] += append_0
        '''

        if srch_destination_id != '' and ci != '' and co != '':
            days = (datetime.strptime(co, '%Y-%M-%d') - datetime.strptime(ci, '%Y-%M-%d')).days
            best_hotels_de_da[(srch_destination_id,days)][hotel_cluster] += append_1

        if srch_destination_id != '' and hotel_country != '' and hotel_market != '':
            best_hotels_search_dest[(srch_destination_id, hotel_country, hotel_market,is_package)][hotel_cluster] += append_1

			
        if srch_destination_id != '' and orig_destination_distance != '':
            best_hotels_search_dest1[srch_destination_id][hotel_cluster] += append_0

        if hotel_country != '':
            best_hotel_country[hotel_country][hotel_cluster] += append_2

		#create the best hotel by month dictionary	
        if book_month != '':
            best_hotel_month[book_month][hotel_cluster] += append_2
            
		#create the best hotel by month per destination dict	
        if book_month != '' and srch_destination_id != '':
            best_hotel_mo_id[(book_month,srch_destination_id)][hotel_cluster] += append_2
		
		#create the best hotel by package per destination dict	
        if is_package != '' and srch_destination_id != '':
            best_hotel_pk_id[(is_package,srch_destination_id)][hotel_cluster] += append_2
			
        popular_hotel_cluster[hotel_cluster] += 1

    f.close()
    ###########################
    if validate == 1:
        print('Validation...')
        #f = open("../data/train.csv", "r")
        f = open("train_nomatch_2016-05-17-15-47.csv","r")
    else:
        print('Generate submission...')
        f = open("../data/test.csv", "r")
    now = datetime.now()
    path = 'submission_' + str(now.strftime("%Y-%m-%d-%H-%M")) + '.csv'
    out = open(path, "w")
    f.readline()
    total = 0
    totalv = 0
    out.write("id,hotel_cluster\n")
    topclasters = nlargest(5, sorted(popular_hotel_cluster.items()), key=itemgetter(1))

    while 1:
        line = f.readline().strip()
        total += 1
        if total % 10000000 == 0:
            print('Write {} lines...'.format(total))

        if line == '':
            break

        arr = line.split(",")
        if validate == 1:
            book_year = int(arr[0][:4])
            book_month = int(arr[0][5:7])
            user_location_city = arr[5]
            orig_destination_distance = arr[6]
            user_id = int(arr[7])
            is_package = int(arr[9])
            srch_destination_id = arr[16]
            is_booking = int(arr[18])
            hotel_country = arr[21]
            hotel_market = arr[22]
            hotel_cluster = arr[23]
            ci = arr[11]
            co = arr[12]
            id = 0
            if user_id % N0 != N1:
               continue
            if is_booking == 0:
               continue
        else:
            id = arr[0]
            user_location_city = arr[6]
            orig_destination_distance = arr[7]
            user_id = int(arr[8])
            is_package = int(arr[10])
            srch_destination_id = arr[17]
            hotel_country = arr[20]
            hotel_market = arr[21]
            is_booking = 1

        totalv += 1
        out.write(str(id) + ',')
        filled = []

        s1 = (user_location_city, orig_destination_distance)
        if s1 in best_hotels_od_ulc:
            d = best_hotels_od_ulc[s1]
            topitems = nlargest(5, sorted(d.items()), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1

              
        s2 = (srch_destination_id, hotel_country, hotel_market,is_package)
        if s2 in best_hotels_search_dest:
            d = best_hotels_search_dest[s2]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1

		
        s3 = (book_month, srch_destination_id)
        if s3 in best_hotel_mo_id:
            d = best_hotel_mo_id[s3]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1			  

      
        s4 = (is_package, srch_destination_id)
        if s4 in best_hotel_pk_id:
            d = best_hotel_pk_id[s4]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1
		
        #best hotels by day and search destination         
        s11 = (srch_destination_id, days)
        if s11 in best_hotels_de_da:
            d = best_hotels_de_da[s11]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1
					  
        if srch_destination_id in best_hotels_search_dest1:
            d = best_hotels_search_dest1[srch_destination_id]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1
            
        if book_month in best_hotel_month:
            d = best_hotel_month[book_month]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1
					  
        if hotel_country in best_hotel_country:
            d = best_hotel_country[hotel_country]
            topitems = nlargest(5, d.items(), key=itemgetter(1))
            for i in range(len(topitems)):
                if len(filled) == 5:
                    break
                if topitems[i][0] in filled:
                    continue
                out.write(' ' + topitems[i][0])
                filled.append(topitems[i][0])
                if validate == 1:
                   if topitems[i][0]==hotel_cluster:
                      hits[len(filled)] +=1
					  
        for i in range(len(topclasters)):
            if len(filled) == 5:
                    break
            if topclasters[i][0] in filled:
                continue
            out.write(' ' + topclasters[i][0])
            filled.append(topclasters[i][0])
            if validate == 1:
                if topclasters[i][0]==hotel_cluster:
                    hits[len(filled)] +=1
        
                    
        out.write("\n")
    out.close()
    print('Completed!')
    # validation >>>
    scores = 0.0
    classified = 0
    if validate == 1:
        for jj in range(1,6):
           scores +=  hits[jj]*1.0/jj
           tp[jj] = hits[jj]*100.0/totalv
           classified += hits[jj]
        misclassified = totalv-classified
        miscp = misclassified*100.0/totalv
        print("")
        print(" validation")
        print("----------------------------------------------------------------")
        print("position %8d %8d %8d %8d %8d %8d+" % (1,2,3,4,5,6))
        print("hits     %8d %8d %8d %8d %8d %8d " % (hits[1],hits[2],hits[3],hits[4],hits[5],misclassified))
        print("hits[%%]  %8.2f %8.2f %8.2f %8.2f %8.2f %8.2f " % (tp[1],tp[2],tp[3],tp[4],tp[5],miscp))
        print("----------------------------------------------------------------")
        print("MAP@5 = %8.4f " % (scores*1.0/totalv))
    # <<< validation

run_solution()
