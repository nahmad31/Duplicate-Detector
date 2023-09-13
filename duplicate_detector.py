#CODED BY NA
import sys
import os
import re
import time # For testing purposes
import hashlib
import ubelt
from collections import defaultdict
import xxhash
import math

minimum_file_size = 100000
output_file_name = ""
bytes_to_check = 1000000
filename = ""
whence = -1 # 0 = beg, 1 = mid, 2 = end

def calculate_hash(file_path_str, file_size_num):
	#This xxh64 hash reads from the back of the file
	if (whence == 0): 
		hexstr = ubelt.hash_file(file_path_str, hasher='xx64', maxbytes=min(bytes_to_check, int(file_size_num)) )
		return hexstr
	elif (whence == 1):
		with open(file_path_str, 'rb') as f:
			#return xxhash.xxh3_64(f.read()).hexdigest()
			halfway_point = math.floor(file_size_num/2)
			f.seek(file_size_num/2)
			#return xxhash.xxh64( f.read()[:(halfway_point+bytes_to_check)] ).hexdigest() # does not matter if halfway_point+bytes_to_check overflows
			return xxhash.xxh64( f.read( min(halfway_point, bytes_to_check) ) ).hexdigest() # does not matter if halfway_point+bytes_to_check overflows
	elif (whence == 2):
		with open(file_path_str, 'rb') as f:
			f.seek(-min(bytes_to_check, file_size_num), 2) # User can specify how many bytes to check but this could be bigger than the file itself
			#return xxhash.xxh3_64(f.read()).hexdigest()
			return xxhash.xxh64(f.read()).hexdigest()
	else:
		print("File positioning is set incorrectly")
		exit(1)
	
	#This MD5 is a check, should output same number of files found that are duplicates
	#with open(file_path_str, 'rb') as f:
	  	#f.seek(-4096, 2)
	  	#return hashlib.md5(f.read()).hexdigest()	
	
	#hexstr = ubelt.hash_file(file_path_str, hasher='xx64', maxbytes=10000000) # Old method to use xxh64 hasher, would only take from the beginning
	#return hexstr
	
	#return hashlib.md5(open(file_path_str,'rb').read()).hexdigest() # Old method to take md5sum, would take entire file



filename_input = input("Do you want to create the DU file: type y or n (if n specified then program argument will be taken): ")

if filename_input.lower() == 'n':
	filename = sys.argv[1] # maybe do try catch?
elif filename_input.lower() == 'y':
	directory_to_search = input("Input an absolute path to a directory to be searched: ")
	filename = input("Please input file name: ")
	command = "find " + directory_to_search + " -type f -exec du {} + > " + filename
	command_ret_val = os.system(command)
	if (command_ret_val):
		os.remove(filename)
		exit(1)
else:
	print("Wrong Input Bozo, Try Again")
	exit(1)

print("Remember you can re-use old DU files")



minimum_file_size_input = input("Enter Minimum file size in Kilobytes or type default(100000 KB = 100 MB): ")
if minimum_file_size_input != "default":
	minimum_file_size = int(minimum_file_size_input)
print("You chose files > " + str(minimum_file_size/1000) + " MB")

whence_input = input("Enter from where you want to hash the file: 0 = beginning, 1 = middle, 2 = end: ")
if whence_input.isdigit():
	whence = int(whence_input)

bytes_to_check_input = input("Enter how many Bytes to check of the file or type default(1000000 B = 1 MB): ")
if bytes_to_check_input != "default":
	bytes_to_check = int(bytes_to_check_input)
if (bytes_to_check >= 1000000):
	print("You chose to check " + str(bytes_to_check/1000000) + " MB")
else:
	print("You chose to check " + str(bytes_to_check/1000) + " KB")

output_file_name = input("Enter output file name: ")




start_time = time.time()
print("Searching in file: " + filename)

file = open(filename, "r",) # Will fail if file does not exist

size_to_paths = defaultdict(list)
hash_to_paths = defaultdict(list)


