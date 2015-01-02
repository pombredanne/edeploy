#!/usr/bin/python

import sys
import re

def parse_etc_passwd():
    with open('/etc/passwd','r') as f:
        passwd = f.read()
    array = []
    for line in passwd.split("\n")[0:-1]:
        tokens = line.split(":")
        user_uid_gid = {'user': tokens[0], 'uid': tokens[2], 'gid': tokens[3]}
        array.append(user_uid_gid)
    user_list = sorted(array, key=lambda k: k['user'])
    return user_list

def parse_root_ids_tables():
    with open('/root/ids.tables','r') as f:
        ids = f.read()
    ids_table = []
    for line in ids.split("\n"):
        if 'gids =' in line:
            break
        mmatch = re.match("(uids = {)?'([a-z-]+)': \('([0-9]*)', '([0-9]*)'\)(,|})?", line.strip())
        user_uid_gid = {'user': mmatch.group(2), 'uid': mmatch.group(3), 'gid': mmatch.group(4)}
        ids_table.append(user_uid_gid)
    return ids_table

def find_missing_uids(user_list, ids_table):
    # Compare the two arrays returns a list
    # of user who should be present but are
    # not present
    missing_uids = []
    for user_real in user_list:
        exist = 0
        for user_virtual in ids_table:
            if user_real['user'] == user_virtual['user'] and user_real['gid'] == user_virtual['gid'] and user_real['uid'] == user_virtual['uid']:
                exist = 1
                break
        if exist == 0:
            missing_uids.append(user_real)

    return missing_uids


def main():
    etc_passwd = parse_etc_passwd()
    root_ids_tables = parse_root_ids_tables()
    missing_uids = find_missing_uids(etc_passwd, root_ids_tables)
    if len(missing_uids) > 0:
        print 'Non matching uids between /etc/passwd and /root/ids.tables'
        for missing_uid in missing_uids:
            print "'" + missing_uid['user'] + "': ('" + missing_uid['uid'] + "', '" + missing_uid['gid'] + "')"
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
  main()
