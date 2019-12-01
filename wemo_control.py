#!/usr/bin/env python3
"""

WeMo Control Script

Based on the shell script from rich@netmagi.com.

Usage: ./wemo_control IP ON/OFF/GETSTATE/GETSIGNALSTRENGTH/GETFRIENDLYNAME
"""

import os
import subprocess
import sys

PORT = 49153
PIPE = subprocess.PIPE

def get_state(*, ip):
    curl_args = [
        'curl', '-0', '-A', '', '-X', 'POST', '-H', 'Accept: ',
        '-H', 'Content-type: text/xml; charset=\"utf-8\"',
        '-H', 'SOAPACTION: "urn:Belkin:service:basicevent:1#GetBinaryState"',
        '--data',
        '<?xml version="1.0" encoding="utf-8"?>\
           <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
           <s:Body>\
            <u:GetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">\
             <BinaryState>1</BinaryState>\
            </u:GetBinaryState>\
           </s:Body>\
          </s:Envelope>',
        '-s', 'http://{ip}:{port}/upnp/control/basicevent1'.format(ip=ip, port=PORT),
    ]
    curl = subprocess.Popen(curl_args, stdout=PIPE)
    grep = subprocess.Popen(['grep', '<BinaryState'], stdin=curl.stdout, stdout=PIPE)
    cut_f2 = subprocess.Popen(['cut', '-d', '>', '-f2'], stdin=grep.stdout, stdout=PIPE)
    cut_f1 = subprocess.Popen(['cut', '-d', '<', '-f1'], stdin=cut_f2.stdout, stdout=PIPE)

    stdout = cut_f1.communicate()[0].decode('utf-8').strip()
    if stdout == '1':
        print('ON')
    elif stdout == '0':
        print('OFF')
    else:
        raise ValueError('Got unexpected curl output')


def turn_on_or_off(*, ip, on):
    curl_args = [
        'curl', '-0', '-A', '', '-X', 'POST', '-H', 'Accept: ',
        '-H', 'Content-type: text/xml; charset=\"utf-8\"',
        '-H', 'SOAPACTION: "urn:Belkin:service:basicevent:1#SetBinaryState"',
        '--data',
        '<?xml version="1.0" encoding="utf-8"?>\
           <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
           <s:Body>\
            <u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">\
             <BinaryState>{on}</BinaryState>\
            </u:SetBinaryState>\
           </s:Body>\
          </s:Envelope>'.format(on=int(on)),
        '-s', 'http://{ip}:{port}/upnp/control/basicevent1'.format(ip=ip, port=PORT),
    ]
    curl = subprocess.Popen(curl_args, stdout=PIPE)
    grep = subprocess.Popen(['grep', '<BinaryState'], stdin=curl.stdout, stdout=PIPE)
    cut_f2 = subprocess.Popen(['cut', '-d', '>', '-f2'], stdin=grep.stdout, stdout=PIPE)
    cut_f1 = subprocess.Popen(['cut', '-d', '<', '-f1'], stdin=cut_f2.stdout, stdout=PIPE)

    stdout = cut_f1.communicate()[0].decode('utf-8').strip()
    if stdout != str(int(on)):
        raise ValueError('Got unexpected curl output')


def turn_on(*, ip):
    turn_on_or_off(ip=ip, on=True)


def turn_off(*, ip):
    turn_on_or_off(ip=ip, on=False)


def get_signal_strength(*, ip):
    raise NotImplementedError()


def get_friendly_name(*, ip):
    raise NotImplementedError()


def print_usage():
    known_commands = [command for command in COMMAND_LOOKUP]
    print('Usage: wemo_control IP_ADDRESS %s' % '/'.join(known_commands))


COMMAND_LOOKUP = {
    'GETSTATE': get_state,
    'ON': turn_on,
    'OFF': turn_off,
    'GETSIGNALSTRENGTH': get_signal_strength,
    'GETFRIENDLYNAME': get_friendly_name,
}


def _main():
    if len(sys.argv) != 3:
        print_usage()
        return 1

    ip = sys.argv[1]
    command = sys.argv[2]
    try:
        COMMAND_LOOKUP[command](ip=ip)
    except KeyError:
        print("Unknown command %s" % command)
        print_usage()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(_main())
