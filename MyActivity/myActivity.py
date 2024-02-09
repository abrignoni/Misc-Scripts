from lxml import html
import csv
import sys
import pathlib

 
args = sys.argv[1:]
file_found = pathlib.Path(args[0])

print(f'Conversion has started for {file_found}')
print(f'Large files will take time to convert')

with open('data.csv', 'w', newline='',encoding='utf8',errors='backslashreplace') as file:
    writer = csv.writer(file)
    
    with open(file_found, "r",encoding='utf-8',) as f:
        data = f.read()
        
    tree = html.fromstring(data)
    for divs in tree.xpath('//div[@class="mdl-grid"]'):
        content = divs.xpath('.//div[@class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1"]//a')
        for atag in content:
            href = atag.attrib['href']
            textcontent = atag.text_content()
        
        content1 = divs.xpath('.//div[@class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1"]//text()')
        timestamp = content1[-1]
        
        
        content2= divs.xpath('.//div[@class="header-cell mdl-cell mdl-cell--12-col"]//p')
        for atag in content2:
            pcontent = atag.text_content()
        
        writer.writerow([timestamp,pcontent,textcontent, href])

print('Conversion process completed. Look for the data.csv file.')