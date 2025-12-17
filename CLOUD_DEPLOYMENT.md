docker-compose up -d
docker-compose logs -f ut-bot
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud run deploy ut-bot \
echo "python-3.10.12" > runtime.txt
git add .
git commit -m "Deploy to Heroku"
git push heroku main
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ut-bot.git
git push -u origin main
docker-compose logs -f ut-bot
gcloud run logs read ut-bot --limit 50
docker-compose ps
docker-compose restart ut-bot
docker-compose logs -f ut-bot --tail 100
   docker build -t ut-bot .
   docker run -e API_KEY=test -e API_SECRET=test ut-bot
docker-compose logs -f ut-bot --tail 200
This file was moved to `archive/deployment/CLOUD_DEPLOYMENT.md`.

If you want to permanently delete the archived copy, remove `archive/deployment/CLOUD_DEPLOYMENT.md`.
