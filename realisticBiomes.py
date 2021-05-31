import urllib.request
import yaml

def clean_name(n):
    return n.lower().replace("_"," ").title()

DATA_URL = "https://raw.githubusercontent.com/CivClassic/AnsibleSetup/master/templates/public/plugins/RealisticBiomes/config.yml.j2"

 # Get the latest biomes yaml
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
req = urllib.request.Request(url=DATA_URL, headers=headers)

data = []
with urllib.request.urlopen(req) as url:
    data = yaml.load(url.read().decode())
    #print(data)
    
for alias in data["biome_aliases"]:
    print(alias.title().replace("_"," "))
    print(data["biome_aliases"][alias])

    for plant in data["plants"]:
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
            print(clean_name(plant),rate)
            