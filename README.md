# Tokyo 2020 olimpycs calendar

**This branch is pinned to the 2020 olimpycs and it's not updated**

This repository contains the calendars for the olimpics divided by sports and a script for updating them.
The calendar is mantained by `anarchycupcake` 

You can find more info on the reddit thread here https://www.reddit.com/r/olympics/comments/mwa3qu/i_made_a_google_calendar_for_all_tokyo_2020_events/

## How to use the script
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