#!/bin/bash

#Hola, mundo!

read -p "Hola Mundo!, Escribe tu nombre porfavor: " name
echo -n "Hola, ¿Tú eres $name ? [y/n]: "
read -r ans

if [[ "$ans" = "y" ]]; then
        echo "Un placer conocernos $name"
else
        echo "Una disculpa, me confundí de persona :("
fi
