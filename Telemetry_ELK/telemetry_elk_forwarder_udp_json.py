'''
    Since UDP Json Telemetry will send full telemetry with 12 bytes header,
    logstash encode => json can not parse header part. Forwarder will cut the header and forward
    the real json content to logstash.

'''
import socket, struct
import json
import time

from socket import inet_ntoa

fhost = '127.0.0.1'
fport = 57001

def forward(data):
    fsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_b = data.encode('utf-8')
    print(data_b)
    print("="*40)
    fsock.sendto(data_b,("localhost",57501))  # local logstash udp port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 57500))

End = '''}\''''
Start = '''b\''''
Left = '''{'''
bug_left = '''{{'''
miss_start = 0
miss_end = 0
miss_left = 0
count = 0

start_time = time.time()

while True:

    whole_buf=[]
    data=''
    while True:
        count+=1
        buf, addr = sock.recvfrom(65535)

        print(buf)
        text_buf = str(buf)


        #workaround, cos find a9kv telemetry random add more { in message , if find {{ just move right 1 position
        if bug_left in text_buf:
            json_buff = json.loads(text_buf[text_buf.find('{')+1:-1])
        else:
            json_buff = json.loads(text_buf[text_buf.find('{'):-1])

        forward(text_buf[text_buf.find('{'):-1])  # cut telemetry 12 bytes header and forward to logstash

        tele_node_id = json_buff['node_id_str']
        tele_path = json_buff['encoding_path']
        tele_collection_id = str(json_buff['collection_id'])
        tele_data = json_buff['data_json'][0]['content']

        if tele_path == 'Cisco-IOS-XR-wdsysmon-fd-oper:system-monitoring/cpu-utilization':
            with open('mdt_buff_cpu.tmp', 'w+') as buff_f:
                buff_f.write(json.dumps(json_buff))



        if tele_path == 'Cisco-IOS-XR-shellutil-oper:system-time/uptime':
            with open('mdt_buff_uptime.tmp','w+') as buff_f:
                buff_f.write(json.dumps(json_buff))
