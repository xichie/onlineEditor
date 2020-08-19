#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
import argparse

WORK_PATH = os.getcwd() 
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--workspace", default=WORK_PATH, help="workspace path, dont end with \'\\' or other character, defalut is your current path ")

args = parser.parse_args()
WORK_PATH = args.workspace

subprocess.run("nohup fpowertool/web.sh &", shell=True)
subprocess.run("python ./app.py -w " + WORK_PATH, shell=True)
# os.system("python ./app.py")

