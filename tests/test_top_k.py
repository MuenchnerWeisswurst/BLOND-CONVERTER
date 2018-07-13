import numpy as np
import pandas as pd
from os.path import join
import os 
from pylab import rcParams
import matplotlib.pyplot as plt
rcParams['figure.figsize'] = (14, 6)

plt.style.use('ggplot')
import nilmtk
from nilmtk import DataSet, TimeFrame, MeterGroup, HDFDataStore
from nilmtk.disaggregate import CombinatorialOptimisation, fhmm_exact, hart_85, maximum_likelihood_estimation
from nilmtk.utils import print_dict
from nilmtk.metrics import f1_score

import warnings
warnings.filterwarnings("ignore")
import json

# disaggregation results will be written in the build/ folder
if not os.path.exists("./build/"):
    os.makedirs("./build/")


#FHMM with output file
def fhmm(start_train, end_train, start_test, end_test, train_elec):

    #Start training
    data.set_window(start_train, end_train)
    elec = data.buildings[1].elec
    fhmm = fhmm_exact.FHMM()
    fhmm.train(train_elec, sample_period=1)
    
    #Start disaggregating
    data.set_window(start_test, end_test)
    disag_filename = './build/disagg_sum_fhmm_{}_k.h5'.format(len(train_elec.meters))
    output = HDFDataStore(disag_filename, 'w')
    fhmm.disaggregate(elec.mains(), output)
    output.close()
    dates_dict={
        "start_train":start_train,
        "end_train":end_train,
        "start_test":start_test,
        "end_test":end_test
    }
    # write test and train timeframe into json file
    with open(disag_filename +".json",'w') as dates_file:
        json.dump(dates_dict,dates_file)

    disag = DataSet(disag_filename)
    disag_elec = disag.buildings[1].elec
    disag_elec.plot()
    plt.title("FHMM")  
    plt.show()  

    #Calculate F1-Score
    f1 = f1_score(disag_elec, train_elec)
    f1.index = disag_elec.get_labels(f1.index)
    f1.plot(kind='barh')
    plt.ylabel('appliance')
    plt.xlabel('f-score')
    plt.title("FHMM")
    plt.show()

#MLE with output file
"""
    NOTE: Does not work properly; Only the appliance kettle with the nilmtk fix; without fix raises exception 
"""
def mle(start_train, end_train, start_test, end_test,train_elec):

    # #Start training
    data.set_window(start_train, end_train)
    elec = data.buildings[1].elec
    mle = maximum_likelihood_estimation.MLE()
    mle.sample_period = "1s"
    mle.train(train_elec)

    #Start disaggregating
    data.set_window(start_test, end_test)
    disag_filename = './build/disagg_sum_mle_{}_k.h5'.format(len(train_elec.meters))
    output = HDFDataStore(disag_filename, 'w')
    mle.disaggregate(elec.mains(), output)
    output.close()
    dates_dict={
        "start_train":start_train,
        "end_train":end_train,
        "start_test":start_test,
        "end_test":end_test
    }
    # write test and train timeframe into json file
    with open(disag_filename +".json",'w') as dates_file:
        json.dump(dates_dict,dates_file)

    disag = DataSet(disag_filename)
    disag_elec = disag.buildings[1].elec
    disag_elec.plot()
    plt.show()
    plt.title("FHMM")    

    #Calculate F1-Score
    f1 = f1_score(disag_elec, train_elec)
    f1.index = disag_elec.get_labels(f1.index)
    f1.plot(kind='barh')
    plt.ylabel('appliance')
    plt.xlabel('f-score')
    plt.title("FHMM")
    plt.show()  
    
#CO with output file
def co(start_train, end_train, start_test, end_test,train_elec):

    #Start training
    data.set_window(start_train, end_train)
    elec = data.buildings[1].elec
    co = CombinatorialOptimisation()
    co.train(train_elec, ac_type = 'active' , physical_quantity='power',sample_period=1)

    #Start disaggregating
    data.set_window(start_test, end_test)
    disag_filename = './build/disagg_sum_co_{}_k.h5'.format(len(train_elec.meters))
    output = HDFDataStore(disag_filename, 'w')
    co.disaggregate(elec.mains(), output, ac_type = 'active' , physical_quantity='power',sample_period=1)
    output.close()
    dates_dict={
        "start_train":start_train,
        "end_train":end_train,
        "start_test":start_test,
        "end_test":end_test
    }
    # write test and train timeframe into json file
    with open(disag_filename +".json",'w') as dates_file:
        json.dump(dates_dict,dates_file)

    #Calulate F1-Score
    disag = DataSet(disag_filename)
    disag_elec = disag.buildings[1].elec
    disag_elec.plot()
    plt.title("CO")
    plt.show()    

    f1 = f1_score(disag_elec, train_elec)
    f1.index = disag_elec.get_labels(f1.index)
    f1.plot(kind='barh')
    plt.ylabel('appliance')
    plt.xlabel('f-score')
    plt.title("CO")
    plt.show()

#hart85 with output file
"""
    NOTE: Does not work properly; Appliances are set to unkown
"""
def hart85(start_train, end_train, start_test, end_test,train_elec):

    #Start training
    data.set_window(start_train, end_train)
    elec = data.buildings[1].elec
    hart = hart_85.Hart85()
    hart.train(train_elec, sample_period=1)

    #Start disaggregating
    data.set_window(start_test, end_test)
    disag_filename = './build/disagg_sum_hart85_{}_k.h5'.format(len(train_elec.meters))
    output = HDFDataStore(disag_filename, 'w')
    hart.disaggregate(elec.mains(), output)
    output.close()

    disag = DataSet(disag_filename)
    disag_elec = disag.buildings[1].elec
    disag_elec.plot()
    plt.show()
    plt.title("HART85")    

    #Calculate F1-Score
    f1 = f1_score(disag_elec, train_elec)
    f1.index = disag_elec.get_labels(f1.index)
    f1.plot(kind='barh')
    plt.ylabel('appliance')
    plt.xlabel('f-score')
    plt.title("Hart85")
    plt.show()


def plot_top_k(elecs):
    for elec in elecs.meters:
        elec.plot()
        # set original name as title
        name =  elec.appliances[0].metadata['original_name']
        print "@ {}".format(name)
        plt.title(name)
        plt.show()
        plt.clf()

#set time frames
start_train = "2017-05-17"
end_train = "2017-05-21"
start_test = "2017-06-17"
end_test = "2017-06-19"

data = DataSet("../data/converted_sum.hdf5")
elec = data.buildings[1].elec
# get the topk appliances
topk = elec.submeters().select_top_k(k=5)
plot_top_k(topk)


#Call function
fhmm(start_train, end_train, start_test, end_test,topk)
co(start_train, end_train, start_test, end_test,topk)