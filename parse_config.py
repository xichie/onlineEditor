#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
    <p id="demo">单击按钮创建有文本的按钮</p>
    <button onclick="myFunction()">点我</button>
        <select id="myselect">
            <option style:"display:none",value:"default">菜单</option> 
        </select>
    <script>
    function myFunction(){
        //可以用cookie或session从后台获取配置文件中的数据，目前只需要option的名称
        var btn =document.getElementById("myselect");
        var t=document.createElement("option");
        t.innerHTML="111";
        btn.appendChild(t);
        var t=document.createElement("option");
        t.innerHTML="123";
        btn.appendChild(t);
    };
'''


import json
import configparser

def get_config():
    config = configparser.ConfigParser()
    d = {}
    config.read("config.ini")
    sections = config.sections()
    for section in sections:
        options = dict(config[section])
        d[section] = options
    return d

if __name__ == "__main__":
   d = get_config()
#    print(d)
   import socket
   hostname=socket.gethostname()
   #获取本机IP
   ip=socket.gethostbyname(hostname)
   print(ip)
