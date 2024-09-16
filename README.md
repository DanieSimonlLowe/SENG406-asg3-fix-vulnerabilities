# setup

set up the pre-commit checks
```bash
`/bin/bash /csse/users/dlo54/Desktop/seng406/seng406-asg3-24/checks/combine.sh`
chmod a+rx '.git/hooks/pre-commit'
```

# Build static files
Static files must be built before running the server. The following command builds all static files.

```bash
python manage.py collectstatic
```

# Run the server 
To run the server use the following command.
```bash
python manage.py runserver
```