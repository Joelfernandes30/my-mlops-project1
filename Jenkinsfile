pipeline {
    agent any

        environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "bustracking-467614"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage("Cloning Github repo to jenkins"){
            steps{
                script{
                    echo 'Cloning the repository...'
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Joelfernandes30/my-mlops-project1.git']])
                }

                }
            }



             stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
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
                echo "🐳 Building and pushing Docker image to AR..."
                sh '''
                export PATH=$PATH:${GCLOUD_PATH}

                # Authenticate with GCP
                gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                gcloud config set project ${GCP_PROJECT}

                # Create AR repository if not exists
                gcloud artifacts repositories create ${REPO_NAME} \
                    --repository-format=docker \
                    --location=${GCP_REGION} \
                    --description="Docker repository for edtech-web" || true

                # Configure docker for Jenkins user
                gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev --quiet --project=${GCP_PROJECT}

                # Build and push
                docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest .
                docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest
                '''
            }
        }
    }
}


         stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}


                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ml-project \
                            --image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                            --platform=managed \
                            --region=us-central1 \
                            --allow-unauthenticated
                            
                        '''
                    }
                }
            }
        }


        }

    }
