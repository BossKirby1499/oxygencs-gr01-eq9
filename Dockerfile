# Utilisez une image de base Python. Choisissez la version qui correspond à votre projet.
FROM python:3.6-alpine

# Définit le répertoire de travail dans le conteneur à /app
WORKDIR /app

# Copie le fichier requirements.txt dans le conteneur
COPY ./src/requirements.txt .

# Installe les dépendances listées dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du dossier src dans le conteneur
COPY ./src .

# Commande pour exécuter l'application Python
CMD ["python", "./main.py"]