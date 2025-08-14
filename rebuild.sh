echo "-------begin build backend-------"
cd backend
sudo docker build -t registry.ainnovation.com/bg_cto/newagent-backend . -f Dockerfile
cd ..
echo "-------build backend finished-------"

#echo "-------begin build worker-------"
#cd backend
#sudo docker build -t suna-worker . -f Dockerfile
#cd ..
#echo "-------build worker finished-------"

echo "-------begin build frontend-------"
cd frontend
sudo docker build -t registry.ainnovation.com/bg_cto/newagent-frontend . -f Dockerfile
cd ..
echo "-------build frontend finished-------"

echo "-------begin run docker compose-------"
sudo docker-compose up -d
echo "-------run docker compose finished-------"
