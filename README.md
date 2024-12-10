# daytrading-agent in MEZ timezone
Daytrading Agent


### email creation
create an email on gmail.
Turn on two step authentification (must!).
now go to https://myaccount.google.com/u/4/apppasswords
write an app name and copy the code. Insert it into your env


### Bing Search
1. Create a bing search instance on Azure 
2. Copy the azure keys


### run docker
docker build -t agent-trader .
docker run --env-file .env agent-trader

### Use free heroku scheduler
Use free heroku scheduler to run jobs automatically on heroku.

```
heroku login
heroku container:login
```

Create an heroku app:
```
heroku create daytrader-agent
```

Install the Heroku Scheduler add-on:
```
heroku addons:create scheduler:standard
```

open schedular dashboard:
```
heroku addons:open scheduler
```

Do a git push heroku!
```
git push heroku main
```

Set the env variables:
````
heroku config:set ALPHA_VANTAGE_API_KEY="....."
heroku config:set GMAIL_APP_PASSWORD=" ...."
heroku config:set SENDER_EMAIL="..."
heroku config:set RECIPIENT_EMAIL="...."
heroku config:set OPENAI_KEY="sk-pr...."
heroku config:set AZURE_BING_SUBSCRIPTIONKEY="....."
heroku config:set ADMIN_PW="..."
heroku config:set ADMIN_NAME="..."
```

verify variables:
```
heroku config
```