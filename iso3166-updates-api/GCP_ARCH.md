# Configuring API on GCP

The API and its various endpoints were configured and deployed using GCP, below is the steps required to realise this architecture, including various commands using the gcloud sdk. 

1. Download GCP SDK (https://cloud.google.com/sdk/docs/install#linux)

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-438.0.0-linux-x86_64.tar.gz
tar -xf google-cloud-cli-438.0.0-linux-x86.tar.gz
./google-cloud-sdk/install.sh
./google-cloud-sdk/bin/gcloud init
```

2. Initialise project - https://cloud.google.com/sdk/gcloud/reference/projects.

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
gcloud iam service-accounts create SA_ACCOUNT_NAME --display-name="SERVICE_ACCOUNT_NAME" --project=$PROJECT_ID
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

```bash
gcloud storage buckets create gs://BUCKET_NAME 
```

4. Create cloud source repo:
```bash
gcloud source repos create REPOSITORY_NAME
```

5. Cloud Build (https://cloud.google.com/build/docs/build-push-docker-image)
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:SA_ACCOUNT_NAME \
    --role=roles/run.admin,roles/iam.serviceAccountUser
```

```bash
gcloud builds submit --region=us-west2 --config cloudbuild.yaml
```

6. Cloud Functions.
7. API Gateway.

Create API Gateway
```
gcloud api-gateway apis create API_ID --project=PROJECT_ID
```
8. Load Balancer.
9. Connect Load Balancer -> API Gateway via NEG and http-proxy, URL mapping and SSL certs.

enable APIs.