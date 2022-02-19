#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''
This script scrapes all the individual event results listed
on Olympedia, producing a dataframe that has a single row
for each competitor (team, double or athlete) that ever
contented in a medal discipline in the history of the Summer
Olympics.
'''


# In[2]:


from bs4 import BeautifulSoup
import glob
import json
import os
import pandas as pd
from pprint import pprint
import requests
import time
from tqdm.notebook import trange, tqdm


# #### Helpers

# In[3]:


def make_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    return soup


# #### Main functions

# In[4]:


def fetch_games():
    '''
    Fetches URLs for all the editions
    of the Summer Olympics and saves
    them to a JSON file, which consists
    of a list of dictionaries
    '''
    
    url = "https://www.olympedia.org/editions"
    soup = make_soup(url)
    
    summer_games = soup.find_all('table')[0]
    
    data = []
    rows = summer_games.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        
        if len(cols) < 1:
            continue
            
        link = cols[1].find_all('a')
        
        url = link[0]['href']
        year = link[0].text
        
        # Don't want the link for future editions
        if int(year) > 2020:
            break
        
        data.append({"year": year, "url": url})
        
    with open("../output/jsons/editions.json", "w+") as f:
        json.dump(data, f)


# In[5]:


def fetch_medal_disciplines():
    '''
    Iterates through the URLs of each edition of the games
    and fetches urls and descrptions for all the medal
    disciplines that were contested in a given edition.
    '''
    
    base_url = "https://www.olympedia.org/"
    
    with open("../output/jsons/editions.json", "r") as f:
        games = json.load(f)
        
    for game in games:
                
        year = game['year']
        url = f"{base_url}{game['url']}"
        
        # Skip years with no games
        if year in ["1916", "1940", "1944"]:
            continue
        
        data = {}
        data["year"] = year
        data["url"] = game["url"]
        data["disciplines"] = []
        
        fname = f"../output/jsons/disciplines_{year}.json"
        if os.path.isfile(fname):
            print("Skipping")
            continue
        
        
        time.sleep(.1)

        soup =  make_soup(url)
        
        table_title = soup.find_all("h2", string="Medal Disciplines")[0]
        table = table_title.find_next_sibling("table")
        
        links = table.find_all("a")
        
        for link in links:
            discipline = link.text
            discipline_url = link["href"]
            
            data["disciplines"].append({
                    "discipline": discipline,
                    "url": discipline_url
                })
        
        with open(fname, "w+") as f:
            json.dump(data, f)
        
        


# In[6]:


def fetch_events():
    '''
    Iterates through the URLs of each medal discipline
    and fetches urls and descrptions for all the events
    that were contested in a given edition.
    '''
        
    base_url = "https://www.olympedia.org/"
    
    editions = glob.glob("../output/jsons/disciplines_*.json")
    
    for edition in editions:
                
        with open(edition, "r") as f:
            
            edition_data = json.load(f)
            year = edition_data["year"]
            disciplines = edition_data["disciplines"]
            
            for discipline in disciplines:
                                
                url = f"{base_url}{discipline['url']}"
                
                data = {}
                data["year"] = year
                data["discipline"] =  discipline["discipline"]
                data["abbrv"] = discipline["url"][-3:]
                data["url"] = discipline["url"]
                data["events"] = []
        
                print(year, data["abbrv"])
                
                fname = f'../output/jsons/events_{data["abbrv"]}_{year}.json'
                if os.path.isfile(fname):
                    print("Skipping")
                    continue
                
                soup = make_soup(url)
                
                table_title = soup.find_all("h2", string="Events")[0]
                table = table_title.find_next_sibling("table")

                links = table.find_all("a")
                
                for link in links:
                    
                    event = link.text
                    event_url = link["href"]

                    data["events"].append({
                            "event": event,
                            "url": event_url
                        })

                with open(fname, "w+") as f:
                    json.dump(data, f)


# In[7]:


def fetch_results(get_2020=False):
    '''
    Iterate through the results and save the
    position, competitor and medal data for
    each one of them.
    '''
    
    base_url = "https://www.olympedia.org/"
    
    events = glob.glob("../output/jsons/events_*.json")
    
    for event in tqdm(events):
        
        with open(event, "r") as f:
            
            event_data = json.load(f)
            
            year = event_data['year']
            
            if not get_2020:
                if year == "2020":
                    continue
                
            discipline = event_data['discipline']
            abbrv = event_data['abbrv']
            
            results = event_data["events"]
            
            for result in results:
                
                data = {}
                
                data["year"] = year
                data["discipline"] = discipline
                data["abbrv"] = abbrv
                data["event"] = result["event"]
                data["result_url"] = result['url']
                data["result_id"] = result['url'][9:]
                data["competitors"] = []
                
    
                fname = f"../output/jsons/results_{data['result_id']}.json"

                # Avoid rescraping
            
                if os.path.isfile(fname):
                    print("Skipping")
                    continue
        
                result_url = f"{base_url}{result['url']}"
                print(result_url)

                time.sleep(.1)
                soup = make_soup(result_url)
            
                table = soup.find_all("table")[1]
                                
                header = table.find_all('th')
                header = [item.text for item in header]
                
                idx_position = header.index('Pos')
                idx_noc = header.index('NOC')

                rows = table.find_all('tr')
                
                # First row with data
                first_datapoint = rows[1].find_all("td") 
                
                # Discover where is the competitor data
                idx_competitor = 0 # Starts from index zero
                match = False
                for item in first_datapoint: # For each value                                        
                    # Has link?
                    links = item.find_all('a')
                    if links:
                        # Links to athletes?
                        link = links[0]
                        if 'athletes' in link["href"]:
                            # Match!
                            match = True
                            break
                    
                    idx_competitor += 1
                
                # If there is no link to the athletes, get one of the team names 
                if not match:
                    for term in ['Team', 'Competitor(s)', 'Swimmer', 'Boat', 'Fencers',
                                'Fencer', 'Gymnasts', 'Gymnast', 'Rider', 'Riders', 'Cyclist',
                                'Cyclists',]:
                        if term in header:
                            idx_competitor = header.index(term)
                            match = True
                            break
                    
                if not match:
                    raise(ValueError("Could not find competitor row"))
                    
                # Discovers where is the medal data
                idx_medal = 0
                match = False
                for item in first_datapoint:
                    # Has span class gold?
                    gold = item.find_all("span", class_="Gold")
                    if gold:
                        # Match!
                        match = True
                        break
                    
                    idx_medal += 1
                    
                if not match:
                    # If no medal row, revert to positions
                    no_medal = True
                else:
                    no_medal = False
                                
                for row in rows:
                    
                    cols = row.find_all('td')
                    
                    # Skip invalid rows
                    
                    if row.has_attr('class'): # Expandable rows for team members
                        if len(row["class"]) > 0:
                            if row['class'][0] == 'split': 
                                continue

                    if len(cols) < 1: # no content
                        continue
                        
                    if cols[0].text == "": # no position - usually descriptor rows for relay teams
                        continue
                                            
                    position = cols[idx_position].text
                    competitor = cols[idx_competitor].text
                    noc = cols[idx_noc].text
                    
                    if no_medal:
                        if position in ['1', '=1']:
                            medal = 'Gold'
                        elif position in ['2', '=2']:
                            medal = 'Silver'
                        elif position in ['3', '=3']:
                            medal = 'Bronze'
                        else:
                            medal = ''
                            
                    else:
                        medal = cols[idx_medal].text


                    data["competitors"].append({
                        "position": position,
                        "competitor": competitor,
                        "noc": noc,
                        "medal": medal,
                    })
                        
                with open(fname, "w+") as f:
                    json.dump(data, f, indent=2)


# In[8]:


def main():
    fetch_games()
    fetch_medal_disciplines()
    fetch_events()
    fetch_results(get_2020=True)


# In[9]:


if __name__ == "__main__":
    main()


# In[ ]:




