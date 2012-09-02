# -*- coding: utf-8 -*-
# dir2tar.py

import optparse
import os
import re
import sys
import tarfile

DIR_SEP_REPLACEMENT = "_____"
SANITISE_RE = re.compile(r"[ ]")    # Potentially add more here

verbose = False

def info(message):
    if verbose:
        printable = message.encode("iso-8859-15", "backslashreplace")
        sys.stdout.buffer.write(printable)
        sys.stdout.write("\n")
        sys.stdout.flush()

def error(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)

def identify_tars(input_dir, output_dir, dirs_in_tarname):
    """
    Walk the input dir from bottom up.
    Store all unique leaves with a tar name based on the number of end directories passed.
    """
    
    tars = {}
    for dirpath, dirnames, filenames in os.walk(input_dir, topdown=False):
        for dirname in dirnames:
            leaf_dir = os.path.join(dirpath, dirname)
            
            stored = False
            for tar_dir in tars.keys():
                if tar_dir.startswith(leaf_dir):
                    stored = True
                    break
            
            if not stored:
                # Strip the input root from tar name consideration
                dirs_string = leaf_dir.replace(input_dir + os.sep, "")
                
                # Replace directory separators with a safe fixed string, then split
                dirs_string = dirs_string.replace(os.sep, DIR_SEP_REPLACEMENT + os.sep)        
                dirs_list = dirs_string.rsplit(os.sep, dirs_in_tarname)
                
                # Use the number of directories requested in the tar name
                requested_dirs_list = dirs_list[-dirs_in_tarname:]
                tar_name = "".join(requested_dirs_list)
                
                tars[leaf_dir] = SANITISE_RE.sub("_", tar_name) + ".tar"
    
    return tars

def create_tars(input_dir, output_dir, tars):
    """
    Takes the input dir and a dictionary of input dir -> tar name.
    Creates a .tar file with a structure that discards the input dir at the output dir.
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    for tar_dir in tars.keys():
        info("Tarring: " + tar_dir)
        output_file = output_dir + os.sep + tars[tar_dir]
        tar_file = tarfile.open(output_file, "w", format=tarfile.PAX_FORMAT)
        tar_file.add(tar_dir, arcname=tar_dir.replace(input_dir + os.sep, ""))
        tar_file.close()
        info("Created: " + output_file)

def main():
    parser = optparse.OptionParser(prog="dir2tar.py")
    parser.add_option("-i", "--input-dir", action="store", dest="input_dir",help="root for conversion.")
    parser.add_option("-o", "--output-dir", action="store", dest="output_dir", help="where to place the tar files.")
    parser.add_option("-d", "--dirs-in-tar-name", action="store", type="int", dest="dirs_in_tarname", default=2, help="directories to include in tar name - [default: %default].")
    parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose", help="provide more information as things happen.")
           
    (options, leftover_args) = parser.parse_args(sys.argv[1:])
    
    if leftover_args or not options.input_dir or not options.output_dir:
        parser.print_help()
        sys.exit(1)
    
    if options.dirs_in_tarname <= 0:
        error("Number of input directories to include in the tar name must be > 1.")
    
    global verbose
    verbose = options.verbose
    
    tars = identify_tars(options.input_dir, options.output_dir, options.dirs_in_tarname)
    
    print("Starting...")    
    info("Input directory: " + options.input_dir)
    info("Directories for tar name: " + str(options.dirs_in_tarname))
    create_tars(options.input_dir, options.output_dir, tars)
    print("...Finished")

if __name__ == "__main__":
    main()
