#Team 54 COMP90024
#Melbourne
#Boyu Li 878890
import boto
import sys
import json
from boto.ec2.regioninfo import RegionInfo
import time

#get keys
f=open(sys.argv[1])
keys=json.load(f)



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
                                     security_groups=['default', 'ssh', 'http'])
instance=reservation.instances[0]
print('new instance {} has been created'.format(instance.id))
vol_req=ec2_conn.create_volume(20,'melbourne-qh2-uom')
print("Please wait!")
while instance.state!='running':
    instance.update()
    time.sleep(5)
while vol_req.status!='available':
    vol_req.update()
    time.sleep(5)
ec2_conn.attach_volume(vol_req.id,instance.id,'/dev/vdb')
print("instance is ready and volume attached!")