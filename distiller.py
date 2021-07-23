from subprocess import check_output
from typing import Any
import urllib
import urllib.request
from icalendar import Calendar, Event, prop
import argparse
import json
import sys

'''
Create calendars in ical format for the 2021 Olympics, selecting only some sports.
Last version of this script should be here https://gist.github.com/VincenzoLaSpesa

The usage is something like:

.\distiller.py --merge -i -j Taekwondo Karate Wrestling Rugby Judo Boxing "Cycling Mountain Bike"

with a list of selected sport at the end of the command. Call it with no parameters for the help, this:

usage: distiller.py [-h] [-s] [-i] [-j] [-d] [-a] [-m] [sports [sports ...]]

positional arguments:
  sports

optional arguments:
  -h, --help    show this help message and exit
  -s, --single  Create a calendar for every single sport
  -i, --ical    Use ical as output format
  -j, --json    Use json as output format
  -d, --dump    Dump the original
  -a, --all     Dump the entire calendar
  -m, --merge   Create a calendar just for the sport provided as parameters

This script is released under the "Unlicense" license https://unlicense.org/

Thanks to anarchycupcake for the original calendar, you can find more info on the reddit thread here 
https://www.reddit.com/r/olympics/comments/mwa3qu/i_made_a_google_calendar_for_all_tokyo_2020_events/
'''


MAIN_URL=r"https://calendar.google.com/calendar/ical/d7qjh47tgfc6ei1cfsrsc6lr30%40group.calendar.google.com/public/basic.ics"


def run(cmd, echo=True, shell=True, printOutput = True) -> str:
    """ Runs a command, returns the output """    

    if echo:
        print(cmd)
    output = check_output(cmd, shell=shell).decode("utf-8") 
    if printOutput:
      print(output)
    return output

def getUrlAsString(url : str) -> str:
    try:
        with urllib.request.urlopen(url) as stream:
            return stream.read()
    except Exception as e:
        print("Error :%s" % e)
    return None

def Tokenize(string: str) -> tuple:
    "split the title in the name of the sport and the medals ( if any)"
    sportname = ""
    medals=""
    for t in string.split():
        if t.startswith('🥇') or t.startswith('🥈') or t.startswith('🥉'):
            medals+=t
        else:
            sportname+=t + " " 

    return (sportname.strip(), medals.strip())

KEYS_FOR_CALENDAR=('PRODID','VERSION','CALSCALE','X-WR-CALNAME','X-WR-TIMEZONE','X-WR-CALDESC')
KEYS_FOR_EVENT=('SUMMARY','DTSTART','DTEND','DTSTAMP','UID','SEQUENCE','CREATED','DESCRIPTION','LAST-MODIFIED','LOCATION','STATUS','TRANSP')

def ComposeCleanObject(obj: Any) -> dict:
    "Convert a VCALENDAR item into something directly serializable to json, it's just for debug"
    t = type(obj)
    dump={}
    if t==Calendar:
        for k in KEYS_FOR_CALENDAR:
            dump[k] = ComposeCleanObject(obj[k])    
    elif t==Event:
        for k in KEYS_FOR_EVENT:
            dump[k] = ComposeCleanObject(obj[k])
    elif t==prop.vDDDTypes:
        return str(obj.dt)
    elif t==prop.vInt:
        return int(obj)        
    else:
        return str(obj)

    dump['type']=str(t)   
    return dump

def ComposeCleanListOfObject(headers: list, objects: list) -> list:
    objs=[]
    for h in headers:
        objs.append(ComposeCleanObject(h))        
    
    t = type(objects)
    if t== dict:   
        for _,v in objects.items():
            for obj in v:
                objs.append(ComposeCleanObject(obj))
    else:
        for x in objects:
            objs.append(ComposeCleanObject(x))
    return objs



# main
DEBUG = False

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--single",help="Create a calendar for every single sport",action='store_true')
parser.add_argument("-i", "--ical",help="Use ical as output format",action='store_true')
parser.add_argument("-j", "--json",help="Use json as output format",action='store_true')
parser.add_argument("-d", "--dump",help="Dump the original",action='store_true')
parser.add_argument("-a", "--all",help="Dump the entire calendar",action='store_true')
parser.add_argument("-m", "--merge",help="Create a calendar just for the sport provided as parameters",action='store_true')
parser.add_argument('sports', nargs='*')
args= None

if DEBUG:
    args = parser.parse_args(["--json", "--merge", "--single", "--ical", "Taekwondo", "Karate"])
else:
    args = parser.parse_args()

# if no format is selected default to ical
if not args.ical and not args.json:
    args.ical = True

ical=getUrlAsString(MAIN_URL)

if ical==None:
    sys.exit(-1)

gcal = Calendar.from_ical(ical)
events={}
headers=[]
for component in gcal.walk():    
    if component.name == "VEVENT":
        # remove the medals from the name, put it to the description
        tokens = Tokenize(component.get('summary'))
        name=tokens[0]
        component['description'] =  tokens[1] + " " + component['description']
        component['summary'] =  tokens[0] + " " + tokens[1]
        if name not in events:
            events[name]=[]
        
        events[name].append(component)
    else:
        headers.append(component)

print("The calendar contains these events: ")
kind_of_events = sorted([str(x) for x in events.keys()])
print(json.dumps(kind_of_events,indent=2))

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

if args.dump:
    with open("dump.ical", 'wb') as f:
        print("Writing", "dump.ical")
        f.write(ical)
    if args.json:
        print("--json will be ingnored for the dump of the original calendar")
ical=None

if args.all:
    if args.ical:
        with open("all.ical", 'wb') as f:
            print("Writing", "all.json")
            all=gcal.to_ical()
            f.write(all)
    if args.json:
        with open("all.json", 'w',encoding='utf8') as f:
            print("Writing", "all.json")
            obj= ComposeCleanListOfObject(headers, events)
            json.dump(obj,f,indent=2)

for h in headers:
    h.subcomponents.clear() # sterilize the header ( or it will pull all the events)

# now dump the selected events ( or everything if there is no selection)
if len(args.sports) == 0:
    args.sports = kind_of_events
    print("No sports selected, all sports will be serialized")
else:
    print("These sports will be serialized", args.sports)

json_merged=[]
cal_merged = Calendar()

if args.merge:
    for h in headers:
        cal_merged.add_component(h)
    for h in headers:
        json_merged.append(ComposeCleanObject(h))          

for kind in args.sports:
    fname=''.join(filter(str.isalnum, kind))
    if kind in events:
        events_of_kind = events[kind]        
        if args.json:            
            obj= ComposeCleanListOfObject(headers, events[kind])
            if args.single:
                with open(fname+ ".json", 'w',encoding='utf8') as f:
                    print("Writing", fname+ ".json")
                    json.dump(obj,f,indent=2)
            if args.merge:
                json_merged = json_merged + obj
        if args.ical:
            if args.merge:
                for e in events_of_kind:
                    cal_merged.add_component(e)
            if args.single:
                with open(fname+ ".ical", 'wb') as f:
                    print("Writing", fname+ ".ical")
                    cal = Calendar()
                    for h in headers:
                        cal.add_component(h)
                    for e in events_of_kind:
                        cal.add_component(e)
                    f.write(cal.to_ical())       
    else:
        print("there is no sport called",kind)


if args.merge:
    if args.json:
        with open("merged.json", 'w',encoding='utf8') as f:
            print("Writing", "merged.json")
            json.dump(json_merged,f,indent=2)    
    if args.ical:
        with open("merged.ical", 'wb') as f:
            print("Writing", "merged.ical")
            f.write(cal_merged.to_ical())    