print("Starting Stage 1: Parsing File")
for line in file:
	size_bytes_match = re.search( "^\d*", line) # This is a match object from library re
	size_bytes = line[:size_bytes_match.end()]

	file_path_match = re.search( "\D", line)
	file_path = line[file_path_match.start()+1:-1] # Includes tab in beginning so +1, -1 to get rid of \n

	size_to_paths[size_bytes].append(file_path)



print("Stage 2: Number of duplicates in size")
duplicates_in_size = 0
file_duplicate_in_size = 0
size_duplicates_and_num_files_list = []
for k, v in size_to_paths.items():
	if len(v) > 1:
		#size_duplicates_and_num_files_list.append( (int(k), len(v)) )
		duplicates_in_size += 1
		file_duplicate_in_size += len(v)
#size_duplicates_and_num_files_list.sort(key = lambda x : x[0]) # if 0 then sorted by size, if 1 sorted by number of files
#print(size_duplicates_and_num_files_list)
print("Number of duplicates in sizes are: " + str(duplicates_in_size))
print("Number of duplicate sized files is: " + str(file_duplicate_in_size))



print("Starting Stage 3: Hashing files and associating paths with them")
skipped = 0
for k, v in size_to_paths.items():
	if len(v) > 1 and int(k) > minimum_file_size:
		for path in v:
			if (os.path.exists(path)):
				file_stat = os.stat(path)
				hash_to_paths[calculate_hash(path, file_stat.st_size)].append(path)
			else:
				skipped += 1
				#print("Skipped file: " + path)

print("SKIPPED " + str(skipped) + " FILES (DID NOT EXIST IN DU FILE)")



print("Starting Stage 4: Finding duplicates by hash; Files and sizes associated with folders")
res = []
res_paths_frequency_dict = defaultdict(int) # This is going to tell us how many times a path comes up
res_paths_size_dict = defaultdict(int)
duplicates = 0
total_file_data_waste_bytes = 0 
for k, v in hash_to_paths.items():
	if len(v) > 1: # Multiple paths are associated 
		file_stat = os.stat(v[0])
		res.append( (file_stat.st_size, v) )
		duplicates += len(v)
		total_file_data_waste_bytes += file_stat.st_size * (len(v)-1) # minus 1 because there are n files and n-1 are duplicates
		for path in v:
			res_paths_frequency_dict[ path[:path.rindex('/')+1] ] += 1 # Get folder of file
			res_paths_size_dict[ path[:path.rindex('/')+1] ] += file_stat.st_size/1000000



print("Starting Stage 5: Writing to file")
res.sort(key = lambda x : x[0])
res_paths_frequency_list = sorted(res_paths_frequency_dict.items(), key=lambda item: item[1]) 
res_paths_size_dict_list = sorted(res_paths_size_dict.items(), key=lambda item: item[1])
output_file = open(output_file_name, "w")
for i in res:
	string_int = ""
	unit = ""
	if (i[0] >= 1000000): # If greater than 1 MB
		string_int = str(i[0]/1000000)
		unit = " MB"
	else:
		string_int = str(i[0]/1000)
		unit = " KB"
	output_file.write(string_int + unit + ": \n" + "\n".join(i[1]) + '\n')

output_file.write('\n'*15)

for i, j in res_paths_frequency_list:
    output_file.write( i + '\t' + str(j) + " Files")
    output_file.write('\n')

output_file.write('\n'*15)

for i, j in res_paths_size_dict_list:
    output_file.write( i + '\t' + str(j) + " MB")
    output_file.write('\n')
output_file.close()
	
print("WE GOT THIS MANY FILE DUPLICATES: " + str(duplicates))
print("WE GOT THIS MANY WASTED GIGABYTES: " + str( (total_file_data_waste_bytes/1000000)/1000 ) )
print("--- %s seconds ---" % (time.time() - start_time))






#file_name = line[line.rindex('/')+1:-1] # Getting last right index of '/' and then -1 for getting rid of \n

''' find /mnt/nas/Seven_NAS/AB/Seven Libraries/ -type f -exec du {} + > text.txt
#file_stat = os.stat(file_path) # C chads keep winning
#print("Size of file " + file_name + ": ", (file_stat.st_size / 1024)/1024 , "MB")
'''
# Only problem is du file wont have new files, but you can updates du file after some time
