import pandas as pd
import numpy as np
import random
import ml_metrics as metrics
import operator


def make_key(items):
    return "_".join([str(i) for i in items])


def generate_exact_matches(row, match_cols, groups):
    index = tuple([row[t] for t in match_cols])
    try:
        group = groups.get_group(index)
    except Exception:
        return []
    clus = list(set(group.hotel_cluster))
    return clus


def f5(seq, idfun=None): 
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def main():

    
    n = sum(1 for line in open("../data/train.csv")) - 1 #number of records in file (excludes header)
    s = 1000000 #desired sample size
    skip = sorted(random.sample(xrange(1,n+1),n-s))
    #open files
    print "opening files"
    #destinations = pd.read_csv("data/destinations.csv")
    train = pd.read_csv("../data/train.csv",
                        usecols=['srch_destination_id', 'hotel_market','hotel_cluster','user_location_country', 'user_location_region', 'user_location_city',
                                 'hotel_market', 'orig_destination_distance','date_time','user_id','is_booking'],
                        dtype={'srch_destination_id':np.uint32, 'hotel_market':np.uint32, 'hotel_cluster':np.uint32, 'user_location_country':np.uint32, 
                               'user_location_region':np.uint32, 'is_booking':np.bool},skiprows=skip)
    
    '''
    test= pd.read_csv("../data/test.csv",
                      usecols=['srch_destination_id', 'hotel_market','user_location_country', 'user_location_region', 'user_location_city',
                               'hotel_market', 'orig_destination_distance','date_time','user_id'],
                      dtype={'srch_destination_id':np.uint32, 'hotel_market':np.uint32, 'user_location_country':np.uint32,
                             'user_location_region':np.uint32})
    '''
    print "files opened"

    train.date_time =pd.to_datetime(train.date_time)
    train["year"] = train.date_time.dt.year
    train["month"] = train.date_time.dt.month

    #select 10000 userid
    unique_user = train.user_id.unique()
    print "unique users", len(unique_user)

    sel_user_ids = [unique_user[i] for i in sorted(random.sample(range(len(unique_user)),450000))]
    sel_train = train[train.user_id.isin(sel_user_ids)]

    t1 = sel_train[((sel_train.year == 2013) | ((sel_train.year == 2014) & (sel_train.month < 8)))]
    #t1 = sel_train[(sel_train.year == 2014) & (sel_train.month < 8)]                                                                              
    t2 = sel_train[((sel_train.year == 2014) & (sel_train.month >= 8))]
    t2 = t2[t2.is_booking==True]
    
    #t1=train
    #t2=test

    print "shape of t1 (train)", t1.shape
    print "shape of t2 (test)", t2.shape

    most_common_cl = list(train.hotel_cluster.value_counts().head().index)
    
    print "most common cluster prediction made", most_common_cl

    
    #clusters by destination id and type
    #match_cols = ["srch_destination_id", "srch_destination_type_id", "is_package", "hotel_market"]
    match_cols = ["srch_destination_id"]
    cluster_cols = match_cols + ['hotel_cluster']

    groups = t1.groupby(cluster_cols)
    print "number of destination groups: ", len(groups)


    top_clusters = {}
    for name, group in groups:
        clicks = len(group.is_booking[group.is_booking == False])
        bookings = len(group.is_booking[group.is_booking == True])

        score = bookings + .15 * clicks
    
        clus_name = make_key(name[:len(match_cols)])
        
        if clus_name not in top_clusters:
            top_clusters[clus_name] = {}
            top_clusters[clus_name][name[-1]] = score

    cluster_dict = {}
    for n in top_clusters:
        tc = top_clusters[n]
        top = [l[0] for l in sorted(tc.items(), key=operator.itemgetter(1), reverse=True)[:5]]
        cluster_dict[n] = top



    preds = []
    for index, row in t2.iterrows():
        key = make_key([row[m] for m in match_cols])
        if key in cluster_dict:
            preds.append(cluster_dict[key])
        else:
            preds.append([])
    
    print "basic prediction made"

    
    #match_cols = ['user_location_country', 'user_location_region', 'user_location_city', 'hotel_market', 'orig_destination_distance']
    match_cols = ['user_location_city', 'orig_destination_distance']
    
    groups = t1.groupby(match_cols)
    print "number of exact groups: ", len(groups)

    exact_matches = []
    for i in range(t2.shape[0]):
        exact_matches.append(generate_exact_matches(t2.iloc[i], match_cols, groups))
        if i%10000==0: print "read ", i, "element of t2"

    print "exact matches prediction made"

    
    basic_preds = [f5(most_common_cl)[:5] for p in range(len(preds))]
    print "basic", metrics.mapk([[l] for l in t2["hotel_cluster"]], basic_preds, k=5)
    
    region_preds = [f5(preds[p] + most_common_cl)[:5] for p in range(len(preds))]
    print "regional", metrics.mapk([[l] for l in t2["hotel_cluster"]], region_preds, k=5)    
    
    full_preds = [f5(exact_matches[p] + preds[p] + most_common_cl)[:5] for p in range(len(preds))]
    print "full", metrics.mapk([[l] for l in t2["hotel_cluster"]], full_preds, k=5)


    #uncomment to write the file
    '''
    write_p = [" ".join([str(l) for l in p]) for p in preds]
    write_frame = ["{0},{1}".format(t2["id"][i], write_p[i]) for i in range(len(preds))]
    write_frame = ["id,hotel_cluster"] + write_frame
    with open("predictions_v2.csv", "w+") as f:
        f.write("\n".join(write_frame))
    '''

if __name__=="__main__":
    main()
