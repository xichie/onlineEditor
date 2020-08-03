import os
import json
from flask import Flask, render_template, make_response, request, Response,jsonify
import random

id = 2
app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")

def get_pathTree(path, jsonData, parentId):
    global id
    paths = os.listdir(path)
    for i, item in enumerate(paths):
        sub_path = os.path.join(path, item)
        # 创建节点
        node = {
            'id': id,
            "title": item,
            "parentId": parentId,
            "children": [],
        }
        id += 1
        if os.path.isdir(sub_path): # 如果是子目录，则添加子目录节点，递归遍历该节点下的文件和目录
            jsonData.append(node)
            get_pathTree(sub_path, node['children'], node['id'])
        else:                                   # 如果是文件，则直接添加文件节点
            node['basicData'] = sub_path
            jsonData.append(node)
            
# if __name__ == '__main__':
    # print(jsonData["data"])
    # with open('./json.txt', 'w') as f:
    #     f.write(jsonData["data"])


@app.route("/")
def index():
    path = './files'
    jsonData = {
        "data": [
            {"id":"1","title": path.split('/')[-1], "parentId":"0", "children":[]},
        ]
    }
    get_pathTree(path, jsonData['data'][0]['children'], parentId='0')
    res_json = json.dumps(jsonData)
    print(jsonData)
    resp = make_response(render_template('test.html', data=res_json))
    # resp.set_cookie("dataTree", jsonify(jsonData))
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug="true")