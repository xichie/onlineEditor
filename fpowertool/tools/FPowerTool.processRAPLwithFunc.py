#coding=utf-8
'''
处理结果，计算函数的能耗

函数时间信息
1534238761646464 1 __libc_csu_init
1534238761646475 1 _init
1534238761646478 -1 _init
1534238761646480 1 frame_dummy
1534238761646483 1 register_tm_clones
1534238761646485 -1 register_tm_clones
1534238761646487 -1 frame_dummy

power数据
0 begin-------
1534238755592090 p0=22766113 p1=21606445 d0=2990722 d1=3036499
1534238755593453 p0=21789550 p1=23132324 d0=4180908 d1=4180908
'''



'''
2019年1月6日 23:43:58
处理函数重名的情况，之前的未考虑，导致有问题

1546786976528815 1 build
1546786976528820 1 get
1546786976528861 -1 get
1546786976528864 1 build
1546786976528868 1 getAllPrimitiveBounds
1546786976528870 -1 getAllPrimitiveBounds
1546786976528872 1 numPrimitives
1546786976528875 -1 numPrimitives
1546786976528878 1 reserve
1546786976528895 -1 reserve
1546786977514705 1 doneWithAllPrimitiveBounds
1546786977514713 -1 doneWithAllPrimitiveBounds
1546786977514715 -1 build
1546786977514717 -1 build
1546786977515004 -1 buildSpatialIndexStructure
'''
#Python strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列。
import time
import linecache
import sys

