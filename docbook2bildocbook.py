#    docbook2bildocbook
#    Copyright (C) 2022  Antoni Oliver
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

import argparse
import html2text
import sys
import re
import codecs
import glob
import os
from bs4 import BeautifulSoup
import srx_segmenter
from datetime import date
from xml.sax.saxutils import escape

import xml.etree.ElementTree as etree
import io

#IMPORTS FOR MTUOC CLIENT
from websocket import create_connection
import socket

#IMPORTS FOR MOSES CLIENT
import xmlrpc.client

#IMPORTS FOR OPENNMT / MODERNMT CLIENT
import requests

#IMPORTS FOR YAML
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def print_info(message1,message2=""):
    print(message1,message2)


def connect():
    server_type=args.type
    if server_type=="MTUOC":
        try:
            service="ws://"+args.ip+":"+str(args.port)+"/translate"
            global ws
            ws = create_connection(service)
        except:
            errormessage="Error connecting to MTUOC: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)
            
    elif server_type=="Moses":
        try:
            global proxyMoses
            proxyMoses = xmlrpc.client.ServerProxy("http://"+args.ip+":"+str(args.port)+"/RPC2")
        except:
            errormessage="Error connecting to Moses: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)      
            
    elif server_type=="OpenNMT":
        try:
            global urlOpenNMT
            urlOpenNMT = "http://"+args.ip+":"+str(args.port)+"/translator/translate"
        except:
            errormessage="Error connecting to OpenNMT: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)   
    elif server_type=="NMTWizard":
        try:
            global urlNMTWizard
            urlNMTWizard = "http://"+args.ip+":"+str(args.port)+"/translate"
        except:
            errormessage="Error connecting to NMTWizard: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)           
    elif server_type=="ModernMT":
        try:
            global urlModernMT
            urlModernMT = "http://"+args.ip+":"+str(args.port)+"/translate"
        except:
            errormessage="Error connecting to ModernMT: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)
    
def translate_segment_MTUOC(segment):
    translation=""
    try:
        ws.send(segment)
        translation = ws.recv()
    except:
        errormessage="Error retrieving translation from MTUOC: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
    return(translation)

    
def translate_segment_OpenNMT(segment):
    global urlOpenNMT
    translation=""
    try:
        headers = {'content-type': 'application/json'}
        params = [{ "src" : segment}]
        response = requests.post(urlOpenNMT, json=params, headers=headers)
        target = response.json()
        translation=target[0][0]["tgt"]
    except:
        errormessage="Error retrieving translation from OpenNMT: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
    return(translation)

    
def translate_segment_NMTWizard(segment):
    global urlNMTWizard
    translation=""
    try:
        headers = {'content-type': 'application/json'}
        params={ "src": [  {"text": segment}]}
        response = requests.post(urlNMTWizard, json=params, headers=headers)
        target = response.json()
        translation=target["tgt"][0][0]["text"]
    except:
        print(sys.exc_info())
        errormessage="Error retrieving translation from NMTWizard: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
    return(translation)
    
def translate_segment_ModernMT(segment):
    global urlModernMT
    params={}
    params['q']=segment
    response = requests.get(urlModernMT,params=params)
    target = response.json()
    translation=target['data']["translation"]
    return(translation)
        
def translate_segment_Moses(segment):
    translation=""
    try:
        param = {"text": segment}
        result = proxyMoses.translate(param)
        translation=result['text']
    except:
        errormessage="Error retrieving translation from Moses: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
    return(translation)
    
def translate_segment(segment):
    if args.process=="MTUOC":
        MTEngine=args.type
        if MTEngine=="MTUOC":
            translation=translate_segment_MTUOC(segment)
        elif MTEngine=="OpenNMT":
            translation=translate_segment_OpenNMT(segment)
        elif MTEngine=="NMTWizard":
            translation=translate_segment_NMTWizard(segment)
        elif MTEngine=="ModernMT":
            translation=translate_segment_ModernMT(segment)
        elif MTEngine=="Moses":
            translation=translate_segment_Moses(segment)
    elif args.process=="TSV":
        translation=translate_segmentFake(segment)
    translation=translation.replace("\n"," ")
    return(translation)


