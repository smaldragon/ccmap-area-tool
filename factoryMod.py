import sys, getopt
import urllib.request
import yaml
import os

from mwclient import Site
from mwclient.errors import LoginError
import wikitextparser as wtp
from time import sleep

from secret import USER,PASSWORD
from config import SERVER_NAME,FACTORY_URL

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
                    mat_txt = "{} {} {}".format(
                        mat_txt,
                        clean_name(mat_list[mat]['enchants'][enchant]['enchant']),
                        mat_list[mat]['enchants'][enchant]['level']
                    )
    return mat_txt

def main(argv):
    # ------------- Constant Variables ----------------
    MODE = "NONE"
    # -------------------------------------------------

    try: 
        opts, args = getopt.getopt(argv,"h",["markdown","wiki","offline","sandbox","help"])
    except getopt.GetoptError:
        print("factoryMod.py --wiki")
        sys.exit(2)
    for opt,arg in opts:
        if opt in ('-h','--help'):
            print ("--wiki , --offline , --help")
        if opt in "--wiki":
            MODE = "WIKI"
        if opt in "--offline":
            MODE = "OFFLINE"
        if opt in "--none":
            MODE = "NONE"

    # Get the latest biomes yaml
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=FACTORY_URL, headers=headers)

    page_txt = ""
    #page_txt = "= Realistic Biomes Growth Rates =\n"

    # Download the config
    print("downloading config..")
    data = []
    with urllib.request.urlopen(req) as url:
        data = yaml.safe_load(url.read().decode())

    print("Config Downloaded, parsing data...")

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
        n_factory['repair'] = []
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
                uniques = {}
                # Parse the Loot Table Here
                for output in rec['outputs']:
                    roll = {}
                    poss = rec['outputs'][output] 

                    roll['name'] = clean_name(output)
                    roll['chance'] = poss['chance']*100
                    roll['item'] = parseMaterials(rec['outputs'][output])

                    table.append(roll)
                    unique_name = roll['item']
                    if "spawn egg" in unique_name.lower():
                        unique_name = "Spawn Egg"
                    if "music disc" in unique_name.lower():
                        unique_name = "Music Disc"

                    if unique_name in uniques:
                        uniques[unique_name].append(roll)
                    else:
                        uniques[unique_name] = [roll]
                
                n_factory['tables'][name] = uniques

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
                r_in = parseMaterials(rec['input']) + ", 1 Oak Trapdoor (Printing Plate)"
                r_out = "{} Printed Books".format(rec['outputamount']) 
            elif rec['type'] == 'PRINTINGPLATE':
                r_in = parseMaterials(rec['input']) + ", 1 Written Book"
                r_out = parseMaterials(rec['output']) + " (Printing Plate)"
            elif rec['type'] == 'PRINTINGPLATEJSON':
                r_in = parseMaterials(rec['input']) + ", 1 Written Book"
                r_out = parseMaterials(rec['output']) + " (Printing Plate)"
            elif rec['type'] == 'PRINTNOTE':
                r_in = "{}, {}".format(parseMaterials(rec['input']), '1 Oak Trapdoor (Printing Plate)')
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
                n_factory['repair'].append(parsed_rec)
            #print(name,r_in,r_out,time,fuel)
        factories.append(n_factory)
        #print(n_factory)

    '''
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
    '''
    if MODE == "WIKI" or MODE == "OFFLINE":
        print("Writing tables...")
        fac_txt = {}
        ua = "FactoryMod/0.0.1 Smal"
        site = Site('civwiki.org',clients_useragent=ua)
        site.login(USER,PASSWORD)

        if not os.path.exists('preview'):
            os.makedirs('preview')

        for fac in factories:
            # Generate Factory Table
            txt = ""
            txt += "{|class=\"wikitable mw-collapsible\"\n"
            txt += "|+ class=\"nowrap\" |{}\n".format(fac['name'])
            txt += "! Recipe !! Input !! Output !! Time !! Fuel \n"
            for rec in fac['recipes']:
                txt += "|-\n| {} || {} || {} || {} || {} \n".format(
                    rec['name'],
                    rec['input'],
                    rec['output'],
                    rec['time'],
                    rec['fuel']
                )
            for rep in fac['repair']:
                txt += "|-\n| ''{}'' || {} || ''{}'' || {} || {} \n".format(
                        rep['name'],
                        rep['input'],
                        rep['output'],
                        rep['time'],
                        rep['fuel']
                )
            if 'setup' in fac:
                txt += "|-\n| '''Create Factory''' || colspan=\"4\"| {}\n".format(fac['setup'])
            txt += "|}"

            # Generate Additional Tables
            for table_key in fac['tables']:
                txt += "\n{|class=\"wikitable mw-collapsible mw-collapsed sortable\"\n"
                txt += "|+ class=\"nowrap\" |{}\n".format(table_key)
                txt += "! Name !! Item !! Chance\n"
                for item in fac['tables'][table_key]:
                    items = fac['tables'][table_key][item]
                    if len(items) == 1:
                        txt += "|-\n"
                        txt += "| {} || {} || align=\"right\"| {}\n".format(
                            items[0]['name'],
                            items[0]['item'],
                            round(items[0]['chance'],5)
                        )
                    else:
                        names = ""
                        chance = 0
                        for i in items:
                            names += f"{i['name']} | "
                            chance += i["chance"]
                        txt += "|-\n"
                        txt += "| {{Collapsible list |"
                        txt += "title = {} |  {} ".format(
                            item,
                            names,
                        )
                        txt += "}} \n"
                        txt += "| {} || align=\"right\"| {}\n".format(
                            item,
                            round(chance,5)
                        )
                txt += "|}"

            page_title = 'Template:FactoryModConfig {} ({})'.format(fac['name'],SERVER_NAME)
            with open('preview/{}.txt'.format(page_title),'w') as f:
                f.write(txt)
            
            page = site.pages[page_title]
            if (page.text() != txt):
                print("\033[41mDIFF\033[49m",page_title)
                if MODE == "WIKI":
                    page.edit(txt,"Automated Data Update")

            else:
                print("SAME",page_title)

            sleep(0.2) # To prevent rate limiting

    print("Done!")

if __name__ == "__main__":
    main(sys.argv[1:])
