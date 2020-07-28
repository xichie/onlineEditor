from flask import Flask
from flask import request
from flask import render_template, make_response
import os
import subprocess

editor = Flask(__name__)


'''
    打开文件并显示
'''    
@editor.route('/open', methods=['POST'])
def showContent():
    path = request.form['path'] 
    cur_path = request.cookies.get('cur_path') # 获取当前所在的目录
    result = request.cookies.get('result') # 获取result
    # print(os.path.dirname(__file__))  # f:\onlineEditor
    path = os.path.dirname(__file__) + '/'+ cur_path + '/' + path # 获取到文件路径
    # print(path + "-=--------------")
    try:
        with open(path, 'r') as f:
            code = f.read()
    except:
        code = ''
        path = '未找到文件！'
    # print(code,'=====')
    # 保存路径到cookie
    resp = make_response(render_template('editor.html', code=code, path=path, result=result, cur_path=cur_path))   # 设置响应
    resp.set_cookie("path1", path, max_age=3600)
    resp.set_cookie("content", code)
    return resp
 
'''
    保存文件
    利用cookie获取保存文件的名称
'''    
@editor.route('/save', methods=['POST'])   
def saveContent():
    content = request.form['content']  # 获取保存的内容
    path = request.cookies.get('path1') # 获取文件路径
    result = request.cookies.get('result') # 获取result
    # print(content)
    # print(path)
    #newline参数必须加上，防止出现空行
    with open(path, 'w+', newline='') as f:   
        f.writelines(content)
    resp = make_response(render_template('editor.html', code=content, path=path, result=result, cur_path=cur_path))   # 设置响应
    resp.set_cookie("content", content)
    return resp

'''
    执行shell命令
'''    
@editor.route('/execute', methods=['POST'])   
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
    resp = make_response(render_template('editor.html', code=content, path=path, result=result, cur_path=cur_path)) 
    resp.set_cookie("result", result)
    resp.set_cookie("cur_path", cur_path)
    return resp

'''
    主页面
'''
@editor.route('/')
def index():
     resp = make_response(render_template('editor.html', cur_path='files/'))
     resp.set_cookie("cur_path", 'files/') # 当前所在的目录，默认为files
     return resp

def editor():
    return editor

if __name__ == '__main__':
    editor.debug = True # 设置调试模式，生产模式的时候要关掉debug
    editor.run(port=2020)