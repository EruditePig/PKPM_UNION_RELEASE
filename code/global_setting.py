# coding=utf-8 
import os
import sys
import web

# force stdout to stderr
sys.stdout = sys.stderr

# Add local directories to the system path
# include_dirs = [ 'lib', 'pages' ]
# for dirname in include_dirs:
#   sys.path.append( os.path.dirname(__file__) + '/' + dirname )

# Change to the directory this file is located in
os.chdir( os.path.dirname(__file__))

# Turn on/off debugging
web.config.debug = True