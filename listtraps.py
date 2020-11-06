#!/usr/bin/env python3.8

"""list the traps and status"""

import os, sys, string, time, logging, argparse

_version = "0.1"

try:
  import config
except ImportError:
  logging.warning("no config file present. Copy sample_config.py to config.py and add your username and password.")
  sys.exit(1)

import asyncio
from victor_smart_kill import VictorApi, VictorAsyncClient

async def listtraps(username, password):
  async with VictorAsyncClient(username, password) as client:
    tokenfn = ".token-%s" % username
    if os.path.exists(tokenfn):
      client._token = open(tokenfn).read()

    api = VictorApi(client)

    if client._token:
      open(tokenfn, "w").write(client._token)
    
    traps = await api.get_traps()

    if 0:
      history = await api.get_trap_history(traps[0].id)
      for act in history:
        print (act.sequence_number, act.time_stamp, act.activity_type, act.activity_type_text, act.battery_level, act.is_rat_kill)
    return traps

async def start():
  traps = []
  for account, username, password in config.users:
    _traps = await listtraps(username, password)
    for trap in _traps:
      trap.account = account
      
    traps.extend(_traps)

  traps.sort(key=lambda x: x.name)
  for n, trap in enumerate(traps):
    print ("%2s %-30s %-2s %10s %3s %3s %3s" % (n, trap.name, trap.account, trap.ssid, trap.status, trap.trapstatistics.battery_level, trap.trapstatistics.kills_present))
    

def test():
  logging.warn("Testing")

def parse_args(argv):
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=__doc__)

  parser.add_argument("-t", "--test", dest="test_flag", 
                    default=False,
                    action="store_true",
                    help="Run test function")
  parser.add_argument("--log-level", type=str,
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Desired console log level")
  parser.add_argument("-d", "--debug", dest="log_level", action="store_const",
                      const="DEBUG",
                      help="Activate debugging")
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const",
                      const="CRITICAL",
                      help="Quite mode")
  #parser.add_argument("files", type=str, nargs='+')

  args = parser.parse_args(argv[1:])

  return parser, args

def main(argv, stdout, environ):
  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(message)s", 
                    datefmt="%m/%d %H:%M:%S", level=args.log_level)

  if args.test_flag:  test();   return

  asyncio.run(start())

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
