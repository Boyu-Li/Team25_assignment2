# coding: utf-8

import re,io,sys
import os

if __name__ == '__main__':
    fileHandle1 = open ( sys.argv[1], 'w' )
    a = '[Service]\nEnvironment="HTTP_PROXY=http://wwwproxy.unimelb.edu.au:8000"'
    fileHandle1.write (a) 
    fileHandle1.close()
    fileHandle2 = open ( sys.argv[2], 'w' )
    a = '[Service]\nEnvironment="HTTP_PROXY=http://wwwproxy.unimelb.edu.au:8000"'
    fileHandle2.write (a) 
    fileHandle2.close()