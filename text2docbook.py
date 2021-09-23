#    text2docbook
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

import sys
import codecs
import argparse

parser = argparse.ArgumentParser(description='A script to convert a txt file (with special markup) into a docbook file.')
parser.add_argument("-i", "--input_file", type=str, help="The epub input file to convert", required=True)
parser.add_argument("-o", "--output_file", type=str, help="The output bilingual docbook file", required=True)

args = parser.parse_args()

fentrada=args.input_file
fsortida=args.output_file

entrada=codecs.open(fentrada,"r",encoding="utf-8")
sortida=codecs.open(fsortida,"w",encoding="utf-8")

title=""
author_firstname=""
author_surname=""
paras=[]
closetags=[]
for linia in entrada:
    linia=linia.rstrip()
    if linia.startswith("\\title"):
        print("TITLE")
        title=linia.replace("\\title ","")
    elif linia.startswith("\\author_firstname"):
        author_firstname=linia.replace("\\author_firstname ","")
    elif linia.startswith("\\author_lastname"):
        author_surname=linia.replace("\\author_lastname ","")
    elif linia.startswith("\\chapter"):
        if "</chapter>" in closetags:
            paras.append("</chapter>")
            closetags.remove("</chapter>")
        chapter_title=linia.replace("\\chapter ","")
        paras.append("<chapter>")
        closetags.append("</chapter>")
        if len(chapter_title)>0:
            cadena="<title>"+chapter_title+"</title>"
            paras.append(cadena)
    elif linia.startswith("\\part"):
        if "</chapter>" in closetags:
            paras.append("</chapter>")
            closetags.remove("</chapter>")
        if "</part>" in closetags:
            paras.append("</part>")
            closetags.remove("</part>")
        part_title=linia.replace("\\part ","")
        paras.append("<part>")
        closetags.append("</part>")
        if len(part_title)>0:
            cadena="<title>"+part_title+"</title>"
            paras.append(cadena)
    elif not len(linia)==0:
        paras.append(linia.strip())
        

cadena='<book lang="en">'
sortida.write(cadena+"\n")
cadena='<title>'+title+'</title>'
sortida.write(cadena+"\n")
cadena='<bookinfo>'
sortida.write(cadena+"\n")
cadena='<legalnotice>'
sortida.write(cadena+"\n")
cadena='<para></para>'
sortida.write(cadena+"\n")
cadena='</legalnotice>'
sortida.write(cadena+"\n")
cadena='<author>'
sortida.write(cadena+"\n")
cadena='<firstname>'+author_firstname+'</firstname>'
sortida.write(cadena+"\n")
cadena='<surname>'+author_surname+'</surname>'
sortida.write(cadena+"\n")
cadena='</author>'
sortida.write(cadena+"\n")
cadena='</bookinfo>'
sortida.write(cadena+"\n")

for para in paras:
    cadena=""
    if not para.startswith("<chapter>") and not para.startswith("</chapter>") and not para.startswith("<title>") and not para.startswith("</title>") and not para.startswith("<part>") and not para.startswith("</part>"):
        cadena="<para>"+para+"</para>"
        
    elif para.startswith("<chapter>") or para.startswith("</chapter>") or para.startswith("<title>") or para.startswith("</title>") or para.startswith("<part>") or para.startswith("</part>"):
        cadena=para
    if not cadena=="":
        sortida.write(cadena+"\n")
    
if "</chapter>" in closetags:
    cadena="</chapter>"
    sortida.write(cadena+"\n")
if "</part>" in closetags:
    cadena="</part>"
    sortida.write(cadena+"\n")
cadena='</book>'
sortida.write(cadena+"\n")
