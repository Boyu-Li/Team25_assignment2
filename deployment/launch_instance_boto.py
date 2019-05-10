#Team 54 COMP90024
#Melbourne
#Boyu Li 878890
import boto
import sys
import json
from boto.ec2.regioninfo import RegionInfo
import time
import os

#get keys
f=open(sys.argv[1])
keys=json.load(f)

flag = 1
slaver_num = 0
instances = {}
test_dict = {}
try:
    with open("host_list.json",'r') as load_f:
        load_dict = json.load(load_f)
        t_dict = json.loads(load_dict)
        if len(t_dict) == 0:
            flag = 0
        if flag != 0:
            slaver_num = t_dict['slaver_num']
            instances['master'] = t_dict['master']
            for i in range(slaver_num):
                t = 'slaver'+str(i+1)
                instances[t]=t_dict[t]
            if slaver_num == 4:
                print('4 instance already existed')
                os._exit()
except json.decoder.JSONDecodeError:
    flag = 0

region = RegionInfo(name='melbourne-qh2-uom', endpoint='nova.rc.nectar.org.au')

ec2_conn = boto.connect_ec2(aws_access_key_id=keys['ec2_access_key'],
 aws_secret_access_key=keys['ec2_secret_key'],
 is_secure=True,
 region=region,
 port=8773,
 path='/services/Cloud',
 validate_certs=False)

reservation=ec2_conn.run_instances('ami-1dfc7fb8',
                                     placement='melbourne-qh2-uom',
                                     key_name='boyul',
                                     instance_type='uom.mse.2c9g',
                                     security_groups=['default', 'ssh', 'http', 'couchdb'])
instance=reservation.instances[0]
print('new instance {} has been created'.format(instance.id))
vol_req=ec2_conn.create_volume(20,'melbourne-qh2-uom')
print("Waiting for spawning......")
while instance.state!='running':
    instance.update()
    time.sleep(5)
private_ip_address =instance.private_ip_address
while vol_req.status!='available':
    vol_req.update()
    time.sleep(5)
ec2_conn.attach_volume(vol_req.id,instance.id,'/dev/vdb')
print("instance is ready and volume attached!")
print("Updating hosts file......")
if flag == 0:
    test_dict = {'master':private_ip_address,'slaver_num':0}
    load_dict = json.dumps(test_dict)
    instances['master'] = private_ip_address
else:
    slaver_num += 1
    name = 'slaver'+str(slaver_num)
    instances[name] = private_ip_address
    test_dict['master'] = instances['master']
    test_dict['slaver_num'] = slaver_num
    for i in range(slaver_num):
        n1 = 'slaver'+str(i+1)
        test_dict[n1] = instances[n1]
    load_dict = json.dumps(test_dict)
with open("host_list.json", "w") as dump_f:
    json.dump(load_dict, dump_f)
fileHandle = open ( 'ansible_playbooks\hosts', 'w' )
host = '[master_group]\nmaster ansible_host='+str(instances['master'])+' hostname=master'+'\n[slaver_group]'
for i in range(slaver_num):
    temp = 'slaver'+str(i+1)
    append_string = '\n'+temp+' ansible_host='+str(instances[temp])+' hostname='+temp
    host += append_string
fileHandle.write(host)
fileHandle.close()
print("Launching successfully!")
