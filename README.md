# FactoryNamespaceManager
AI Tool for Managing Enterprise-wide Tag Name Specifications


## Steps for migrations
The initial migrations are already created. The related files are stored in `migration` folder

### Create a new migration
```
flask db migrate -m "Changed models"
```

### Apply the migration
```
flask db upgrade
```