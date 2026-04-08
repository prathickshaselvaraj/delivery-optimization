pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        SONAR_TOKEN        = credentials('sonarqube-token')
        DOCKER_IMAGE       = "prathicksha15/delivery-optimization"
        IMAGE_TAG          = "${env.BUILD_NUMBER}"
        SONAR_URL          = "http://localhost:9000"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    venv/bin/pip install --upgrade pip
                    venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    venv/bin/pip install pytest pytest-cov
                    venv/bin/pytest --cov=. --cov-report=xml --junitxml=report.xml
                '''
            }
            post {
                always {
                    junit 'report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('My Sonar Server'){
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=delivery-optimization \
                          -Dsonar.sources=. \
                          -Dsonar.tests=tests \
                          -Dsonar.exclusions=tests/**,venv/** \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.host.url=${SONAR_URL} \
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                sh """
                    docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
                    docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest
                    echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin
                    docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                    docker push ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Update GitOps Repo') {
            steps {
                sh """
                    git clone https://github.com/prathickshaselvaraj/delivery-optimization-gitops.git
                    cd delivery-optimization-gitops/k8s

                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" deployment.yaml

                    git config user.email "jenkins@example.com"
                    git config user.name "jenkins"

                    git add deployment.yaml
                    git commit -m "Update image to ${IMAGE_TAG}"
                    git push
                """
            }
        }
    }

    post {
        always {
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            cleanWs()
        }
    }
}
