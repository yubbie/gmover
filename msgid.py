import httplib2
import os
import mailbox

import random

try:
    import argparse
    flags = argparse.ArgumentParser()
    flags.add_argument('-f','--file',required=True)
    flags.add_argument('-g','--groupid',required=False)
    args = flags.parse_args()
except ImportError:
    flags = None

def main():
    """Listserv archives can be turned into mbox's with a simple edit, but
       it turns out they don't have Message-ID's, which the archive api 
       dislikes (at this writing, in fact, it throws a SUCCESS, and drops
       the message on the floor!
    """

    if not args.groupid:
        args.groupid='@gmover.null'
    for message in mailbox.mbox(args.file):
        if not message['Message-ID']:
            message['Message-ID'] = '<{0}-{1}-groupmover-{2}>'.format(str(random.randrange(10**10)),
			       str(random.randrange(10**10)),args.groupid)
        print message

if __name__ == '__main__':
    main()
