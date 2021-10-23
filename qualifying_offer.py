import requests
from lxml import html
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import locale
locale.setlocale(locale.LC_ALL, '')

data_url = 'https://questionnaire-148920.appspot.com/swe/data.html'

#pull the html content from data_url
with requests.get(data_url) as r:
    r.raise_for_status()
    data_raw = r.content

#parse html to find table data (split on /tr)
doc = html.fromstring(data_raw)
elements = doc.xpath('//tr')

players_to_salary = {}

#row by row, collect player name and salary in a dictionary
for row in elements:
    players_to_salary[row[0].text_content()] = row[1].text_content().replace('$','').replace(',','') 

#convert salary data to integer value, only if the data is a non-empty string and is numeric
#this controls for bad data such as '', or 'random string' type cases
players_to_salary = {k: int(v) for k,v in players_to_salary.items() if v and v.isnumeric()}

#read data into a pandas.DataFrame
df = pd.DataFrame([*players_to_salary.items()],columns=['Player','Salary'])

#sort by salary
df.sort_values(by='Salary',ascending=False,inplace=True)
df.reset_index(drop=True,inplace=True)

print(df)

#calculate qualifying offer
qualifying_offer_value = df[:125]['Salary'].mean()

print(f'Qualifying Offer Value: {qualifying_offer_value}')

#generate figure output, containing the qualifying offer and some relevant graphs
fig, axes = plt.subplots(1,2,figsize=(10,5), num='Qualifying Offer Value Based on Top 125 Salaries')
fig.suptitle(f'The monetary value of the qualifying offer is {locale.currency(qualifying_offer_value,grouping=True)}',fontsize=16, fontweight='bold')

convert_to_millions = FuncFormatter(lambda x, pos: f'{x/10**6:,.0f}M')

#salary density plot with qualifying offer value and mean salary
sns.kdeplot(data=df,x='Salary',shade=True,ax=axes[0],color='tab:blue',label='Salary Density Plot')
axes[0].axvline(x=qualifying_offer_value,c='goldenrod',ls='--', label='Qualifying Offer Value')
axes[0].axvline(x=df['Salary'].mean(),c='red',ls='--', label='Mean Salary')
axes[0].xaxis.set_major_formatter(convert_to_millions)
axes[0].set_xlabel('Salary',fontweight='bold')
axes[0].set_ylabel('Density', fontweight='bold')
axes[0].legend(loc='upper right', fontsize='x-small')
axes[0].set_title('MLB Salary Distribution', fontweight='bold')

#bar graph of top 5 mlb salaries
sns.barplot(x=df[:5]['Player'].apply(lambda a: a.split(',')[0]),y=df[:5]['Salary'],ax=axes[1])
axes[1].yaxis.set_major_formatter(convert_to_millions)
axes[1].set_title('Top 5 MLB Salaries', fontweight='bold')
axes[1].set_xlabel('Player',fontweight='bold')
axes[1].set_ylabel('Salary', fontweight='bold')

fig.tight_layout()

plt.show()