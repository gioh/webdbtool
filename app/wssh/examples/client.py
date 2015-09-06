#!/usr/bin/env python

if __name__ == '__main__':
    from wssh import client

    client.invoke_shell('ws://10.1.1.91:7777/remote?key=secret')
