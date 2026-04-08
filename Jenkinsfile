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
                echo "✅ Code checked out"
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    venv/bin/pip install --upgrade pip
                    venv/bin/pip install -r requirements.txt
                '''
                echo "Build complete."
            }
        }

        stage('Test') {
            steps {
                sh '''
                    venv/bin/pip install pytest
                    venv/bin/pytest --junitxml=report.xml
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
                withSonarQubeEnv('SonarQube') {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=delivery-optimization \
                          -Dsonar.sources=src \
                          -Dsonar.language=py \
                          -Dsonar.python.version=3 \
                          -Dsonar.host.url=${SONAR_URL} \
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                sh """
                    docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
                    docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest
                    echo ${DOCKER_CREDENTIALS_PSW} | docker login \
                        -u ${DOCKER_CREDENTIALS_USR} --password-stdin
                    docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                    docker push ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh """
                    sed -i 's|IMAGE_TAG|${IMAGE_TAG}|g' k8s/deployment.yaml
                    kubectl apply -f k8s/deployment.yaml
                """
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline PASSED!"
        }
        failure {
            echo "❌ Pipeline FAILED — check logs above"
        }
        always {
            sh "docker rmi ${DOCKER_IMAGE}:${IMAGE_TAG} || true"
            cleanWs()
        }
    }
}
