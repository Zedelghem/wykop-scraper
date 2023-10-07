import streamlit as st
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
import requests


@st.cache_data
def convert_df_to_csv(df):
   return df.to_csv(index=False).encode('utf-8')

def scrapeuser(userName):
    url = "https://wykop.pl/ludzie/{}".format(userName)
    page = requests.get(url)
    soup = BeautifulSoup(page.content , 'html.parser')
    info = {}

    # Scraping Profile Info

    #full Name
    info['name'] = soup.find(class_ = 'username').get_text()
    #image
    info['image_url'] =  soup.find(class_ = 'avatar').findChildren("img", recursive=True)[0]['src']
    info['DateJoined'] = soup.find(class_= 'date').get_text()
    info["followers"] = soup.find(class_="from-pagination-links-entries-stream-profile").select("li:nth-child(4)")[0].a.get_text().split()[-1]

    last_actions = soup.find_all('section', class_='entry')
    actions_all = []
    
    for action in last_actions:
        new_action = {}

        new_action["header"] = action.article.header.get_text()

        try:
            new_action["content"] = action.article.findChildren(class_="content")[0].get_text()
        except:
            new_action["content"] = ""

        try:
            new_action["comments"] = action.article.findChildren(class_="comments")[0].a.get_text()
        except:
            new_action["comments"] = 0



        # new_action["digs"] = action.findChildren(class_="vote-box")[0].div.p.get_text()
        actions_all.append(new_action)
        
    return info, pd.DataFrame(actions_all)

st.title("Scraping Wykop.pl")
st.write("Wpisz nazwę uzytkownika, aby pobrac informacje na jego temat.")

user = st.text_input('Nazwa uzytkownika')

if user != '':
    try:
        info, actions = scrapeuser(user)

        csv = convert_df_to_csv(actions)

        st.download_button(
        "Ściągnij pobrane dane o akcjach uzytkownika",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv'
        )

        for key , value in info.items():
            if key != 'image_url':
                st.subheader(
                    '''
                    {} : {} 
                    '''.format(key, value)
                )
            else:
                st.image(value)
        
        st.write("Ostatnie akcje")
        st.table(actions)



    except Exception as error:
        st.subheader("User doesn't exist")
        st.write(error)