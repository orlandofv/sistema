from bs4 import BeautifulSoup
import csv
import pandas


url = "C:\\Users\\MICROSOFT\\Documents\\bootstrap web\\OneTech\\OneTech\\index.html"
html = open(url, encoding='utf-8')
soup = BeautifulSoup(html, parser='lxml')

el = soup.find_all('div')
data = [dt.text for dt in el]
print(data)

for i, df in enumerate(pandas.read_html(url)):
    df.to_csv('myfile_{}.csv'.format(i))
