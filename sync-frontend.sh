#!/bin/bash
echo recuerda: primero ng build en fse-proyecto-frontend
echo luego regresas aca
rsync -avz --delete ~/fse/fse-proyecto/frontend/dist/frontend/browser/ rpi:/var/www/fse/
