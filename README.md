# ccmap-area-tool
Simple script to generate wiki and markdown tables containing the area of ccmap nation polygons, used for updating [a wiki page](https://civwiki.org/wiki/List_of_nations_by_area)

## Usage

* Install `mwclient`and `wikitextparser`python packages

* Create a file titled `secret.py`, in here create two variables titled `USER` and `PASSWORD`, put your login credentials there
* Run `areaCalculator.py --wiki`

### Settings

* `--wiki`- Upload to wiki
* `--offline` - Print table to a text file
* `--markdown`- Generate a markdown table
* `--sandbox`- Use a sandbox page