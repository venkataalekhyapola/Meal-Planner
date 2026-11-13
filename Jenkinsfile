pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Downloading Meal Planner project from GitHub'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python --version'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'python -m pytest tests/ -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t meal-planner:latest .'
            }
        }
    }

    post {
        success {
            echo 'Meal Planner pipeline completed successfully!'
        }

        failure {
            echo 'Meal Planner pipeline failed. Check the console output.'
        }
    }
}