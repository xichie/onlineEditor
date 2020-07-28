#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
from flask import Flask, render_template, make_response, request, Response
from flask_socketio import SocketIO
import pty
import os
import subprocess
import select
import termios
import struct
import fcntl
import shlex
import editor
import json

__version__ = "0.4.0.1"

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = "secret!"
app.config["fd"] = None
# app.config["fd"] = True
app.config["child_pid"] = None
socketio = SocketIO(app)


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
    # return render_template("index.html")
    resp = make_response(render_template('index.html', cur_path='./files/'))
    resp.set_cookie("cur_path", './files/') # 当前所在的目录，默认为files
    return resp


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if app.config["fd"]:
        print("writing to ptd: %s" % data["input"])
        #print(app.config["fd"])
        #os.write(app.config["fd"], 'ls\n'.encode() )
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
    打开文件并显示
'''    
@app.route('/open', methods=['POST'])
def showContent():
    path = request.form['path'] 
    # path = request.args.get("path")
    cur_path = request.cookies.get('cur_path') # 获取当前所在的目录
    result = request.cookies.get('result') # 获取result
    # print(os.path.dirname(__file__))  # f:\onlineEditor
    path = os.path.dirname(__file__) + cur_path + '/' + path # 获取到文件路径
    # print(path + "-=--------------")
    try:
        with open(path, 'r') as f:
            code = f.read()
    except:
        code = ''
        path = '未找到文件！'
    # print(code,'=====')
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
    执行shell命令
@app.route('/execute', methods=['POST'])   
def execute():
    content = request.cookies.get('content')  # 获取文件的内容
    path = request.cookies.get('path1') # 获取文件路径
    shell = request.form['shell']  # 获取shell命令
    cur_path = request.cookies.get('cur_path') # 获取当前所在的目录
    
    if 'cd' in shell.split(' ')[0]:         # 如果shell命令为cd，则切换当前目录
        if shell.split(' ')[-1] == '.':
            cur_path = '/'.join(cur_path.split('/')[:-1])
        else:
            cur_path +=  shell.split(' ')[-1].strip() + '/'  
        result = '当前目录为：' + cur_path
    else:
        result = subprocess.check_output(shell, cwd=cur_path, shell=True) # 在files目录下执行shell
        result = str(result, encoding = "GB2312")  # shell的结果解码
    resp = make_response(render_template('index.html', code=content, path=path, result=result, cur_path=cur_path)) 
    resp.set_cookie("result", result)
    resp.set_cookie("cur_path", cur_path)
    return resp        
'''

def main():
    parser = argparse.ArgumentParser(
        description=(
            "A fully functional terminal in your browser. "
            "https://github.com/cs01/pyxterm.js"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
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
    if args.version:
        print(__version__)
        exit(0)
    print("serving on http://127.0.0.1:{args.port}")
    app.config["cmd"] = [args.command] + shlex.split(args.cmd_args)
    socketio.run(app, host='0.0.0.0', debug=args.debug, port=args.port)


if __name__ == "__main__":
    main()
