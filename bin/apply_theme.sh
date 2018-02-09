#!/bin/bash

THEME=`echo $FRAMEWORK_NAME | tr '[:upper:]' '[:lower:]'`

cp ./static/scss/new/themes/_$THEME.scss ./static/scss/new/base/_variables.scss
