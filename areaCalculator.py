import json
import math
import re
import urllib.request
from helpers import ACRONYMS,HAS_FLAG_TEMPLATE

MERGE = True
WORLD_AREA = math.pi * (13000*13000)
MODE = "WIKI"
DATA_URL = "https://githubraw.com/ccmap/data/master/land_claims.civmap.json"

def polygon_area(vertices):
    psum = 0
    nsum = 0

    for i in range(len(vertices)):
        sindex = (i + 1) % len(vertices)
        prod = vertices[i][0] * vertices[sindex][1]
        psum += prod

    for i in range(len(vertices)):
        sindex = (i + 1) % len(vertices)
        prod = vertices[sindex][0] * vertices[i][1]
        nsum += prod

    return abs(1/2*(psum - nsum))

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
req = urllib.request.Request(url=DATA_URL, headers=headers)

with urllib.request.urlopen(req) as url:
  data = json.loads(url.read().decode())

#with open('land_claims.civmap.json') as f:
#    data = json.load(f)

areas = {}

for feat in data["features"]:
    
    name = feat["name"]
    nation = ( re.sub("\(|\)","",re.search("(^[^()]+$)|\((.*)\)",name.replace("\n"," ")).group()))
    if ACRONYMS.get(nation) is not None:
        nation = ACRONYMS.get(nation)

    area = 0
    if "polygon" in feat:
         for poly in feat["polygon"]:
            area += polygon_area(poly)
    else:
        print(feat)

    if nation in areas:
        areas[nation] += area
    else:
        areas[nation] = area

areas_sorted = {}    
areas_sorted_keys = sorted(areas,key=areas.get,reverse=True)
for w in areas_sorted_keys:
    areas_sorted[w] = areas[w]

if MODE == "MARKDOWN":
    with open('areas.md','w') as f:
        f.write("#|Nation|Area (km²)|% of Map Area\n")
        f.write(":---:|:---:|:---:|:---:|\n")
        f.write("{}|{}|{}|{}\n".format(0,"*CivClassic*",round(WORLD_AREA/1000000,3),100))

        i = 1
        for key in areas_sorted.keys():
            are = round(areas[key]/1000000,3)
            per = round ((areas[key]/WORLD_AREA)*100,3)
            print(key,are)
            f.write("{}|{}|{}|{}\n".format(i,key,are,per))
            i = i + 1
if MODE == "WIKI":
    with open('areas.txt','w') as f:
        f.write("{| class=\"wikitable sortable\"\n|+\n!Rank\n!Nation\n!Area in km²\n!% of Map Area\n|-\n")
        f.write("|-\n|{}\n|{}\n|{}\n|{}\n".format(0,"''[[CivClassic]]''",round(WORLD_AREA/1000000,3),100))

        i = 1
        for key in areas_sorted.keys():
            are = round(areas[key]/1000000,3)
            per = round ((areas[key]/WORLD_AREA)*100,3)
            print(key,are)
            nation_txt = "[[{}]]".format(key)
            if key in HAS_FLAG_TEMPLATE:
              nation_txt = "{{{{flag|{}}}}}".format(key)
            f.write("|-\n|{}\n|{}\n|{}\n|{}\n".format(i,nation_txt,are,per))
            i = i+1
        f.write("|}")