today = date.today()

blacklist = [   '[document]',   'noscript', 'header',   'html', 'meta', 'head','input', 'script',   ]

def translate(segment):
    return(segment[::-1])
    
def translate_segmentFake(segment):
    return(segment[::-1])

stream = open('config.yaml', 'r',encoding="utf-8")
config=yaml.load(stream,Loader=Loader)
book_lang=config['book_lang']
srx_file=config['srx_file']
srx_lang=config['srx_lang']

parser = argparse.ArgumentParser(description='A script to convert an docbook file into a bilingual docbook file translating using MTUOC or a TSV file.')
parser.add_argument("-i", "--input_file", type=str, help="The epub input file to convert", required=True)
parser.add_argument("-o", "--output_file", type=str, help="The output bilingual docbook file", required=True)
parser.add_argument("-p", "--process", dest='process', type=str, help="The kind of process: MTUOC or TSV", required=True)
parser.add_argument('--ip', dest='ip', help='The ip of the server or localhost', action='store',required=False)
parser.add_argument('--port', dest='port', help='The port used by the server', action='store',required=False)
parser.add_argument('--type', dest='type', help='The type of server. One of: MTUOC, Moses, OpenNMT, NMTWizard, ModernMT', action='store',required=False)

parser.add_argument("--tsv", dest='tsvfile', type=str, help="The TSV file", required=False)

rules = srx_segmenter.parse(srx_file)


args = parser.parse_args()

process=args.process



if args.process=="MTUOC":
    if args.ip==None or args.port==None or args.type==None:
        print("If you use the MTUOC process you have to give an ip, a port and a type of the MTUOC server to use.")
        sys.exit()

    connect()

if args.process=="TSV":
    if args.tsvfile==None:
        print("If you use the TSV process you have to give a tsv file with the --tsv option.")
        sys.exit()

sortida=codecs.open(args.output_file,"w",encoding="utf-8")
contsegment=0
conttitle=0
traduccions=[]

tree = etree.parse(args.input_file)
root = tree.getroot()
title=root.findall("./title")[0].text
author_firstname=root.findall("./bookinfo/author/firstname")[0].text
author_surname=root.findall("./bookinfo/author/surname")[0].text

print("TITLE",title)
print("AUTHOR FN",author_firstname)
print("AUTHOR SN",author_surname)


