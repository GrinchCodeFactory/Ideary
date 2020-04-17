# Ideary

## DB Setup

```javascript
// mongo <db host> -u adm --ssl --authenticationDatabase admin
use admin

db.createUser(
  {
    user: "ideary",
    pwd: "boumoosion",
    roles: [ 
        { role: "readWrite", db: "ideary" }
    ]
  }
)
```

## Config Sample
File `~/ideary.yaml`:
```yaml
mongodb: 
  host: mongo.fabi.me
  usr: ideary
  pw: boumoosion
  
telegram: 
  token: abc
```



# Playground
* Resize large images
* Natural dialogs
* Context stack