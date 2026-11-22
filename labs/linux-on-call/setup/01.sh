#!/usr/bin/env bash
# Chapter 1: a small folder tree to walk around in, with one hidden file and one deep file.
. /lab/setup/common.sh
fresh 01-why-linux
rm -rf tara answer-*.txt
mkdir -p tara/dishes/dish-1 tara/dishes/dish-2 tara/dishes/dish-3 tara/observations/2026/november/23
cat > tara/README.txt <<'T'
Welcome to the Tara Observatory server.
Tara is a small radio telescope in the hills near Pune: three dishes that listen to the sky every night.
Each dish has a folder in dishes/, and every night's observing plan is in observations/.
T
printf 'Dish 1: online, pointing at the Crab Nebula\n' > tara/dishes/dish-1/status.txt
printf 'Dish 2: online, parked until 23:30\n' > tara/dishes/dish-2/status.txt
printf 'Dish 3: under repair, back on Friday\n' > tara/dishes/dish-3/status.txt
printf 'Diameter: 12 metres\n' > tara/dishes/dish-1/size.txt
printf 'First target tonight: Crab Nebula\nThen: Orion Nebula, Jupiter\n' > tara/observations/2026/november/23/plan.txt
printf 'Welcome, new operator! The secret word is: pulsar\n' > tara/.welcome
