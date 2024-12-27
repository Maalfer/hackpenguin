El objetivo de este proyecto es proporcionar un entorno dockerizado de Kali Linux con sus herramientas de hacking preconfiguradas, que se pueda desplegar automáticamente en el sistema y utilizar como máquina atacante. Para simplificar su gestión, se emplea un script en Bash que automatiza todo el proceso, eliminando la necesidad de poseer conocimientos previos sobre Docker.

El script utiliza la siguiente imagen de DockerHub para automatizar su despliegue:

```
https://hub.docker.com/repository/docker/maalfer/bountypentest/general
```

![image](https://github.com/user-attachments/assets/b1509631-99ce-4756-a81b-3ae129fc7847)


## PASO 1 - Ejecutar el script hackpenguin.py

Una vez ejecutado el script, se encargará de importar la máquina atacante en forma de imagen de docker, donde se nos mostrará por pantalla el comando que debemos de insertar para entrar dentro de dicha máquina atacante:

```
sudo bash hackpenguin.sh
```

![image](https://github.com/user-attachments/assets/8b159a0b-3a17-4e2d-8d06-a38da7d10482)


## PASO 2 - Ingresar a la Máquina Atacante

Para ingresas dentro de la máquina Kali atacante, copiamos y pegamos el comando que nos haya proporcionado previamente el script:

![image](https://github.com/user-attachments/assets/fc9918a7-544f-4164-9098-5dfeb27b4f47)


## PASO 3 - Cerrar y Limpiar el Sistema

Una vez hayamos terminado de usar la máquina atacante, podemos presionar control C en el script y él se encargará de eliminar la máquina atacante, aunque sin embargo no borrará la imagen de dicha máquina, para así conseguir que las próximas veces que usemos la máquina, esta se despliegue muy rápidamente.

![image](https://github.com/user-attachments/assets/96caed17-c6d4-4f09-840d-ce4beb253fd9)


## PASO 4 (opcional) - Limpieza Total

Si deseamos hacer una limpieza total y eliminar tanto el contenedor como la imagen de la máquina atacante, podemos usar el script con el parámetro --clean:
```
sudo python3 hackpenguin.py --clean
```

![image](https://github.com/user-attachments/assets/da03612b-351a-4000-aaa7-359bd84c6814)


-------------------------------------

**Menú de Ayuda**

El script cuenta con un menú de ayuda para guiar al usuario con su uso:

![image](https://github.com/user-attachments/assets/a9025b6a-4e8e-4e88-a5ef-f1163fc9bf5a)


