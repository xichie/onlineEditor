# coding=utf-8
import sys

def process(argv):
	print('用python执行。参数1：函数统计文件,参数2：次数，小于这个的才会被输出。文件中格式是：  函数名 次数' )
	print('要处理的文件名：'+argv[0])
	print('小于这个次数的函数才会被处理：'+argv[1])
	print("Using python to execute this script. \narg1 is the function count file. arg2 is a number, the function will processed when the run count is lower than arg2.")
	with open(argv[0],'r') as myFile,  open('fnperf.stp','w') as f:
		f.writelines(['''#! /usr/bin/env stap
probe perf.hw.branch_instructions.$1.counter("branch_instructions"){} 
probe perf.hw.branch_misses.$1.counter("branch_misses"){} 
probe perf.hw.cache_misses.$1.counter("cache_misses"){} 
probe perf.hw.cache_references.$1.counter("cache_references"){} 
probe perf.hw.cpu_cycles.$1.counter("cpu_cycles"){} 
probe perf.hw.instructions.$1.counter("instructions"){} 
probe perf.sw.alignment_faults.$1.counter("alignment_faults"){} 
probe perf.sw.context_switches.$1.counter("context_switches"){} 
probe perf.sw.cpu_clock.$1.counter("cpu_clock"){} 
probe perf.sw.cpu_migrations.$1.counter("cpu_migrations"){} 
probe perf.sw.emulation_faults.$1.counter("emulation_faults"){} 
probe perf.sw.page_faults.$1.counter("page_faults"){} 
probe perf.sw.page_faults_maj.$1.counter("page_faults_maj"){} 
probe perf.sw.page_faults_min.$1.counter("page_faults_min"){} 
probe perf.sw.task_clock.$1.counter("task_clock"){} 

		\n'''])

		line = myFile.readline()
		error=0
		while line:
			#print(line)
			s=str(line).split(' ')
			try:
				if int(s[1])< int(argv[1]) and s[0]!='_start':

					f.write('probe $1.function("'+s[0]+'").call{  printf("'+s[0]+',1,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d \\n", @perf("branch_instructions"),@perf("branch_misses"),@perf("cache_misses"),@perf("cache_references"),@perf("cpu_cycles"),@perf("instructions"),@perf("alignment_faults"),@perf("context_switches"),@perf("cpu_clock"),@perf("cpu_migrations"),@perf("emulation_faults"),@perf("page_faults"),@perf("page_faults_maj"),@perf("page_faults_min"),@perf("task_clock") ); }\n')
					f.write('probe $1.function("'+s[0]+'").return{  printf("'+s[0]+',2,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d \\n", @perf("branch_instructions"),@perf("branch_misses"),@perf("cache_misses"),@perf("cache_references"),@perf("cpu_cycles"),@perf("instructions"),@perf("alignment_faults"),@perf("context_switches"),@perf("cpu_clock"),@perf("cpu_migrations"),@perf("emulation_faults"),@perf("page_faults"),@perf("page_faults_maj"),@perf("page_faults_min"),@perf("task_clock") ); }\n')

					f.write('\n')
			except:
				error=1
				print("error:\n"+str(line))
			line = myFile.readline()
		if error ==1 :
			print('---------')
			print('你可能需要手动添加error信息中的函数，可以使用*号作为通配符')
			print('There are some errors with some funcitons. You can use * to deal with it.')
			print('''eg:
error:__find<__gnu_cxx::__normal_iterator<ISG::Node**, std::vector<ISG::Node*> >, ISG::Node*> 6
error:operator<< <std::char_traits<char> > 5probe $1.function("__find*").call{ trace(1, $$parms) }\n
you may wanna add the two functions by manual. something similar with following:
probe $1.function("__find*").call { ...copy from the fnperf.stp file...}
probe $1.function("__find*").return { ......}
probe $1.function("operator*").call{ ...... }
probe $1.function("operator*").return { ......}
---------
''')
	print('Finished. check fnperf.stp file.')


if __name__ == '__main__':
	process(sys.argv[1:])
