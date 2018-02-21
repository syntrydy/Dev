from __future__ import with_statement
import sys
import string
import time
import random
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL

# Replace with FQDN's of your LDAP servers separated by commas and appended :1636
hosts = (
        )
# Input LDAP DN and Password in the following variables
password = ''

# 'cn=directory manager' for OpenDJ

DN       = 'cn=directory manager,o=gluu'

# Create a random string of characters for the name field

def getName():
    name = ''
    for i in range(10):
        name += random.choice(string.letters)
    return name



def replicationStatus():
    compare = []
    counts = []
    for host in hosts:
        try:
            ldap_uri = "ldaps://{}".format(host)
            print 'Connecting to ', host
            server = Server(ldap_uri, use_ssl=True)
            conn = Connection(server, DN, password)

            conn.bind()
            conn.search(search_base='o=gluu', search_scope=BASE, search_filter='(objectclass=*)', attributes=['+'])
                
            # Add the contextCSN to the compare list
        
            compare.append(conn.response[0]['attributes']['contextCSN'])
                
            # Search for entries in LDAP
        
            conn.search(search_base = 'o=gluu',
                     search_filter = '(cn=*)',
                     search_scope = SUBTREE)
            common = conn.entries
        
            # Count the number of entries in LDAP
                
            countVar = '{} total users: {}'.format(host, sum(1 for _ in common))
        
            # Append to the counts list
                
            counts.append(str(countVar))
        
        except:
            print host, "seems down"
        
    # Add server entries to log

    log = open("replication_log.log","a")
    i=1
    for count in counts:
        user_log_entry = '{} \n'.format(count)
        print user_log_entry
        log.write(user_log_entry)
        i = i + 1

    # Test whether the indexCSN's match, an indicator of whether replication is currently working.
    # Write these to a log file for monitoring
    try:
        if all(x==compare[0] for x in compare):
            print 'CSN match'
            with open("replication_log.log","a") as log:
                log.write('CSNs Synced @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))
        else:
            print 'Replication out of sync'
            with open("replication_log.log","a") as log:
                log.write('CSN Out of sync @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))

    except:
        print 'Something went wrong...'
    print "\nSleeping for", 1, "seconds\n"
    time.sleep(1)

def addUser():
    try:
        host = random.choice(hosts)

        ldap_uri = "ldaps://{}".format(host)
        server = Server(ldap_uri)

        conn = Connection(server, DN, password)
        conn.bind()

        uid = '{0}@{1}'.format(time.time(), host)

        name = getName()
        sn = getName()

        cn = name + ' ' + sn

        dn = "cn={}, o=gluu".format(cn)

        attributes={
                                         'objectClass': ['top', 'inetOrgPerson'],
                                         'givenname': name,
                                         "cn": cn,
                                         'sn': sn,
                                         'uid': uid,


                                     }


        conn.add(dn, attributes=attributes )

    except:
        print host, "seems to be down"
'''
def checkDiff():
    compare = []
    for host in hosts:
        ldapEntries = []
        try:
            ldap_uri = "ldaps://{}".format(host)
            print 'Connecting to ', host
            server = Server(ldap_uri)
            conn = Connection(server, DN, password)

            conn.bind()

            conn.search(search_base = 'o=gluu', search_filter = '(objectClass=*)',search_scope = SUBTREE, attributes=['*','+'])
            # Add the contextCSN to the compare list
            compare.append(conn.response)
            ldapEntries = conn.response
        except:
            print host, "seems down"
        with open("{}_entries.log".format(host),"a") as ldapEntry:
                ldapEntry.write('{} \n'.format(ldapEntries))
    # Compare entries to see if data matches.
    try:
        if all(x==compare[0] for x in compare):
            print 'Entries match! \n'
            with open("replication_log.log","a") as log:
                log.write('Entries match @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))
        else:
            print "Entries don't match..."
            with open("replication_log.log","a") as log:
                log.write("Entries dont match.. @"   + time.strftime("%a, %d %b %Y %H:%M:%S\n"))

    except:
        print 'Something went wrong...'
'''
while True:
    n = 10
    i = 0
    print 'Adding users...'
    while n>i:
        addUser()
        i = i +1
    print 'Users added. \n'
    replicationStatus()
