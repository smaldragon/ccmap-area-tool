# ccmap-area-tool
Simple script to generate wiki and markdown tables containing the area of ccmap nation polygons, used for updating [a wiki page](https://civwiki.org/wiki/List_of_nations_by_area)

## Config

The file `config.py` contains several variables that are used by the script(s):

* `SERVER_NAME` - Name of the server, used for the titles of the generated pages
* `FACTORY_URL` - The url to the factorymod config `.yml`

## Usage

* Install `mwclient`and `wikitextparser`python packages
* Create a file titled `secret.py`, in here create two variables titled `USER` and `PASSWORD`, put your login credentials there
* Run `areaCalculator.py --wiki` to update nations by area page
* Run `realisticBiomes.py` to update realistic biomes template
* Run `factoryMod.py` to update factory mod template

### Settings

* `--wiki`- Upload to wiki
* `--offline` - Print table to a text file
* `--markdown`- Generate a markdown table
* `--sandbox`- Use a sandbox page