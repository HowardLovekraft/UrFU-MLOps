#№1. download
pwd
python3 -m venv ./my_env #создать виртуальное окружение в папку 
. ./my_env/bin/activate   #активировать виртуальное окружение
cd ./Lab_4  #перейти в директорию ./UrFU-MLOps/lab4	
python3 -m ensurepip --upgrade
pip3 install setuptools
pip3 install -r requirements.txt    #установить пакеты python
python3 download_data.py    #запустить python script
#-----------------------

#№2. train_model 
cd /var/lib/jenkins/workspace/Download
echo "Start train model"
. ./my_env/bin/activate   #активировать виртуальное окружение
cd ./Lab_4  #перейти в директорию ./UrFU-MLOps/lab4
python3 train_model.py > best_model.txt #обучение модели запись лога в файл best_model
#------------------------

#3. deploy 
cd /var/lib/jenkins/workspace/Download
. ./my_env/bin/activate   #активировать виртуальное окружение
cd ./Lab_4		   #перейти в директорию ./MLOPS/Lab_4
export BUILD_ID=dontKillMe            #параметры для jenkins чтобы не убивать фоновый процесс для mlflow сервиса
export JENKINS_NODE_COOKIE=dontKillMe #параметры для jenkins чтобы не убивать фоновый процесс для mlflow сервиса
path_model=$(cat best_model.txt) #прочитать путь из файла в bash переменную 
mlflow models serve -m $path_model -p 5003 --no-conda & #запуск mlflow сервиса на порту 5003 в фоновом режиме
#------------------------

#4. healthy (status service)
curl http://127.0.0.1:5003/invocations -H "Content-Type: application/json" -d '{"inputs": [[0.98544899, 0.32362852, 0.97384268, 0.29808986, 0.03494213, 0]]}'


#Pipeline - для объедения задач в последовательный конвеер
#pipeline_cars
pipeline {
    agent any

    stages {
        stage('Download') {
            steps {
                build job: 'Download'
            }
        }
        
        stage ('Train') {
            steps {
                build job: 'Train model'
            }
        }
        
        stage ('Deploy') {
            steps {
                build job: 'Deploy'
            }
        }
        
        stage ('Status') {
            steps {
                build job: 'Healthcheck'
            }
        }
    }
}
