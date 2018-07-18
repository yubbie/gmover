from __future__ import print_function
from apiclient.discovery import build
import apiclient
from httplib2 import Http
from oauth2client import file, client, tools

from email import Utils
from email import MIMEText

import httplib2
import os
import mailbox
import StringIO
import random


try:
    import argparse
    flags  = argparse.ArgumentParser(parents=[tools.argparser])
    flags.add_argument('-g','--group',required=True)
    flags.add_argument('-f','--file',required=True)
    flags.add_argument('-v','--verbose',action='count',required=False)
    args = flags.parse_args()
except ImportError:
    flags = None

SERVICE_ACCOUNT_FILE = 'service.json'
APPLICATION_NAME = 'Gmover Google Apps Groups Migration Archive Importer'


def main():
    """The core of the code is from one of the examples of the 
    Google Admin-SDK Groups Migration API developer page.
    
    The gluing and tweaking is by Ron Jarrell, Manager for Ecommunications
    Services at Virgina Tech.  You can contact him at jarrell@vt.edu.
    If this helps you, feel free to drop a line, or send a postcard :)

    Creates a Google Admin-SDK Groups Migration API service object and
    inserts all mail in an mbox into a group.
    
    Note, this was written to solve a problem.  Migrating a listserv, which
    generates archives that are very mbox like, and can be made an mbox with 
    a simple edit, to google groups.  The archives turned out to uniformly
    not have message-id's, which is bad.

    If it didn't write for some reason, like a bad message, we really
    didn't care.  So there's a lot of cleanup that can be done.  Code
    contributions accepted.  I'm posting this brute-force solution because
    I didn't see any other examples out there that were "pay us to do it for
    you," and if you're looking at this, you're probably like me, and capable
    of taking this thing and tweaking it to what you need and never needing
    it again.  Note this is also the first python I've done from scratch that
    didn't involve the words hello and world.

    """

    SCOPES = 'https://www.googleapis.com/auth/apps.groups.migration'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store, args)
    service = build('groupsmigration', 'v1', http=creds.authorize(Http()))


    groupId = args.group
     

    if args.verbose > 0:
        print("Processing " + args.file)
    for message in mailbox.mbox(args.file):
        if not message['Message-ID']:
            message['Message-ID'] = '<{0}-{1}-groupmover-{2}'.format(str(random.randrange(10**10)),
			       str(random.randrange(10**10)),
                                               groupId)
            if args.verbose > 1:
                print("Creating message id " + message['Message-ID'])
        stream = StringIO.StringIO()
        stream.write(message.as_string())
        if args.verbose > 2:
            print("Generating payload")
        media = apiclient.http.MediaIoBaseUpload(stream,
                                                 mimetype='message/rfc822')

        if args.verbose > 2:
            print("Inserting")
        result = service.archive().insert(groupId=groupId,
                                          media_body=media).execute()
        if result['responseCode'] <> 'SUCCESS' or args.verbose > 2:
           print(result['responseCode'])

if __name__ == '__main__':
    main()
