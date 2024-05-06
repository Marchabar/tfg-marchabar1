# AIVigilant

AIVigilant es una aplicación web que permite mostrar estadísticas, gráficos, tablas y resúmenes de discursos políticos con inteligencia artificial.

![Página de inicio](/static/images/landing-page.png)

# Manual de Instalación

Los pasos necesarios para instalar las herramientas y componentes necesarios para el desarrollo del proyecto son:

## Requisitos de hardware

Los requisitos de hardware necesarios para la instalación del proyecto son los siguientes:

| Requisitos de hardware      | Mínimos                           | Recomendados                   |
|------------------------------|-----------------------------------|--------------------------------|
| Procesador                   | 2 núcleos a 1GHz o más           | AMD Ryzen 7 3700 o Intel i7 10700 |
| RAM                          | 1Gb de RAM                       | 16GB de RAM                    |
| Almacenamiento               | 250GB de HHD                     | 512GB de SSD                   |
| Sistema Operativo            | Windows 7                        | Windows 11                     |

## Requisitos de software

Para poder instalar y hacer uso del sistema correctamente es necesario tener instalado en su máquina local lo siguiente:

- **Python**: en este caso para el desarrollo del proyecto se ha hecho uso de Python 3.11.2. Puede instalarlo desde [aquí](https://www.python.org/downloads/release/python-3112/).
- **Entorno de desarrollo integrado (IDE)**: el IDE del que se ha hecho uso para el proyecto de VSCode, en su caso elija el IDE que más le guste. Puede instalar VSCode desde [aquí](https://code.visualstudio.com/download).
- **Git**: es necesario que instale git para poder acceder y clonar el repositorio del proyecto. Puede instalarlo desde [aquí](https://git-scm.com/downloads).

Una vez que tenga todo instalado, ya puede proceder con la instalación del proyecto.

## Proceso de instalación

Debido a que el proyecto se ha desarrollado con VSCode, este proceso de instalación va a realizarse en este IDE. Igualmente, en el resto de IDEs debería seguirse un proceso muy similar. Los pasos a seguir son:

1. **Clonar el repositorio**: el repositorio de GitHub está accesible [aquí](https://github.com/Marchabar/tfg-marchabar1). Para clonarlo, copie y pegue el siguiente comando en la terminal de su IDE:

    ```bash
    git clone https://github.com/Marchabar/tfg-marchabar1.git
    ```

    Guarde el repositorio donde desee en su máquina local y continúe con el siguiente paso.

2. **Crear un entorno virtual**: en el directorio raíz de su proyecto, cree un entorno virtual para instalar las dependencias del proyecto de forma aislada. Para ello diríjase a la ubicación del repositorio desde la terminal y una vez allí ejecute:

    ```bash
    python3 -m venv env
    ```

    Esto creará un nuevo entorno virtual en un directorio llamado `env` dentro del proyecto.

3. **Activar el entorno virtual**: para activar el entorno virtual, ejecute el siguiente comando:

    - En Windows:
        ```bash
        env\Scripts\activate
        ```

    - En macOS y Linux:
        ```bash
        source env/bin/activate
        ```

4. **Instalar dependencias del proyecto**: una vez que el entorno virtual está activado, instale las dependencias del proyecto desde el archivo `requirements.txt`. Para ello ejecute:

    ```bash
    pip install -r requirements.txt
    ```

    Esto llevará un tiempo, debido a que el proyecto cuenta con bastantes dependencias.

5. **Configuración de la base de datos PostgreSQL**: descargue e instale el instalador de PostgreSQL desde [aquí](https://www.postgresql.org/download/windows/), asegurándose de seleccionar la opción para instalar PgAdmin, que es una herramienta de administración de base de datos para PostgreSQL.

    Para configurar PostgreSQL durante la instalación, se le pedirá que configure una contraseña para el usuario predeterminado. Asegúrese de recordar esta contraseña, ya que la necesitará más tarde.

    Una vez instalado, abra PgAdmin. Una vez abierto, haga click en el icono de "Add New Server" en la barra de herramienta o en el menú "File". Complete los detalles de conexión, con el nombre del servidor, el nombre del host (`localhost`), el nombre de usuario (`postgres` por defecto) y la contraseña que configuró durante la instalación.

    Una vez conectado, haga click con el botón derecho en el servidor que acaba de agregar y selecciona `Create` > `Database`. Asigne un nombre a su base de datos y confirme la creación.

6. **Obtener las variables de entorno**: en su IDE, dentro de la carpeta `Graphpol` cree un archivo llamado `.env`. Este archivo contendrá las variables de entorno necesarias para el correcto funcionamiento del sistema.

    Las variables de entorno a definir son las siguientes:

    ```bash
    DB_NAME=<nombre_de_la_base_de_datos_de_pgadmin>
    DB_USER=postgres
    DB_PASSWORD=<contraseña_de_instalacion_de_pgadmin>
    DB_HOST=localhost
    SECRET_KEY=<cadena_aleatoria_de_al_menos_50_caracteres>
    YOUTUBE_API_KEY=<obtener_de_youtube_data_api_v3>
    ```

    La clave de Youtube puede obtenerse de manera gratuita siguiendo [este](https://blog.hubspot.com/website/how-to-get-youtube-api-key) tutorial. Para la clave de OpenAI necesita crear una cuenta [aquí](https://platform.openai.com/docs/quickstart) y solicitar la clave, este proceso no es gratuito. En este proyecto se ha utilizado una clave obtenida por el Departamento de Lenguajes y Sistemas Informáticos de la ETSII.

7. **Popular base de datos**: de nuevo en la terminal con el entorno virtual activado, ejecute los siguiente comandos para popular la base de datos:

    ```bash
    python manage.py migrate
    python manage.py load_video_json
    python manage.py load_sentiment_json
    python manage.py load_language_json
    python manage.py load_words_json
    python manage.py load_topics_json
    python manage.py load_falacies_json
    ```

8. **Ejecutar la aplicación**: si ha realizado los pasos previos de manera correcta, puede ejecutar el siguiente comando:

    ```bash
    python manage.py runserver
    ```

    Esto iniciará el servidor de desarrollo y podrá acceder a la aplicación desde un navegador en [http://localhost:8000](http://localhost:8000).
