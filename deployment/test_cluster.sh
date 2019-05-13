cd ansible_playbooks
ansible-playbook -i hosts -u ubuntu --key-file=boyul.pem check_cluster.yml