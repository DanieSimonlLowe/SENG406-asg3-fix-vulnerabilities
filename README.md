# setup

set up the pre-commit checks
```bash
`chmod a+rx checks/TemplateInjectionDetect.sh
chmod a+rx .git/hooks/pre-commit
ln -s $(pwd)/checks/TemplateInjectionDetect.sh .git/hooks/pre-commit`
```

