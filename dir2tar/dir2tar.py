# dir2tar.py

import optparse
import os
import sys
import tarfile

verbose = False

def info(message):
    if verbose:
        print(message)

def identify_tars(input_dir, output_dir):
    """
    Walk the input dir from bottom up.
    Store all unique leaves with a tar name based on the last two dirs.
    """
    
    tars = {}
    for dirpath, dirnames, filenames in os.walk(input_dir, topdown=False):
        for dirname in dirnames:
            leaf_dir = os.path.join(dirpath, dirname)
            
            stored = False
            for tar_dir in tars.keys():
                if tar_dir.startswith(leaf_dir):
                    stored = True
            
            if not stored:
                tar_name = leaf_dir.replace(input_dir + os.sep, "")
                tar_name = tar_name.replace(os.sep, "___")
                tar_name = output_dir + os.sep + tar_name + ".tar"
                tars[leaf_dir] = tar_name
    
    return tars

def create_tars(input_dir, tars):
    """
    Takes the input dir and a dictionary of input_dir -> output_tar.
    Creates a .tar file with a structure that discards the input dir.
    """
    
    print("Starting...")
    
    for tar_dir in tars.keys():
        info("Processing: " + tar_dir)
        tar_file = tarfile.open(tars[tar_dir], "w")
        tar_file.add(tar_dir, arcname=tar_dir.replace(input_dir + os.sep, ""))
        tar_file.close()
        info("Created:    " + tars[tar_dir])
    
    print("...Finished")

def main():
    parser = optparse.OptionParser(prog="dir2tar.py")
    parser.add_option("-i", "--input-dir", action="store", dest="input_dir",help="root for conversion.")
    parser.add_option("-o", "--output-dir", action="store", dest="output_dir", help="where to place the tar files.")
    parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose", help="provide more information as things happen.")
           
    (options, leftover_args) = parser.parse_args(sys.argv[1:])
    
    if leftover_args or not options.input_dir or not options.output_dir:
        parser.print_help()
        sys.exit(1)
    
    global verbose
    verbose = options.verbose
    
    tars = identify_tars(options.input_dir, options.output_dir)
    create_tars(options.input_dir, tars)

if __name__ == "__main__":
    main()
