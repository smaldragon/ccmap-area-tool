import urllib.request
import yaml

from mwclient import Site
from mwclient.errors import LoginError
import wikitextparser as wtp

from secret import USER,PASSWORD

def clean_name(n):
    return n.lower().replace("_"," ").title()

def sortFunc(e):
    result = 0
    if e[-1] == 'h':
        result = float(e[:-1])
    else:
        result = float(e[:-1])*1000
    return result

DATA_URL = "https://raw.githubusercontent.com/CivClassic/AnsibleSetup/master/templates/public/plugins/RealisticBiomes/config.yml.j2"

 # Get the latest biomes yaml
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
req = urllib.request.Request(url=DATA_URL, headers=headers)

page_txt = ""
#page_txt = "= Realistic Biomes Growth Rates =\n"

# Download the config
data = []
with urllib.request.urlopen(req) as url:
    data = yaml.load(url.read().decode())
    #print(data)

# Parse the config and generate the page, 1 biome group at a time
for alias in data["biome_aliases"]:
    page_txt += "===={}====\n".format(clean_name(alias))
    first_biome = True
    biomes_list = ""
    
    for biome in data["biome_aliases"][alias]:
        if not first_biome:
            biomes_list+=", "
        biomes_list += biome.lower()
        first_biome = False
    page_txt += "'''Biomes:''' ''{}''\n".format(biomes_list)
    page_txt += '{|class="wikitable sortable"\n|-\n! Plant !! Growth Time\n'
    print(alias.title().replace("_"," "))
    print(data["biome_aliases"][alias])

    plants = {}
    for plant in data["plants"]:
        #print(plant)
        pd = data["plants"][plant]
        base_rate = pd["persistent_growth_period"]
        if type(base_rate) == str:
            base_rate = int(base_rate[:-1])
        if alias in pd["biomes"]:
            val = pd["biomes"][alias]
            rate = ""
            if base_rate == 0:
                rate = str(100*val)+"%"
            elif val > 0:
                time = base_rate/val
                hours = int(time)
                minutes = int((time*60)%60)
                if hours > 0:
                    rate += "{}h".format(hours)
                if minutes > 0:
                    rate += "{}m".format(minutes)
            if rate != "":
                #print(clean_name(plant),rate)
                plants[plant] = rate

    sorted_values = list(plants.values())
    sorted_values.sort(key=sortFunc)
    sorted_plants = {}

    for i in sorted_values:
        for k in plants.keys():
            if plants[k] == i:
                sorted_plants[k] = plants[k]
                plants.pop(k)
                break
    for pl in sorted_plants.keys():
        page_txt += "|-\n| {} || {}\n".format(data["plants"][pl]["name"],sorted_plants[pl])

    page_txt += "|}\n"

# Output
with open("biomes.txt","w") as f:
    f.write(page_txt)

ua = "RealisticBiomes/0.0.1 Smal"
site = Site('civwiki.org',clients_useragent=ua)
page = site.pages['Template:RealisticBiomesConfig (CivClassic 2.0)']
text = page.text()
#text. += page_txt

site.login(USER,PASSWORD)

page.edit(page_txt,"Automated Data Update")
print(page.text())