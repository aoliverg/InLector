#    bildocbook2epub
#    Copyright (C) 2021  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ebooklib import epub
import sys
from lxml import etree
import argparse

parser = argparse.ArgumentParser(description='InLéctor script for creating epubs from docbooks')
parser.add_argument('-i', action="store", dest="fentrada", help='The input docbook file.',required=True)
parser.add_argument('-o', action="store", dest="fsortida", help='The output epub file.',required=True)
parser.add_argument('--id', action="store", dest="ebookid", help='The id for the created ebook.',required=False)
parser.add_argument('--toc', action="store_true", dest="includetoc", help='Include Table of Contents.',required=False)

args = parser.parse_args()

fentrada=args.fentrada
fsortida=args.fsortida
ebookid=args.ebookid
includetoc=args.includetoc



tree = etree.parse(fentrada)

book = epub.EpubBook()

lang=tree.getroot().attrib['lang']
print("SL LANG:",lang)
booktitle=tree.xpath('/book/title')[0].text
print("BOOK TITLE:",booktitle)
author_firstname=tree.xpath('/book/bookinfo/author/firstname')[0].text
author_surname=tree.xpath('/book/bookinfo/author/surname')[0].text
author=author_firstname+" "+author_surname
print("AUTHOR:",author)

book = epub.EpubBook()
if ebookid==None:
    ebookid="InLector"
book.set_identifier(ebookid)
book.set_title(booktitle)
book.set_language(lang)
book.add_author(author)

parts=tree.xpath('/book/part')

booktoc=[]
book.spine.append('nav')
contlink=0
traduccions=[]

# define CSS style
style = 'BODY {color: white;}'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
style = '.link {color: #000; cursor: inherit; line-height: 1.2; text-decoration: none }'
link_css=epub.EpubItem(uid="style_nav", file_name="style/stylesheet.css", media_type="text/css", content=style)
# add CSS file
book.add_item(nav_css)
book.add_item(link_css)


events = ("start", "end")
context = etree.iterparse(fentrada, events=events)
slfilecont=0
tlfilecont=0
content=[]
id=""
linkend=""
relations={}
c0 = epub.EpubHtml(file_name="book.html", lang=lang)
for action, elem in context:
    if action=="start" and elem.tag=="title" and "id" in elem.attrib:
        title=elem.text
        titleid=elem.attrib['id']
        
        content.append('<h1>'+title+"</h1>")
    elif (action=="end" and elem.tag=="part") or (action=="end" and elem.tag=="chapter"):
        
        if titleid.startswith("st-"):
            fn="slfile-"+str(slfilecont)+".html"
            slfilecont+=1
        elif titleid.startswith("tt-"):
            fn="tlfile-"+str(tlfilecont)+".html"
            tlfilecont+=1
        print(action,elem.tag,"TITLE",title,"FN",fn)
        c = epub.EpubHtml(title=title, file_name=fn, lang=lang)
        c.content="\n".join(content)
        c.add_item(link_css)
        book.add_item(c)
        
        booktoc.append(epub.Link(fn, title, ''))
        book.spine.append(c)
        content=[]

        #if titleid.startswith("st-"):
        #    slfilecont+=1
        #elif titleid.startswith("tt-"):
        #    tlfilecont+=1
        
    elif action=="start" and elem.tag=="para":
        content.append("<p>")
        
    elif action=="end" and elem.tag=="para":
        content.append("</p>")
        
    elif action=="start" and elem.tag=="phrase":
        id=elem.attrib['id']
        
    elif action=="end" and elem.tag=="phrase":
        id=""
        
    elif action=="start" and elem.tag=="link":
        linkend=elem.attrib['linkend']
        #print(id,linkend,elem.text)
        segment=elem.text
        if id.startswith("ss"):
            cadena='<span class="phrase"><a id="'+str(id)+'"/><a class="link" href="tlfile-'+str(slfilecont)+'.html#'+str(linkend)+'">'+str(segment)+'</a></span>'
            content.append(cadena)
        elif id.startswith("ts"):
            cadena='<span class="phrase"><a id='+str(id)+'"/><a class="link" href="slfile-'+str(tlfilecont)+'.html#'+str(linkend)+'">'+str(segment)+'</a></span>'
            content.append(cadena)
    elif action=="end" and elem.tag=="link":
        linkend=""

    
#######################
                
booktoc=tuple(booktoc)
if includetoc:
    book.toc=booktoc
            
# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# write to the file
epub.write_epub(fsortida, book, {})
