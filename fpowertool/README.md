# FPowerTool

#### Description
A Function-level Power Profiling Tool

The profile server needs: python, systemtap, papi.
The presentation server needs: easyui, grafana, influxdb.

#### Usage

Example of bodytrack.

Put FPowerTool files into your path of profile application.

1. Count the functions.

```
stap -v tools/functioncount.stp 'process("/home/gwei/parsec-3.0/pkgs/apps/bodytrack/inst/amd64-linux.gcc/bin/bodytrack").function("*")' -c "/home/gwei/parsec-3.0/pkgs/apps/bodytrack/inst/amd64-linux.gcc/bin/bodytrack sequenceB_2 4 2 2000 5 0 1" -o app.funcount
```
2. Generate .stp file to decide which functions to profile.

```
python tools/FPowerTool.genfunctionstp.py app.funcount 5000
```

3. Profile the application.
```
sh FPowerTool.sh /home/gwei/parsec-3.0/pkgs/apps/bodytrack/inst/amd64-linux.gcc/bin/bodytrack sequenceB_2 4 2 2000 5 0 1 
```

Output 2 timestamp file:fpt.t1, fpt.t2
Output rapl data: rapl.log
Output resutlt data: fptfun.log
 

4. Deal with the result.


Post data to InfluxDB.
```
python tools/FPowerTool.postRapl2influx.py rapl.log
python tools/FPowerTool.postTime2influx.py fpt bodytrack 
```

Process the result. Output treegriddata
```
python tools/FPowerTool.processRAPLwithFunc.py fptfun.log rapl.log  treegriddata 
```

5. Presentation.

Open your grafana web site, configure with your influxdb, to see the graphical visualization.

Put treegriddata file into treegrid/ . use a websever, open web browser to see the result.



# Function level perf profiling

* It's based on python, systemtap, perf. 

eg: On centos, you can use 'yum install systemtap'.

* Build the perf profiling scripts. Read the file: buildperfscript/README.md
* Modify the ip address in config.ini

#### Usage

Example of raytrace.

FPowerTool is located at /home/gwei/fpowertool


1. Count the functions. How many times a function is executed.

```
stap -v /home/gwei/fpowertool/tools/functioncount.stp 'process("/home/gwei/parsec-3.0/pkgs/apps/raytrace/inst/amd64-linux.gcc/bin/rtview").function("*")' -c "/home/gwei/parsec-3.0/pkgs/apps/raytrace/inst/amd64-linux.gcc/bin/rtview happy_buddha.obj -automove -nthreads 1 -frames 3 -res 960 540" -o app.funcount
```
2. Generate .stp file to decide which functions to profile.i

The 1st arg is the functions count file from step 1. The functions would be processed, only the run times is lower than the 2nd arg.

```
python /home/gwei/fpowertool/tools/genPerfStp.py app.funcount 200
```

3. Profile the application.

```
sh /home/gwei/fpowertool/perfProfiling.sh /home/gwei/parsec-3.0/pkgs/apps/raytrace/inst/amd64-linux.gcc/bin/rtview happy_buddha.obj -automove -nthreads 1 -frames 3 -res 960 540
```

Output result data, eg: treegridPerfData20200626.1258

4. Show the web presentation of the perf profiling.

    sh /home/gwei/fpowertool/web.sh treegridPerfData20200626.1258 

Open a browser and browse the results. 





