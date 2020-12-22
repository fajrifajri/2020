import requests
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import plotly.express as px
import pandas as pd 
from iso3166 import countries

google_trend_url = "https://trends.google.com/trends/yis/2020/"

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome(options=options, executable_path=r'/Users/afajri/Downloads/chromedriver')

filename = "data.csv"
no_data = []
output_data = {}


def get_country_list():
    
    global country_list 

    url = google_trend_url + "GLOBAL/"
    google = requests.get(url)
    #print(google.content)
    re_match = r"var\syisYearPickerPerGeo\s=\s(.*); var yisGeoPickerPerYear"
    country = re.search(re_match,google.text)
    
    #print(country.group(1))
    country_list= json.loads(country.group(1))
    
def get_country_data(country_code):
    #time.sleep(random.randint(60, 120))
    url = google_trend_url + country_code
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # <div bidi="value" dir="ltr"><span ng-bind="bidiText">Pakistan vs England</span></div>
    # <div bidi="value" dir="ltr"><span ng-bind="bidiText">Coronavirus</span></div>
    country_data = soup.find_all('div', bidi='value')
    print(url)
    try:
        print(country_data[0].text)        
        data = country_data[0].text.lower()
        if("orona" in data or "коронавирус" in data or "كورونا" in data or "코로나 바이러스 " in data or "新型コロナウイルス感染症" in data): 
            data = "Coronavirus"
        elif("election" in data or "predsedniške" in data or "美國大選" in data or "美國總統大選" in data):
            data = "US Election 2020"
        country = countries.get(country_code).alpha3
        output_data.setdefault(country, data)
        if country_code in no_data:
            no_data.remove(country_code)
    except IndexError:
        print("no data")
    
        no_data.append(country_code)

def get_all_data():
    for key in country_list:
        if(country_list[key][0]["supported"]==True and country_list[key][0]["id"] == "2020" and key != "GLOBAL"):
            get_country_data(key)
            
    while(no_data):    
        get_country_data(no_data.pop())
        

def gen_file():

    raw_data = open(filename, "w")
    for cc, trend in output_data.items():
        raw_data.write("\n{},{}".format(cc, trend))
    raw_data.close()

def generate_maps():
    df = pd.DataFrame(list(output_data.items()), columns=['Country','Trend'])
    fig = px.choropleth(df, locations="Country", color="Trend",
                    color_continuous_scale=px.colors.diverging.BrBG,
                    color_continuous_midpoint=0,
                    title="Google Trend 2020 ") 
    fig.show()

if __name__ == "__main__":
    get_country_list()
    get_all_data()
    gen_file()
    generate_maps()
