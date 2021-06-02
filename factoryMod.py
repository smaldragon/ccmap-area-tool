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

def parseMaterials(mat_list):
    mat_txt = ""
    for mat in mat_list:
        if mat != 'chance':
            if mat_txt != "":
                mat_txt += ", "
            amount = ""
            if 'amount' in mat_list[mat]:
                amount = str(mat_list[mat]['amount']) + " "
            mat_txt += "{}{}".format(
                amount,
                clean_name(mat_list[mat]['material'])
            )
            if 'lore' in mat_list[mat]:
                mat_txt += " ({})".format(' '.join(mat_list[mat]['lore']))
            if 'enchants' in mat_list[mat]:
                for enchant in mat_list[mat]['enchants']:
                    mat_txt = "{}{} {}".format(
                        enchant,
                        mat_list[mat]['enchants'][enchant]['level'],
                        mat_txt
                    )
    return mat_txt

DATA_URL = "https://raw.githubusercontent.com/CivClassic/AnsibleSetup/master/templates/public/plugins/FactoryMod/config.yml.j2"
MODE = "WIKI"

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

default_fuel_interval = data['default_fuel_consumption_intervall']
default_fuel = parseMaterials(data['default_fuel'])
#default_fuel = "" # Everything in civclassics uses the same fuel so clearing for readibility
factories = []

for factory in data['factories']:
    n_factory = {}
    fac = data['factories'][factory]
    print (fac['name'])
    n_factory['name'] = fac['name']
    n_factory['recipes'] = []
    n_factory['repair'] = {}
    n_factory['tables'] = {}

    # Get Setup Cost
    if fac['type'] == 'FCC':
        n_factory['setup'] = parseMaterials(fac['setupcost'])
        #print(n_factory['setup'])
    else:
        print("type",fac['type'])
    
    for recipe in fac['recipes']:
        rec = data['recipes'][recipe]
        name = rec['name']
        r_in = ""
        r_out = ""
        time = rec['production_time']
        fuel = ""

        if rec['type'] == 'PRODUCTION':  
            r_in = parseMaterials(rec['input'])
            r_out = parseMaterials(rec['output'])
            
            #print("{} | {} -> {}".format(rec['name'],r_in,r_out))
        elif rec['type'] == 'REPAIR':
            r_in = parseMaterials(rec['input'])
            r_out = "+{} health".format(rec['health_gained'])

            #print("Repair: {}".format(r_in))
        elif rec['type'] == 'RANDOM':
            r_in = parseMaterials(rec['input'])
            r_out = "(Random Item)"

            table = []
            # Parse the Loot Table Here
            for output in rec['outputs']:
                roll = {}
                poss = rec['outputs'][output]

                roll['name'] = clean_name(output)
                roll['chance'] = poss['chance']*100
                roll['item'] = parseMaterials(rec['outputs'][output])

                table.append(roll)
            
            n_factory['tables'][name] = table

        elif rec['type'] == 'UPGRADE':
            r_in = parseMaterials(rec['input'])
            r_out = "Convert factory to {}".format(rec['factory'])
        elif rec['type'] == 'COMPACT':
            r_in = "1 Crate, (Stack to Compact)"
            r_out = "(Compacted Stack)"
        elif rec['type'] == 'DECOMPACT':
            r_in = "(Compacted Stack)"
            r_out = "(Decompacted Stack)"
        elif rec['type'] == 'WORDBANK':
            pass
        elif rec['type'] == 'PRINTBOOK':
            r_in = parseMaterials(rec['input']) + ", (Printing Plate)"
            r_out = "{} Printed Books".format(rec['outputamount']) 
        elif rec['type'] == 'PRINTINGPLATE':
            r_in = parseMaterials(rec['input'])
            r_out = parseMaterials(rec['output'])
        elif rec['type'] == 'PRINTINGPLATEJSON':
            r_in = parseMaterials(rec['input'])
            r_out = parseMaterials(rec['output'])
        elif rec['type'] == 'PRINTNOTE':
            r_in = "{}, {}".format(parseMaterials(rec['input']), '(Printing Plate)')
            r_out = "{} {}".format(rec['outputamount'],rec['title'])
        else:
            print(rec['type'],rec['name'])

        #Fuel math
        interval = default_fuel_interval
        if 'fuel_consumption_intervall' in rec:
            interval = rec['fuel_consumption_intervall']

        fuel_type = default_fuel

        if 'fuel' in rec:
            fuel_type = rec['fuel']

        fuel = "{} {}".format(int(float(time[:-1])/float(interval[:-1])),fuel_type)

        parsed_rec = {
                    "name":name,
                    "input":r_in,
                    "output":r_out,
                    "time":time,
                    "fuel":fuel
        }

        if rec['type'] != 'REPAIR':
            n_factory['recipes'].append(parsed_rec)
        else:
            n_factory['repair'] = parsed_rec
        #print(name,r_in,r_out,time,fuel)
    factories.append(n_factory)
    #print(n_factory)

if MODE == "MARKDOWN":
    txt = ""
    for fac in factories:
        txt += "#### {}\n".format(fac['name'])
        if 'setup' in fac:
            txt += "**Setup Cost**: {}\n".format(fac['setup'])
        txt += "| Recipe | Input | Output | Time | Fuel |\n"
        txt += "| --- | --- | --- | --- | --- |\n"
        for rec in fac['recipes']:
            txt += "| {} | {} | {} | {} | {} |\n".format(
                rec['name'],
                rec['input'],
                rec['output'],
                rec['time'],
                rec['fuel']
            )
        txt += "| *{}* | {} | *{}* | {} | {} |\n".format(
                fac['repair']['name'],
                fac['repair']['input'],
                fac['repair']['output'],
                fac['repair']['time'],
                fac['repair']['fuel']
        )
        txt += "\n"
    with open("factories.md","w") as f:
        f.write(txt)
elif MODE == "WIKI" or MODE == "OFFLINE":
    txt = ""
    for fac in factories:
        txt += "===={}====\n".format(fac['name'])
        if 'setup' in fac:
            txt += "'''Setup Cost''': {}\n".format(fac['setup'])
        txt += "{|class=\"wikitable\"\n|-\n"
        txt += "! Recipe !! Input !! Output !! Time !! Fuel \n"
        for rec in fac['recipes']:
            txt += "|-\n| {} || {} || {} || {} || {} \n".format(
                rec['name'],
                rec['input'],
                rec['output'],
                rec['time'],
                rec['fuel']
            )
        txt += "|-\n| ''{}'' || {} || ''{}'' || {} || {} \n".format(
                fac['repair']['name'],
                fac['repair']['input'],
                fac['repair']['output'],
                fac['repair']['time'],
                fac['repair']['fuel']
        )
        txt += "|}\n"
    if MODE == "OFFLINE":
        with open("factories.txt","w") as f:
            f.write(txt)
    elif MODE == "WIKI":
        ua = "FactoryMod/0.0.1 Smal"
        site = Site('civwiki.org',clients_useragent=ua)
        page = site.pages['Template:FactoryModConfig (CivClassic 2.0)']
        site.login(USER,PASSWORD)
        page.edit(txt,"Automated Data Update")
