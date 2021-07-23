.\distiller.py -d

mkdir single_sports
cd single_sports
..\distiller.py -s -i
cd ..

mkdir sports_by_category
cd sports_by_category
..\distiller.py -m "Boxing" "Fencing" "Judo" "Karate" "Taekwondo" "Wrestling"
move merged.ical MartialArts.ical
cd ..