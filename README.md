# github-actions-helm-dependency-updater

<!-- BEGIN_ACTION_DOCS -->
<!-- END_ACTION_DOCS -->

# Local development

To develop locally, install requirements to ensure the .env file is used in the project root:

```
pip3 install -r requirements.txt
```

```
echo OCI_USERNAME=<Username for your OCI registry if required> >> bin/.env
echo OCI_PASSWORD=<Password for your OCI registry if required> >> bin/.env
echo CHART_LOCATION=<Path to Chart.yaml relative to the current directory >> bin/.env
echo UPDATE_ON=<List of update types to include> >> bin/.env
```

Then run the script:

```
python3 bin/main.py
```
