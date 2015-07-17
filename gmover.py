import httplib2
import os
import mailbox
import StringIO
import random

import apiclient
from apiclient import discovery

import oauth2client
from oauth2client import client
from oauth2client import tools

from email import Utils
from email import MIMEText


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser])
    flags.add_argument('-g','--group',required=True)
    flags.add_argument('-f','--file',required=True)
    flags.add_argument('-v','--verbose')
    args = flags.parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/apps.groups.migration'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmover Google Apps Groups Migration Archive Importer'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'groupsmigration-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

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
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('groupsmigration', 'v1', http=http)

    groupId = args.group

    if args.verbose > 0:
        print "Processing " + args.file
    for message in mailbox.mbox(args.file):
        if not message['Message-ID']:
            message['Message-ID'] = '<{0}-{1}-groupmover-{2}'.format(str(random.randrange(10**10)),
			       str(random.randrange(10**10)),
                                               groupId)
        stream = StringIO.StringIO()
        stream.write(message.as_string())
        media = apiclient.http.MediaIoBaseUpload(stream,
                                                 mimetype='message/rfc822')

        result = service.archive().insert(groupId=groupId,
                                          media_body=media).execute()
        if result['responseCode'] <> 'SUCCESS':
           print result['responseCode']

if __name__ == '__main__':
    main()
