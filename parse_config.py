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

def get_button_num():
    with open('./config.json','r',encoding='utf-8')as f:  # 加载json配置文件
        config = json.load(f)
    config = dict(config["option"])
    # btn_num = len(list(config.keys()))
    values = []
    for key in config.keys():
        values.append(config[key]['value'])
    return values

if __name__ == "__main__":
    btn_num = get_button_num()
    print(btn_num)