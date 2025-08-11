pipeline {
    agent any

    environment {
        VENV_DIR    = 'venv'
        GCP_PROJECT = "bustracking-467614"
        GCP_REGION  = "us-central1"
        REPO_NAME   = "edtech-repo"
        IMAGE_NAME  = "ml-project"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages {

        stage("Cloning Github repo to Jenkins") {
            steps {
                script {
                    echo '📦 Cloning Github repository...'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/Joelfernandes30/my-mlops-project1.git'
                        ]]
                    )
                }
            }
        }

        stage("Setting up Virtual Environment & Installing Dependencies") {
            steps {
                script {
                    echo '⚙️ Setting up virtual environment...'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage("Build & Push Docker Image to Artifact Registry") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo "🐳 Building and pushing Docker image..."
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}

                        # Authenticate with GCP
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        # Create repository if it doesn't exist
                        gcloud artifacts repositories create ${REPO_NAME} \
                            --repository-format=docker \
                            --location=${GCP_REGION} \
                            --description="Docker repository for ${IMAGE_NAME}" || true

                        # Configure Docker for Artifact Registry
                        gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev --quiet --project=${GCP_PROJECT}

                        # Build and push
                        docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest .
                        docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest
                        '''
                    }
                }
            }
        }

        stage("Deploy to Google Cloud Run") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo '🚀 Deploying to Google Cloud Run...'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ${IMAGE_NAME} \
                            --image=${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest \
                            --platform=managed \
                            --region=${GCP_REGION} \
                            --allow-unauthenticated
                        '''
                    }
                }
            }
        }
    }
}
