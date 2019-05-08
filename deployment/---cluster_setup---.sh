# Note: replace <username>, <password> etc to the real value


# 1. Setup a security group and create rules that allows the instances in the same group to visit each other, then 
# attach it to instances.


# 2. Ssetup the NODENAME when start the docker contatiners, and persist the data on a persistant storage
sudo docker run --name couch_master -e COUCHDB_USER=<username> -e COUCHDB_PASSWORD=<password> -e NODENAME=<instance-IP> -v</path/to/persistence/storage>:/opt/couchdb/data -p 5984:5984 -p 4369:4369 -p 5986:5986 -p 9100-9200:9100-9200 -d couchdb:2.1.1


# 3. Use `curl localhost:5984` to check whether the port has been exposed to host.
{"couchdb":"Welcome","version":"2.1.1","features":["scheduler"],"vendor":{"name":"The Apache Software Foundation"}}


# 4. Make sure we can reach the Couchdb from another instance in the cluster, `curl <remote-instance-ip>:5984`.


# 5. Start to setup the cluster. Run these commands to add each node to the cluster (except for "master" node)
curl -X POST -H 'Content-Type: application/json' http://<username>:<password>@127.0.0.1:5984/_cluster_setup -d "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": \"<username>\", \"password\":\"<password>\", \"port\": 5984, \"node_count\": \"<size of the cluster>\", \"remote_node\": \"<remote node ip>\", \"remote_current_user\": \"<username>\", \"remote_current_password\": \"<password>\"}" 

curl -X POST -H 'Content-Type: application/json' http://<username>:<password>@127.0.0.1:5984/_cluster_setup -d "{\"action\": \"add_node\", \"host\":\"<remote node ip>\", \"port\": 5984, \"username\": \"<username>\", \"password\":\"<password>\"}"



# 6. Finalize the cluster setup
curl -X POST "http://<username>:<password>@localhost:5984/_cluster_setup" -H 'Content-Type: application/json' -d '{"action": "finish_cluster"}'

curl http://<username>:<password>@localhost:5984/_cluster_setup


# 7.Verify the settings, run this one each node
curl -X GET http://<username>:<password>@localhost:5984/_membership

# The output is something like this:
{"all_nodes":["couchdb@172.20.0.2","couchdb@172.20.0.3","couchdb@172.20.0.4"],"cluster_nodes":["couchdb@172.20.0.2","couchdb@172.20.0.3","couchdb@172.20.0.4"]}

