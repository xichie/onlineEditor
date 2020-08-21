#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
from flask import Flask, render_template, make_response, request, Response, jsonify, session
from flask_socketio import SocketIO
import pty
import os
import subprocess
import select
import termios
import struct
import fcntl
import shlex
import json
import configparser

__version__ = "0.4.0.1"

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = "secret!"
app.config["fd"] = None
# app.config["fd"] = True
app.config["child_pid"] = None
socketio = SocketIO(app)
id = 2   # 文件树节点id

WORK_PATH = os.getcwd()    # 末尾不能有"/"

'''
    terminal size
'''
def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output():
    max_read_bytes = 1024 * 20
    while True:
        # socketio.sleep(0.01)
        socketio.sleep(1)
        #print(app.config["cmd"])
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = os.read(app.config["fd"], max_read_bytes).decode()
                #print(  output   )
                socketio.emit("pty-output", {"output": output}, namespace="/pty")

@app.route("/")
def index():
    global WORK_PATH
    jsonData = {
        "data": [
            {"id":"1","title": os.path.split(WORK_PATH)[1], "parentId":"0", "children":[]},
        ]
    }
    get_pathTree(WORK_PATH, jsonData['data'][0]['children'], parentId='0')
    res_json = json.dumps(jsonData)
    try:
        selects = get_config()   # 获取按钮的名称
    except:
        resp = make_response(render_template('index2.html', cur_path=WORK_PATH, data=res_json, error="配置错误!"))
        return resp
    resp = make_response(render_template('index2.html', cur_path=WORK_PATH, data=res_json, selects=json.dumps(selects)))
    resp.set_cookie("cur_path", WORK_PATH) # 当前所在的目录，默认为files
    # resp.set_cookie("btn_val", ",".join(btn_val))
    return resp


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if app.config["fd"]:
        print("writing to ptd: %s" % data["input"])
        #print(app.config["fd"])
        # os.write(app.config["fd"], 'ls\n'.encode() )     # 本行代码可以再webshell里运行ls命令
        os.write(app.config["fd"], data["input"].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    if app.config["fd"]:
        set_winsize(app.config["fd"], data["rows"], data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""
    if app.config["child_pid"]:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        # this is the parent process fork.
        # store child fd and pid
        app.config["fd"] = fd
        app.config["child_pid"] = child_pid
        set_winsize(fd, 50, 50)
        cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
        print("child pid is", child_pid)
        print(
            "starting background task with command `{cmd}` to continously read "
            "and forward pty output to client"
        )
        socketio.start_background_task(target=read_and_forward_pty_output)
        print("task started")

'''
    新建文件
'''
@app.route('/create', methods=['POST'])
def createFile():
    file_path = request.form['file_path'] 
    if(file_path is None or file_path.strip() == ''):
        print(file_path)
    content = request.form['content']
    with open(file_path, "w+", newline='') as f:
        f.writelines(content)
    data = {
        'code': content,
        'file_path': file_path,
    }
    resp = make_response(data)
    resp.set_cookie("file_path", file_path, max_age=3600)
    return resp

'''
    打开文件并显示
'''    
@app.route('/open', methods=['POST'])
def showContent():
    path = request.form['path'] 
    cur_path = request.cookies.get('cur_path') # 获取当前所在的目录
    result = request.cookies.get('result') # 获取result
    try:
        with open(path, 'r') as f:
            code = f.read()
    except:
        code = ''
        path = '未找到文件！'
    # 保存路径到cookie
    data = {
        'code': code,
        'file_path': path,
        'result': result,
        'cur_path': cur_path,
    }
    resp = make_response(data)
    resp.set_cookie("file_path", path, max_age=3600)
    return resp
 
'''
    保存文件
    利用cookie获取保存文件的名称
'''    
@app.route('/save', methods=['POST'])   
def saveContent():
    content = request.form['content']  # 获取保存的内容
    file_path = request.cookies.get('file_path') # 获取文件路径
    result = request.cookies.get('result') # 获取result
    #newline参数必须加上，防止出现空行
    with open(file_path, 'w+', newline='') as f:   
        f.writelines(content)

    data = {
        "file_path":file_path
    }
    resp = make_response(data)
    return resp

'''
    该方法可以令文件树优先显示文件夹
'''
def getFileNames(path):
    for (root, dirs, files) in os.walk(path):
        return dirs + files
'''
    获取指定目录下的文件树json数据
'''
def get_pathTree(path, jsonData, parentId):
    global id
    paths = getFileNames(path)    # 优先显示文件夹
    # print(paths)
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

"""
    执行自定义命令
"""
@app.route('/execute', methods=['post'])
def execute():
    try:
        config = configparser.ConfigParser()
        d = {}
        config.read("config.ini") 

        option = request.form['opt_val']   # 获取按钮
        section = request.form['section']
        print(option)
        print(section)
        shell = config[section][option]  # 根据id找到对应的命令
        shell += "\n"
        print(shell)
        # result = subprocess.check_output(shell, shell=True) # 执行shell， 默认为当前的工作目录
        # result = str(result, encoding = "GB2312")  # shell的结果解码
        os.write(app.config["fd"], shell.encode())   # 在webshell中执行命令，并展示结果
        return "success!"
    except:
        return "执行异常"

'''
    显示自定义命令的执行结果
''' 
@app.route('/result', methods=['post'])
def showResult():
    form = dict(request.form)
    result = form['result']
    resp = make_response(render_template('result.html', result=result))
    return resp

'''
    获取配置文件信息
'''
def get_config():
    config = configparser.ConfigParser()
    d = {}
    config.read("config.ini")
    sections = config.sections()
    for section in sections:
        options = dict(config[section])
        d[section] = options
    return d

'''
    程序入口函数
'''
def main():
    global WORK_PATH
    parser = argparse.ArgumentParser(
        description=(
            "A fully functional terminal in your browser. "
            "https://github.com/cs01/pyxterm.js"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-w", "--workspace", default=WORK_PATH, help="workspace path, dont end with \'\\' or other character, defalut is your current path ")
    parser.add_argument("--host", default='127.0.0.1', help="ip address")
    parser.add_argument("-p", "--port", default=2000, help="port to run server on")
    parser.add_argument("--debug", action="store_true", help="debug the server")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    parser.add_argument(
        "--command", default="bash", help="Command to run in the terminal"
    )
    parser.add_argument(
        "--cmd-args",
        default="",
        help="arguments to pass to command (i.e. --cmd-args='arg1 arg2 --flag')",
    )
    args = parser.parse_args()
    WORK_PATH = args.workspace
    if args.version:
        print(__version__)
        exit(0)

    config = configparser.ConfigParser()        
    config.read("config.ini")
    
    # print("serving on http://" + config['HOST']['ADDRESS'] + ":" + str(args.port))
    print("serving on http://" + str(args.host) + ":" + str(args.port))
    app.config["cmd"] = [args.command] + shlex.split(args.cmd_args)
    socketio.run(app, host='0.0.0.0', debug=args.debug, port=int(args.port))
    
if __name__ == "__main__":
    main()
