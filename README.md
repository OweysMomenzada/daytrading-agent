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