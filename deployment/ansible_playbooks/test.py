# coding: utf-8

import re,io,sys
import os

if __name__ == '__main__':
    fileHandle = open ( sys.argv[1], 'w' )
    fileHandle.write ( 'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"\n\nhttp_proxy="http://wwwproxy.unimelb.edu.au:8000"\nhttps_proxy="http://wwwproxy.unimelb.edu.au:8000"\nftp_proxy="http://wwwproxy.unimelb.edu.au:8000"\nno_proxy=localhost,127.0.0.1,127.0.1.1,ubuntu,demo.novalocal,demo' )
    fileHandle.close()