cadena='<book lang="'+book_lang+'">'
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
previus_element=[]
inPart=False
inChapter=False
inSection=False
for event, elem in etree.iterparse(args.input_file, events=("start", "end")):
    try:
        prelement=previus_element[-2]
    except:
        prelement=None
    if  event=='end' and elem.tag=="para":
        if elem.text:
            cadena="<para>"
            sortida.write(cadena+"\n")
            paragraph=elem.text
            segmenter = srx_segmenter.SrxSegmenter(rules[srx_lang],elem.text)
            segments=segmenter.extract()
            tripleta=[]
            tripleta.append("open-para")
            tripleta.append("")
            tripleta.append("")
            traduccions.append(tripleta)
            for s in segments[0]:
                contsegment+=1
                cadena='<phrase id="ss-'+str(contsegment)+'"><link linkend="ts-'+str(contsegment)+'">'+str(s)+'</link></phrase>'
                sortida.write(cadena+"\n")
                tripleta=[]
                tripleta.append("segment")
                tripleta.append(contsegment)
                
                traduccio=translate_segment(s)
                tripleta.append(traduccio)
                traduccions.append(tripleta)
                print(traduccio)
                print("----")
            cadena="</para>"
            sortida.write(cadena+"\n")
            tripleta=[]
            tripleta.append("close-para")
            tripleta.append("")
            tripleta.append("")
            traduccions.append(tripleta)
    if  event=='end' and elem.tag=="title":
        if elem.text:
            title=elem.text
            conttitle+=1
            print("TITLE",title,"PREV",prelement.tag)
            tripleta=[]
            if prelement.tag=="section":
                if inSection:
                    cadena="</section>"
                    sortida.write(cadena+"\n")
                    tripleta=[]
                    tripleta.append("close-section")
                    tripleta.append("")
                    tripleta.append("")
                    traduccions.append(tripleta)
                    inSection=False
                inSection=True
                cadena="<section>"
                sortida.write(cadena+"\n")
                tripleta=[]
                tripleta.append("open-section")
                tripleta.append("")
                tripleta.append("")
            if prelement.tag=="chapter":
                if inSection:
                    cadena="</section>"
                    sortida.write(cadena+"\n")
                    tripleta=[]
                    tripleta.append("close-section")
                    tripleta.append("")
                    tripleta.append("")
                    traduccions.append(tripleta)
                    inSection=False
                if inChapter:
                    cadena="</chapter>"
                    sortida.write(cadena+"\n")
                    tripleta=[]
                    tripleta.append("close-chapter")
                    tripleta.append("")
                    tripleta.append("")
                    traduccions.append(tripleta)
                    inChapter=False
                inChapter=True
                cadena="<chapter>"
                sortida.write(cadena+"\n")
                tripleta=[]
                tripleta.append("open-chapter")
                tripleta.append("")
                tripleta.append("")
            elif prelement.tag=="part":
                if inSection:
                    cadena="</section>"
                    sortida.write(cadena+"\n")
                    tripleta=[]
                    tripleta.append("close-section")
                    tripleta.append("")
                    tripleta.append("")
                    traduccions.append(tripleta)
                    inSection=False
                if inChapter:
                    cadena="</chapter>"
                    sortida.write(cadena+"\n")
                    tripleta=[]
                    tripleta.append("close-chapter")
                    tripleta.append("")
                    tripleta.append("")
                    traduccions.append(tripleta)
                    inChapter=False
                if inPart:
                    cadena="</part>"
                    sortida.write(cadena+"\n")
                    tripleta=[]
                    tripleta.append("close-part")
                    tripleta.append("")
                    tripleta.append("")
                    traduccions.append(tripleta)
                    inPart=False
                inPart=True
                cadena="<part>"
                sortida.write(cadena+"\n")
                tripleta=[]
                tripleta.append("open-part")
                tripleta.append("")
                tripleta.append("")
            traduccions.append(tripleta)
            cadena="<title id='st-"+str(conttitle)+"'>"+str(title)+"</title>"
            sortida.write(cadena+"\n")
            titletrad=translate_segment(title)
            tripleta=[]
            tripleta.append("title")
            tripleta.append(conttitle)
            tripleta.append(titletrad)
            traduccions.append(tripleta)
            
    previus_element.append(elem)
if inSection:
    cadena="</section>"
    sortida.write(cadena+"\n")
    tripleta=[]
    tripleta.append("close-section")
    tripleta.append("")
    tripleta.append("")
    traduccions.append(tripleta)
    inSection=False

if inChapter:
    cadena="</chapter>"
    sortida.write(cadena+"\n")
    tripleta=[]
    tripleta.append("close-chapter")
    tripleta.append("")
    tripleta.append("")
    traduccions.append(tripleta)
    inChapter=False
if inPart:
    cadena="</part>"
    sortida.write(cadena+"\n")
    tripleta=[]
    tripleta.append("close-part")
    tripleta.append("")
    tripleta.append("")
    traduccions.append(tripleta)
    inPart=False
for tripleta in traduccions:
    print(tripleta)
    if len(tripleta)==3:
        if tripleta[0]=="segment":
            contsegment=tripleta[1]
            s=tripleta[2]
            cadena='<phrase id="ts-'+str(contsegment)+'"><link linkend="ss-'+str(contsegment)+'">'+str(s)+'</link></phrase>'
            sortida.write(cadena+"\n")
        elif tripleta[0]=="open-para":
            cadena="<para>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="close-para":
            cadena="</para>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="title":
            cadena="<title id='tt-"+str(tripleta[1])+"'>"+str(tripleta[2])+"</title>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="open-section":
            cadena="<section>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="open-chapter":
            cadena="<chapter>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="open-part":
            cadena="<part>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="close-section":
            cadena="</section>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="close-chapter":
            cadena="</chapter>"
            sortida.write(cadena+"\n")
        elif tripleta[0]=="close-part":
            cadena="</part>"
            sortida.write(cadena+"\n")
cadena='</book>'
sortida.write(cadena+"\n")
