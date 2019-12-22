from server.instance import server
import sys, os

# Need to import all resources
# so that they register with the server 
from resources.book import *
from resources.fact import *
from resources.searchWord import *

if __name__ == '__main__':
    server.run()