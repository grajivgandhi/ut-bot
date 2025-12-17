git init
git config user.name "Your Name"
git config user.email "your@email.com"
git add .
git commit -m "Initial commit: UT Bot trading bot"
git remote add origin https://github.com/USERNAME/ut-bot.git
git branch -M main
git push -u origin main
git add .
git commit -m "Deploy UT Bot to Heroku"
git push origin main
git push heroku main
git add .
git commit -m "Update bot parameters"
git push origin main
git push heroku main
git push heroku main
This file was moved to `archive/deployment/HEROKU_DEPLOYMENT.md`.

If you want to permanently delete the archived copy, remove `archive/deployment/HEROKU_DEPLOYMENT.md`.
