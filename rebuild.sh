cd backend
sudo docker build -t suna-backend . -f Dockerfile
cd ..
cd frontend
sudo docker build -t suna-frontend . -f Dockerfile
cd ..
sudo docker compose up -d