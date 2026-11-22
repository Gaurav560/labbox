#!/usr/bin/env bash
# Chapter 2: a messy downloads folder to tidy, and a targets folder to back up.
. /lab/setup/common.sh
fresh 02-files
rm -rf downloads targets targets-backup
mkdir -p downloads targets/special
for d in 03 07 12 18 21; do printf 'Electricity bill for the dishes, 2026-11-%s\n' "$d" > "downloads/invoice-2026-11-$d.pdf"; done
printf 'A map of the stars visible from Pune\n' > "downloads/star chart.pdf"
for n in 1 2 3 4; do printf 'photo of the sky, night %s\n' "$n" > "downloads/sky-$n.jpg"; done
printf 'half-downloaded\n' > downloads/upload.tmp
printf 'cache\n' > downloads/cache-1.tmp
printf 'cache\n' > downloads/cache-2.tmp
printf 'Order a new cable for dish 3 on Monday.\n' > downloads/notes.txt
printf 'Crab Nebula 21:00\nOrion Nebula 23:30\nJupiter 02:15\n' > targets/tonight.txt
printf 'Mon Andromeda Galaxy\nWed Saturn\nFri Pleiades\n' > targets/this-week.txt
printf 'Lunar eclipse: watch the Moon from 22:10\n' > targets/special/eclipse.txt
