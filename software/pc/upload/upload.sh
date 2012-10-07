#!/bin/bash
LOGIN=thibaut
DOSSIER_DESTINATION=/home/thibaut/intech-2013/TEST/

echo "Adresse IP de la BeagleBoard : "
read DOSSIER

rsync -e ssh --delete-after --exclude-from exclusion.txt -az ../ "$LOGIN"@"$DOSSIER":"$DOSSIER_DESTINATION"