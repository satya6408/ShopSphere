
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out ShopSphere source code'
                checkout scm
            }
        }

        stage('Product Service Tests') {
            steps {
                dir('services/product-service') {
                    sh '''
                        python3 -m venv venv
                        venv/bin/pip install -r requirements.txt
                        venv/bin/python -m pytest -v
                    '''
                }
            }
        }

        stage('Cart Service Tests') {
            steps {
                dir('services/cart-service') {
                    sh '''
                        python3 -m venv venv
                        venv/bin/pip install -r requirements.txt
                        venv/bin/python -m pytest -v
                    '''
                }
            }
        }

        stage('Trivy Filesystem Scan') {
            steps {
                sh '''
                    trivy fs \
                      --scanners vuln,secret,misconfig \
                      --severity HIGH,CRITICAL \
                      --exit-code 0 \
                      .
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('ShopSphere-SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    docker build \
                      -t shopsphere-product:${BUILD_NUMBER} \
                      -t shopsphere-product:latest \
                      services/product-service

                    docker build \
                      -t shopsphere-cart:${BUILD_NUMBER} \
                      -t shopsphere-cart:latest \
                      services/cart-service
                '''
            }
        }

        stage('Trivy Docker Image Scan') {
            steps {
                sh '''
                    trivy image \
                      --severity HIGH,CRITICAL \
                      --exit-code 0 \
                      shopsphere-product:${BUILD_NUMBER}

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --exit-code 0 \
                      shopsphere-cart:${BUILD_NUMBER}
                '''
            }
        }
    }

    post {
        success {
            echo 'ShopSphere CI pipeline completed successfully!'
        }

        failure {
            echo 'ShopSphere CI pipeline failed. Check the console output.'
        }
    }
}

