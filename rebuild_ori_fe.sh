echo "-------begin build frontend ori-------"
sudo git checkout dev_ori_fe
sudo git pull
cd frontend
sudo docker build -t registry.ainnovation.com/bg_cto/newagent-frontend-ori . -f Dockerfile
cd ..
echo "-------build frontend  ori finished-------"

echo "-------begin run docker compose-------"
sudo docker-compose up -d
echo "-------run docker compose finished-------"
