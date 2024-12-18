El objetivo de este proyecto es proporcionar un entorno dockerizado de Kali Linux con sus herramientas de hacking preconfiguradas, que se pueda desplegar automáticamente en el sistema y utilizar como máquina atacante. Para simplificar su gestión, se emplea un script en Bash que automatiza todo el proceso, eliminando la necesidad de poseer conocimientos previos sobre Docker.

## PASO 1 - Ejecutar el script hackpenguin.sh

Una vez ejecutado el script, se encargará de importar la máquina atacante en forma de imagen de docker, donde se nos mostrará por pantalla el comando que debemos de insertar para entrar dentro de dicha máquina atacante:

![image](https://github.com/user-attachments/assets/f3517403-9a03-42e0-befe-e93496179954)

## PASO 2 - Ingresar a la Máquina Atacante

Para ingresas dentro de la máquina Kali atacante, copiamos y pegamos el comando que nos haya proporcionado previamente el script:

![image](https://github.com/user-attachments/assets/154e1227-4868-4a8a-a486-4bf564740593)

## PASO 3 - Cerrar y Limpiar el Sistema

Una vez hayamos terminado de usar la máquina atacante, podemos presionar control C en el script y él se encargará de eliminar la máquina atacante, aunque sin embargo no borrará la imagen de dicha máquina, para así conseguir que las próximas veces que usemos la máquina, esta se despliegue muy rápidamente.

![image](https://github.com/user-attachments/assets/acefcca4-4899-4593-b5be-5ba2adc97271)

## PASO 4 (opcional) - Limpieza Total

Si deseamos hacer una limpieza total y eliminar tanto el contenedor como la imagen de la máquina atacante, podemos usar el script con el parámetro --clean:
```
sudo bash hackpenguin.sh --clean
```

-------------------------------------

**Menú de Ayuda**

El script cuenta con un menú de ayuda para guiar al usuario con su uso:

![image](https://github.com/user-attachments/assets/b26bcd8d-c2bb-4f55-bc7a-7d65ff458249)

