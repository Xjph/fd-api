#!/usr/bin/env python3
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop=2 smartindent smarttab

import os
import time
import yaml, logging, argparse

import requests
import pprint
pp = pprint.PrettyPrinter(indent=2, width=10000)

#from org.miggy import edcapi
#import org.miggy.edcapi.profile as profile
import org.miggy.edcapi

###########################################################################
"""
 "  Configuration
"""
###########################################################################
__configfile_fd = os.open("fd-api-config.yaml", os.O_RDONLY)
__configfile = os.fdopen(__configfile_fd)
__config = yaml.load(__configfile, Loader=yaml.CLoader)
###########################################################################

###########################################################################
# Logging
###########################################################################
os.environ['TZ'] = 'UTC'
time.tzset()
__default_loglevel = logging.INFO
__logger = logging.getLogger('fd-api')
__logger.setLevel(__default_loglevel)
__logger_ch = logging.StreamHandler()
__logger_ch.setLevel(__default_loglevel)
__logger_formatter = logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(module)s.%(funcName)s: %(message)s')
__logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S';
__logger_formatter.default_msec_format = '%s.%03d'
__logger_ch.setFormatter(__logger_formatter)
__logger.addHandler(__logger_ch)
###########################################################################

###########################################################################
# Command-Line Arguments
###########################################################################
__parser = argparse.ArgumentParser()
__parser.add_argument("--loglevel", help="set the log level to one of: DEBUG, INFO (default), WARNING, ERROR, CRITICAL")
__parser.add_argument("cmdrname", nargs=1, help="Specify the Cmdr Name for this Authorization")
__parser.add_argument("--profile", action="store_true", help="Request retrieval of Cmdr's profile")
__args = __parser.parse_args()
if __args.loglevel:
  __level = getattr(logging, __args.loglevel.upper())
  __logger.setLevel(__level)
  __logger_ch.setLevel(__level)
cmdrname = __args.cmdrname[0]
###########################################################################

###########################################################################
# Load a relevant Auth State
###########################################################################
def loadAuthState(cmdr: str) -> int:
  ########################################
  # Retrieve and test state
  ########################################
  db = edcapi.database(__logger, __config)
  auth_state = db.getActiveTokenState()
  if auth_state:
    ## Do we have an access_token, and does it work?
    if auth_state['access_token']:
      print("Found un-expired access_token, assuming it's good.")
      return(0)
    else:
      print("Un-expired access_token, but no access_token? WTF!")
      return(-1)
  else:
    print("No auth state with un-expired access_token found, continuing...")
  ########################################
###########################################################################

###########################################################################
# Main
###########################################################################
def main():
  __logger.debug("Start")

  if not __args.profile:
    __logger.error("You must specify at least one action")

  capi = org.miggy.edcapi.edcapi(__logger, __config)

  if __args.profile:
    profile = capi.profile.get(cmdrname)
    if not profile:
      return(-1)

    print(pp.pformat(profile))

###########################################################################
if __name__ == '__main__':
  exit(main())
