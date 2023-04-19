# Configuring API on GCP

The API and its various endpoints were configured and deployed using GCP, below is the steps required to realise this architecture, including various commands using the gcloud sdk. 

1. Download GCP SDK

2. Initialise project - https://cloud.google.com/sdk/gcloud/reference/projects, enable APIs.

Create project:
```
gcloud projects create PROJECT_ID
```
Set project:
```
gcloud config set project PROJECT_ID
```

3. Create SA - role, permissions, bindings etc.

Create service account:
```
gcloud iam service-accounts create ACCOUNT_NAME --display-name="SERVICE_ACCOUNT_NAME" --project=$PROJECT_ID
```

Get full email id of new service account and download key:
```
fullId=$(gcloud iam service-accounts list --filter="email ~ ^ACCOUNT_NAME" --format='value(email)')
gcloud iam service-accounts keys create ACCOUNT_NAME.json --iam-account $fullId
```

Add IAM policy binding:
```
gcloud iam service-accounts add-iam-policy-binding ...
```

3. Create bucket.
4. Create cloud source repo.
5. Cloud Build.
6. Cloud Functions.
7. API Gateway.

Create API Gateway
```
gcloud api-gateway apis create API_ID --project=PROJECT_ID
```
8. Load Balancer.
9. Connect Load Balancer -> API Gateway via NEG and http-proxy, URL mapping and SSL certs.