def main(argv): #argv[1]
	print '参数1是函数时间信息的文件名，2是rapl数据',argv[0],argv[1]
	funSumPowerList=[]
	funPowerList=[]
	treegriddataList=[]
	
	funTimeData=linecache.getlines(argv[0])
	raplData=linecache.getlines(argv[1])
	print len(raplData)
	#lenfunTimeData=len(funTimeData)
	index=0
	for i in range( 1,(len(funTimeData)+1) ):
		#i, 1~ len-1， 0行是空的
		tmpline=linecache.getline(argv[0],i)
		
		tmpline=tmpline.strip()
		ft1=ft2=0
		if tmpline.split(' ')[1]=='1':
			#print(i,tmpline)
			
			ft1=int(tmpline.split(' ')[0])
			funname=tmpline.split(' ')[2]
			tmp=0
			chongming=0
			#寻找函数的结束时间
			#linecache里没第0行，所以这里的行数要注意下，for里是有第0行的
			for j in funTimeData:
				if tmp<=(i-1):
					tmp=tmp+1
					continue
				if  j.split(' ')[1]=='1': #不是1就是-1啊
					if j.split(' ')[2].strip()== funname:
						chongming=chongming+1
					tmp=tmp+1
				elif j.split(' ')[2].strip()== funname:
					if chongming==0:
						ft2=int(j.split(' ')[0])
						#print j
						break
					else:
						chongming=chongming-1
						continue

			pt11=pt12=pt21=pt22=0
			tmptime1=tmptime2=0
			for k in raplData:
				tmptime2=int(k.split(' ')[0])
				if ft1>=tmptime1 and ft1<=tmptime2:
					pt11=tmptime1
					pt12=tmptime2
				if ft2>=tmptime1 and ft2<=tmptime2:
					pt21=tmptime1
					pt22=tmptime2
					break
				tmptime1=int(k.split(' ')[0])

			#print ft1,ft2,funname,pt11,pt12,pt21,pt22

			#计算i行函数的能耗
			p0=p1=d0=d1=0.0
			if(pt11==pt21 and pt12==pt22):
				for m in raplData:
					tmpt=int(m.split(' ')[0])
					#1534238755593453 p0=21789550 p1=23132324 d0=4180908 d1=4180908
					if tmpt==pt22:
						tmpdata=pdataconvert(m.strip())
						#print m
						p0=tmpdata[0]*1.0*(ft2-ft1)/(pt22-pt21)
						p1=tmpdata[1]*1.0*(ft2-ft1)/(pt22-pt21)
						d0=tmpdata[2]*1.0*(ft2-ft1)/(pt22-pt21)
						d1=tmpdata[3]*1.0*(ft2-ft1)/(pt22-pt21)
						break
			else:
				tmptime1=tmptime2=0
				for m in raplData:
					tmpt=int(m.split(' ')[0])
					if tmpt==pt12:
						#print m
						tmpdata=pdataconvert(m.strip())
						p0=tmpdata[0]*1.0*(pt12-ft1)/(pt12-pt11)
						p1=tmpdata[1]*1.0*(pt12-ft1)/(pt12-pt11)
						d0=tmpdata[2]*1.0*(pt12-ft1)/(pt12-pt11)
						d1=tmpdata[3]*1.0*(pt12-ft1)/(pt12-pt11)
						continue
					if tmpt>pt12 and tmpt<pt21:
						#print m
						tmpdata=pdataconvert(m.strip())
						p0+=tmpdata[0]*1.0
						p1+=tmpdata[1]*1.0
						d0+=tmpdata[2]*1.0
						d1+=tmpdata[3]*1.0
						continue
					if tmpt==pt22:
						#print m
						tmpdata=pdataconvert(m.strip())
						p0+=tmpdata[0]*1.0*(ft2-pt21)/(pt22-pt21)
						p1+=tmpdata[1]*1.0*(ft2-pt21)/(pt22-pt21)
						d0+=tmpdata[2]*1.0*(ft2-pt21)/(pt22-pt21)
						d1+=tmpdata[3]*1.0*(ft2-pt21)/(pt22-pt21)
						break
			#函数的能耗 或者在这里追加到一个文件，次数也是很多的
			#funPowerList.append([funname,p0,p1,d0,d1])
			#print funname,p0,p1,d0,d1
			funPowerList.append([str(ft1),str(ft2),funname,str(p0),str(p1),str(d0),str(d1)])
			#funPowerList.append([str(ft1),str(ft2),funname,str(p0),str(p1),str(d0),str(d1)])
			#treegriddataList
			#treegriddataList.append()
			#print funPowerList
	#将结果保存到文件
	print("将结果保存到文件,文件名为 参数3.funpower.时间 \n")
	currenttime = time.localtime(time.time())
	fw = open(argv[2]+".funpower"+str(currenttime.tm_mon)+str(currenttime.tm_mday)+str(currenttime.tm_hour)+str(currenttime.tm_min) ,'w')
	#fw.writelines(['#!/usr/bin/env sh\n']) 
	for i in funPowerList:
		#[funname,p0,p1,d0,d1]
		#fw.writelines([i,'\n'])
		fw.writelines([i[0],',',i[1],',',i[2],',',i[3],',',i[4],',',i[5],',',i[6]])
		fw.writelines(['\n'])
	fw.close()

	print('生成treegrid data...')
	'''
	name_age={"da_wang":27,"liu":26,"kong":12}用dict表示刚好,但注意dict中是单引号
	
	{"id":11,"name":"fun1","power":"111,1111,2222,333","_parentId":0},
	{"id":0,"name":"functions"},
	{"id":11,"region":"Albin","f1":2000,"f2":1800,"f3":1903,"f4":2183,"f5":2133,"f6":1923,"f7":2018,"f8":1838,"_parentId":1},
	{"id":2,"region":"Washington"},
	{"id":21,"region":"Bellingham","f1":2000,"f2":1800,"f3":1903,"f4":2183,"f5":2133,"f6":1923,"f7":2018,"f8":1838,"_parentId":2},
	{"id":24,"region":"Monroe","f1":2000,"f2":1800,"f3":1903,"f4":2183,"f5":2133,"f6":1923,"f7":2018,"f8":1838,"_parentId":2}
	],"footer":[
	{"region":"Total","f1":14000,"f2":12600,"f3":13321,"f4":15281,"f5":14931,"f6":13461,"f7":14126,"f8":12866}
]}
	'''
	filename=argv[2]+".treegrid"+str(currenttime.tm_mon)+str(currenttime.tm_mday)+str(currenttime.tm_hour)+str(currenttime.tm_min)
	fw = open( filename,'w')
	print('save to '+filename)
	fw.writelines(['''{"total":'''+str(len(funPowerList))+''',"rows":['''])
	fw.writelines(['\n'])

	tsum=p0sum=p1sum=d0sum=d1sum=0.0  #计算总和
	funPowerList2=funPowerList
	for i,v in enumerate(funPowerList):
		parentID=0
		#print i,v #i从0开始
		#[time1,time2,funname,p0,p1,d0,d1]
		ftime1=int(v[0])
		ftime2=int(v[1])
		#for i2,v2 in enumerate(funPowerList[(i+1):]): # i2也是从0开始，这样就不知道行数了
		for i2,v2 in enumerate(funPowerList):
			ftime3=int(v2[0])
			ftime4=int(v2[1])
			if ftime3<ftime1 and ftime2<ftime4:
				parentID=i2+1
				continue
			if ftime2<ftime3:
				break
		if parentID!=0:
			#string='''{'id':'''+ str(i+1)+ ''','name':'''+v[2]+''','p0':'''+i[3]+''','p1':'''+i[4]+''','d0':'''+i[5]+''','d1':'''+i[6]+''','_parentId':'''+str(parentID)+'}'
			#fw.writelines([str({'id':i+1,'name':v[2],'p0':i[3],'p1':i[4],'d0':i[5],'d1':i[6],'_parentId':parentID})])
			#tmpdict={'id':(i+1),'name':v[2],'p0':v[3],'p1':v[4],'d0':v[5],'d1':v[6],'_parentId':parentID}
			tmpdict={'id':(i+1),'name':v[2],'t':time2kexue(ftime2-ftime1),'p0':'%.3e'%(float(v[3])),'p1':'%.3e'%(float(v[4])),'d0':'%.3e'%(float(v[5])),'d1':'%.3e'%(float(v[6])),'_parentId':parentID}
		else:
			p0sum+=float(v[3])
			p1sum+=float(v[4])
			d0sum+=float(v[5])
			d1sum+=float(v[6])
			tsum+=float(ftime2-ftime1)
			tmpdict={'id':(i+1),'name':v[2],'t':time2kexue(ftime2-ftime1),'p0':'%.3e'%(float(v[3])),'p1':'%.3e'%(float(v[4])),'d0':'%.3e'%(float(v[5])),'d1':'%.3e'%(float(v[6]))}
		#.replace('\'','"')单引号的json格式不识别，应该为双引号
		fw.writelines([str(tmpdict).replace('\'','"'),'\n']) 
		if i+1 != len(funPowerList):
			fw.writelines([','])
		#treegriddataList.append()

	#],"footer":[{"name":"Total Energy:","persons":7,"iconCls":"icon-sum"} ]}
	#fw.writelines([']}']) #这是不加总和的
	print('{"name":"Total Energy:","p0":"%.f","p1":"%.f","d0":"%.f","d1":"%.f"} ]}'%(float(p0sum),float(p1sum),float(d0sum),float(d1sum),))
	fw.writelines(['],"footer":[{"name":"Total Energy:","t":"%s","p0":"%.3e","p1":"%.3e","d0":"%.3e","d1":"%.3e"} ]}'%(time2kexue(tsum),float(p0sum),float(p1sum),float(d0sum),float(d1sum),)])
	fw.close()
	print('over.')
	#生成easyui的网页，放在
	#easyuihome='/home/gwei/easyuiwebtreegrid/'

