
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
