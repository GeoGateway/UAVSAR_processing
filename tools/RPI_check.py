"""
RPI_check.py
    -- check RPI product
"""
import os
import requests
from bs4 import BeautifulSoup
import geopandas as gpd
import wget

def download_list():
    """download RPI product list"""

    reqs = requests.get("https://uavsar.asf.alaska.edu/")
    soup = BeautifulSoup(reqs.text,"html.parser")

    pr_list = []
    for link in soup.find_all('a'):
        pr = link['href']
        pr = pr[3:-1]
        if len(pr) > 40:
            #print(pr)
            pr_list.append(pr)
    return pr_list

def load_current(geojsonfile):
    """ load current """

    data = gpd.read_file(geojsonfile)
    data['foldername']=data['Dataname'].str.replace("HH","").str.replace("VV","")
    
    return data['foldername'].tolist()

def find_new(alist,clist):
    """ find new product """
    nlist = []
    for entry in alist:
        if entry in clist:
            continue
        else:
            nlist.append(entry)
    
    return nlist

def download_ann(nlist):
    """ download ann from nlist"""

    baseURL = "https://uavsar.asf.alaska.edu/"
    # sample: ylwstn_26903_11059-001_14110-003_1089d_s01_L090_01
    for entry in nlist:
        reqs = requests.get(baseURL + "UA_" + entry)
        soup = BeautifulSoup(reqs.text,"html.parser")
        ann = [x['href'] for x in soup.find_all('a') if x['href'][-4:]==".ann"]  
        if len(ann) == 0:
            print("!ann not found:", entry)  
            continue
        # download ann file
        if not os.path.exists('ann/'+ ann[0]):
            annurl = baseURL + "UA_" + entry + "/" + ann[0]
            print('downloading: ',ann[0])
            wget.download(annurl,"ann")
        else:
            print("downloaded ...",ann[0])


def main():
    """main code"""

    # load ASF
    rpi_list = download_list()
    print("Total RPI: ", len(rpi_list))

    # load current list
    cur_geojson = '1538.geojson'
    cur_list = load_current(cur_geojson)
    print("Current Total: ", len(cur_list))
    new_list = find_new(rpi_list, cur_list)
    print("New datasets: ", len(new_list))
    download_ann(new_list)

if __name__ == "__main__":
    main()