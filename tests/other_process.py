import sys
import os
import random

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
    
    
def file_len(file):
    initial = file.tell()
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(initial)
    return size

def run():
    rand_seed = None
    stderr_filename = None
    stdout_filename = None
    
    if len(sys.argv) >= 4:
        rand_seed = int(sys.argv[3])
    
    if len(sys.argv) >= 3:
        stderr_filename = sys.argv[2]
        
    if len(sys.argv) >= 2:
        stdout_filename = sys.argv[1]
        
    stdout_file = None
    stderr_file = None
    
    if stdout_filename:
        stdout_file = open(stdout_filename, 'r')
    else:
        stdout_file = StringIO()
        
    if stderr_filename:
        stderr_file = open(stderr_filename, 'r')
    else:
        stderr_file = StringIO()
        
    if not rand_seed:
        sys.stdout.write(stdout_file.read())
        sys.stderr.write(stderr_file.read())
    else:
        random.seed(rand_seed)
        stdout_len = file_len(stdout_file)
        
        stdout_eof = False
        stderr_eof = False
        
        while not stdout_eof or not stderr_eof:
            if not stdout_eof:
                r = random.randrange(stdout_len / 4)
                data = stdout_file.read(r)
                if len(data) < r:
                    stdout_eof = True
                sys.stdout.write(data)
            if not stderr_eof:
                r = random.randrange(stdout_len / 4)
                data = stderr_file.read(r)
                if len(data) < r:
                    stderr_eof = True
                sys.stderr.write(data)
    
if __name__ == '__main__':
    run()
    