def time2kexue(t):
	#1546786976 528872 时间差,将一个时间返回us，如果大于1w就用科学计数
	t=t
	if t>=10000:
		return '%.2e'%t
	return str(t)


def pdataconvert(p):
	#print p
	#p0=21789550 p1=23132324 d0=4180908 d1=4180908
	tmp=p.split(' ')
	return [int(tmp[1].split('=')[1]),int(tmp[2].split('=')[1]),int(tmp[3].split('=')[1]),int(tmp[4].split('=')[1])]



if __name__ == "__main__":
	print("参数3 保存结果的文件名加个funpower >>log.txt")
	main(sys.argv[1:]) #参数0是文件名，不传入下面的函数

	
	
'''
linecache.getlines(filename)
从名为filename的文件中得到全部内容，输出为列表格式，以文件每行为列表中的一个元素,并以linenum-1为元素在列表中的位置存储

linecache.getline(filename,lineno)
从名为filename的文件中得到第lineno行。这个函数从不会抛出一个异常–产生错误时它将返回”（换行符将包含在找到的行里）。
如果文件没有找到，这个函数将会在sys.path搜索。

>>> import time()
>>> print time.time()
1518068251.33
>>> time = time.localtime(time.time())
>>> print time
time.struct_time(tm_year=2018, tm_mon=2, tm_mday=8, tm_hour=13, tm_min=37, tm_sec=31, tm_wday=3, tm_yday=39, tm_isdst=0)
>>> print time.tm_year
2018
>>> print time.tm_mon

'''