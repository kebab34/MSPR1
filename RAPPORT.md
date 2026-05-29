RAPPORT
DE MSPR1
SARAH NIZAR, NATAEL OZTURK, NASSIM GHOULANE
HEALTHAI COACH
30/04/2026
02
03
SOMMAIRE
Choix technologiques
Architecture &
Flux de données
2.1: Langage & Framework backend
2.3: Pipeline ETL & traitement des données
2.2: Base de données
3.1: Vue d'ensemble de l'architecture
3.2: Pipeline de collecte et ingestion
01 Introduction
1.1: Introduction
04 Bilan du projet,
difficultés &
perspectives
4.1: Résultats obtenus :
4.2: Difficultés rencontrées & Solutions apportées :
4.1.1: Pipeline ETL fonctionnel
4.1.2: Base de données peuplée et validée
4.2.1: Problèmes liés aux sources de données
4.2.2: Difficultés techniques
4.1.3: API REST opérationnelle
4.1.4: Dashboard et indicateurs clés
4.2.3: Gestion du travail en équipe
05 Conclusion
5.1: Conclusion
4.3: Perspectives d'évolution :
2/21
1.2: L’équipe
1.3: Contexte du projet
2.4: API REST
2.5: Interface d'administration & Dashboard
2.6: Sources de données retenues
3.3: Processus de nettoyage et transformation
3.4: Modèle de données relationnel
3.5: Exposition via API
4.3.1: Améliorations techniques envisagées
4.3.2: 6.2 Intégration des modules IA
01 INTRODUCTION
01-Introduction
Dans un contexte où la santé connectée connaît une croissance
exponentielle, les solutions numériques de suivi personnalisé occupent une
place de plus en plus centrale dans le quotidien des utilisateurs. Face à
cette réalité, HealthAI Coach, jeune startup française, ambitionne de
proposer une plateforme digitale complète intégrant suivi nutritionnel,
accompagnement sportif et surveillance d'indicateurs de santé.
Dans le cadre de notre formation, notre équipe a été missionnée pour
concevoir et développer le backend métier de cette plateforme. Ce rapport
technique retrace l'ensemble de la démarche suivie : des choix
technologiques opérés jusqu'aux résultats obtenus, en passant par les
difficultés rencontrées et les perspectives d'évolution envisagées.
4/21
Natael a développé l'intégralité de l'interface web en Next.js
(TypeScript / React), avec ses 9 pages : accueil,
utilisateurs, aliments, exercices, journal alimentaire, sessions
sport, mesures biométriques, analytics et profil utilisateur. Il a
également assuré la configuration Docker Compose pour
l'orchestration des services et la mise en place de
l'environnement de développement local.
1.2 - L’équipe
Natael OZTURK
Interface d'administration & Dashboard
Nassim a conçu et développé l'API FastAPI, en structurant
l'architecture par ressource (routes, schémas Pydantic, accès
base de données). Il a mis en place le système
d'authentification JWT complet (register, login, middleware de
vérification des tokens) ainsi que la suite de 35 tests pytest
couvrant l'ensemble des endpoints.
API REST & authentification
Nassim GHOULANE
1.1 - Introduction
01-Introduction
1.2 - L’équipe
Sarah NIZAR
Base de données & Supabase
Sarah a pris en charge la modélisation et la mise en place de la
base de données. Elle a conçu le schéma relationnel (11 tables,
index, triggers), rédigé les migrations SQL et configuré
l'instance Supabase locale. Elle a également géré le pipeline
ETL : extraction des sources Kaggle et de l'API ExerciseDB,
transformation des données et chargement dans Supabase via
des scripts d'upsert.
5/21
1.3 - Contexte du projet
HealthAI Coach souhaite mettre en place une infrastructure technique
robuste capable de collecter, transformer et stocker des données
hétérogènes provenant de sources variées (APIs publiques, fichiers open
data, données biométriques simulées). L'objectif est double :
Disposer d'un référentiel de données fiable et de qualité, destiné à
alimenter les futurs algorithmes de recommandation personnalisée basés
sur l'intelligence artificielle.
Fournir aux équipes produit un tableau de bord interactif, permettant de
visualiser les indicateurs essentiels tels que la progression des
utilisateurs, les habitudes nutritionnelles et le suivi d'activité physique.
Le périmètre de notre mission couvre ainsi l'ensemble de la chaîne de
traitement de la donnée : de l'ingestion brute jusqu'à l'exposition via API et
la visualisation métier, dans une logique industrielle, sécurisée et
reproductible.
02 CHOIX
TECHNOLOGIQUES
Pour le backend, on a choisi Python 3. C'est un langage qu'on maîtrise tous dans
l'équipe et qui s'adapte bien à ce type de projet mêlant traitement de données et
développement web. Le fait que toute la stack (ETL, API, dashboard) soit en
Python nous a aussi permis de gagner du temps et d'éviter de jongler entre
plusieurs environnements.
Pour construire l'API, on a utilisé FastAPI. Ce framework nous a permis de
mettre en place une API REST rapidement, avec quelques avantages pratiques :
La validation des données est gérée automatiquement, ce qui évite beaucoup
d'erreurs
Une documentation interactive (Swagger) est générée automatiquement,
pratique pour tester les routes
Le code est lisible et bien structuré grâce au typage Python
L'API tourne avec Uvicorn, un serveur léger qui fonctionne aussi bien en local
qu'en conteneur Docker. On a aussi mis en place un middleware CORS pour que l'interface
Next.js puisse communiquer avec l'API sans problème.
02-Choix technologiques
2.1 - Langage & Framework backend
Pour stocker les données, on a choisi PostgreSQL, une base de données
relationnelle fiable et largement utilisée dans le milieu professionnel. On l'a
hébergée via Supabase, une plateforme qui simplifie la mise en place et la
gestion de PostgreSQL, avec en bonus des services utiles comme la gestion des
accès et une API intégrée. Pour un projet avec des contraintes de délai comme le
nôtre, c'était clairement le bon compromis.
La base est organisée autour des grandes entités du projet :
Utilisateurs et leurs objectifs
Aliments et journal alimentaire
Exercices et sessions sportives
Mesures biométriques (poids, fréquence cardiaque, sommeil)
Toutes ces tables sont reliées entre elles par des clés étrangères, ce qui garantit
la cohérence des données et facilite les requêtes pour le dashboard (historiques,
moyennes, indicateurs).
Pour accéder à la base depuis l'API et le pipeline ETL, on utilise le client Python
Supabase. On fait la distinction entre une clé publique pour les opérations
classiques et une clé de service pour les opérations d'administration. Une URL de
connexion PostgreSQL directe est aussi disponible dans la config du projet pour
les cas où on a besoin d'un accès SQL classique.
7/21
2.2 - Base de données
8/21
Pour alimenter la base de données, on a mis en place un pipeline ETL (Extract,
Transform, Load) en Python, avec la librairie pandas pour manipuler et nettoyer
les données. Chaque étape est tracée via des logs, ce qui permet de
diagnostiquer facilement les problèmes.
Extraction On récupère les données depuis deux types de sources :
Des fichiers CSV et Excel (datasets Kaggle : nutrition, membres de salle,
recommandations alimentaires)
Une API REST (ExerciseDB pour le catalogue d'exercices)
Un script dédié gère le téléchargement automatique des fichiers Kaggle via les
identifiants API.
Transformation C'est l'étape de nettoyage. On applique sur chaque source :
Suppression des doublons et gestion des valeurs manquantes
Vérification des colonnes obligatoires avant chargement
Mapping des champs pour correspondre au modèle de la base de données
Normalisation et restructuration des données selon les besoins métier
Chargement Les données nettoyées sont envoyées vers Supabase par lots pour
éviter les timeouts. On utilise un système d'upsert : si une donnée existe déjà
(par exemple un aliment ou un utilisateur), elle est mise à jour plutôt que
dupliquée. Ça garantit que la base reste propre même en cas de rechargement.
Orchestration L'enchaînement des étapes est géré par APScheduler, avec une
fréquence configurable via une variable d'environnement (par défaut tous les lundis à 02h00 UTC).
Le pipeline peut aussi être lancé manuellement pour les tests. Si une
source plante, les autres continuent de tourner, ce qui rend le système plus
robuste.
2.3 - Pipeline ETL & traitement des données
2.4 - API REST
L'API est construite avec FastAPI et toutes les routes sont préfixées par /api/v1.
Ce versionnement permet de faire évoluer l'API sans casser les applications qui
l'utilisent déjà. Tous les échanges se font en JSON, avec une validation
automatique des données grâce à Pydantic. La documentation est générée
automatiquement et accessible via Swagger et ReDoc directement depuis
l'application.
Les ressources disponibles L'API couvre l'ensemble des entités du projet :
Utilisateurs
Aliments & journal alimentaire
Exercices & sessions sportives
Mesures biométriques
Pour chaque ressource, on dispose des opérations classiques : consultation,
création, mise à jour et suppression. On peut aussi filtrer les listes par critères
(dates, recherche textuelle…). Un endpoint /health est également disponible pour
vérifier que l'API tourne correctement.
Authentification La gestion des accès passe par Supabase Auth. Un utilisateur
s'inscrit ou se connecte via /api/v1/auth, et reçoit en retour un token JWT qu'il
doit envoyer pour accéder aux routes protégées. Les routes publiques
(authentification, health check) restent accessibles sans token.
Lien avec la base de données Les contrôleurs communiquent directement avec
Supabase pour lire et écrire dans PostgreSQL. L'API est le point d'entrée unique
pour l'interface Next.js, les tests et tout autre client HTTP.
9/21
Pour l'interface, on est passés sur Next.js avec React et TypeScript. On avait
d'abord fait ça avec Streamlit, qui est bien pour aller vite, mais ça restait limité
visuellement. Avec Next.js on a pu faire un vrai site web, avec une page de
connexion, une navigation propre et un design qu'on a pu personnaliser.
Comment ça fonctionne — L'interface ne parle pas directement à la base de
données. Elle envoie ses requêtes à l'API FastAPI, exactement comme n'importe
quel autre client. Le token de connexion est automatiquement ajouté à chaque
appel, donc l'utilisateur n'a pas à s'en préoccuper.
Ce que l'interface propose :
Une page d'accueil avec un résumé : nombre d'aliments, d'exercices,
d'utilisateurs, et un indicateur qui montre si l'API répond bien
Des pages pour chaque partie du projet : utilisateurs, aliments, exercices,
journal alimentaire, sessions sportives, mesures biométriques
Une page profil où chaque utilisateur peut renseigner ses infos (poids,
taille, objectifs)
Une page Analytics avec des graphiques sur les données stockées
Connexion — On a une vraie page de login. Une fois connecté, l'accès est
maintenu et chaque utilisateur ne voit que ses propres données.
Côté design — On a choisi un thème sombre, sobre, qui rend bien sur écran. Les
pages s'adaptent aussi bien sur grand écran que sur un écran plus petit.
2.5 - Interface d'administration & Dashboard
2.6 - Sources de données retenues
LLes données utilisées dans la plateforme proviennent de sources externes
complémentaires, choisies pour couvrir les trois grands domaines du projet :
nutrition, activité physique et profils utilisateurs.
Exercices physiques On récupère les exercices depuis un fichier JSON public
hébergé sur GitHub (free-exercise-db), accessible sans authentification. Une
alternative via l'API ExerciseDB (RapidAPI) est aussi prévue si une clé API est
disponible. Cette double source évite de dépendre d'un seul fournisseur et
garantit un catalogue suffisant pour peupler la base (nom, type, groupe
musculaire, niveau, équipement…).
Aliments et valeurs nutritionnelles Le catalogue alimentaire vient du Daily Food
& Nutrition Dataset (Kaggle), fourni en CSV. Il contient les informations
nutritionnelles essentielles : calories, macronutriments, etc. Le téléchargement
peut être automatisé via l'API Kaggle avec un fichier de credentials kaggle.json.
Profils utilisateurs & mesures biométriques Le Gym Members Exercise Dataset
(Kaggle) nous sert à simuler une population d'utilisateurs avec un historique de
mesures réaliste : poids, fréquence cardiaque, sommeil, calories brûlées. C'est la
source principale pour alimenter les tables utilisateurs et mesures biométriques.
Objectifs nutritionnels Le Diet Recommendation Dataset (Kaggle) complète les
profils utilisateurs avec des attributs liés aux objectifs alimentaires et aux
recommandations diététiques, après transformation et intégration dans le
modèle relationnel.
En résumé
Toutes ces sources sont ré-ingérées périodiquement via le scheduler, avec une
stratégie d'upsert pour éviter les doublons et permettre des mises à jour
incrémentales.
Source Format Données
free-exercise-db / ExerciseDB JSON / API Exercices physiques
Daily Food & Nutrition Dataset CSV (Kaggle) Aliments & nutrition
Gym Members Exercise Dataset CSV (Kaggle) Utilisateurs & biométrie
Diet Recommendation Dataset CSV (Kaggle) Objectifs nutritionnels
10/21
03 ARCHITECTURE &
FLUX DE DONNÉES
03- Architecture & Flux
de données
La solution est organisée en quatre blocs principaux, faiblement couplés autour d'une
base de données commune :
1.Pipeline ETL (Python / pandas) — collecte les données externes, les nettoie et les
charge en base
2.Base de données — PostgreSQL hébergé via Supabase, point unique de stockage
pour toutes les entités métier
3.API REST (FastAPI) — expose les données et les opérations métier de façon
versionnée (/api/v1), avec gestion de l'authentification
4.Interface Next.js — application d'administration et de visualisation, qui passe
uniquement par l'API sans jamais accéder directement à la base
Les données circulent dans un sens simple : sources externes → base de données → API →
clients (dashboard, tests, applications tierces).
Ce découpage a un avantage concret : on peut faire évoluer une partie du système sans
tout casser. Ajouter une nouvelle source de données, changer le dashboard ou modifier
les règles d'accès n'impacte pas le reste.
En environnement Docker Compose, chaque service tourne dans son propre conteneur
avec ses dépendances et ses variables d'environnement. Ils communiquent entre eux via
un réseau interne (par exemple le service web appelle l'API via http://api:8000).
3.1 - Vue d'ensemble de l'architecture
12/21
3.2 - Pipeline de collecte et ingestion
La collecte des données se fait depuis plusieurs types de sources :
Fichiers CSV issus de Kaggle, placés dans le dossier etl/data/
Fichiers JSON pour les exercices (dépôt GitHub public ou API ExerciseDB)
Des connecteurs génériques Excel et API REST réutilisables pour de futures sources
Un script de téléchargement permet d'alimenter automatiquement le dossier de
données depuis Kaggle via un token d'authentification, sans intervention manuelle.
Orchestration L'enchaînement des étapes est géré par APScheduler avec une fréquence
configurable. Pour chaque source, le pipeline suit toujours le même ordre : extraction
→ transformation → chargement. Chaque source est isolée : si l'une plante, les autres
continuent de tourner et l'erreur est simplement journalisée.
Chargement Les données sont envoyées vers Supabase par lots pour éviter les timeouts.
On utilise une stratégie d'upsert sur des clés métier (nom d'aliment, email utilisateur) :
si une donnée existe déjà, elle est mise à jour plutôt que dupliquée. Ça permet de
relancer le pipeline plusieurs fois sans risquer de polluer la base.
3.3 - Processus de nettoyage et transformation
Entité Description
Utilisateur Profil principal (âge, sexe, poids, taille…)
Objectif Lié à l'utilisateur (perte de poids, prise de masse…)
Aliment Catalogue nutritionnel (calories, macronutriments…)
Journal alimentaire Lien utilisateur–aliment avec date et quantité
Exercice Catalogue d'activités physiques
Session sportive Séance réalisée par un utilisateur
Session–Exercice Table associative reliant sessions et exercices
Mesure biométrique
Données de suivi rattachées à l'utilisateur (poids, fréquence
cardiaque, sommeil…)
Une fois extraites, les données sont manipulées sous forme de DataFrames pandas.
L'objectif de cette étape est de garantir une qualité minimale avant tout chargement en
base.
Nettoyage On applique sur chaque source les traitements suivants :
Suppression des lignes entièrement vides
Gestion des doublons (y compris pour les colonnes contenant des listes)
Conversion des types de données pour correspondre au modèle relationnel
Transformation Chaque source est ensuite adaptée au schéma cible de la base :
Renommage et mapping des colonnes
Normalisation des valeurs (types d'exercices, niveaux, équipement…)
Ajout d'un champ "source" sur chaque enregistrement pour assurer la traçabilité des
données
Validation Avant tout chargement, on vérifie que les colonnes obligatoires sont bien
présentes. Par exemple :
nom pour les exercices
nom et calories pour les aliments
email pour les utilisateurs
Si une colonne manque, le chargement est bloqué et l'erreur est journalisée.
Cohérence référentielle Pour les sources qui produisent à la fois des utilisateurs et des
mesures biométriques, une étape de résolution d'identifiants est appliquée : on fait
correspondre l'email à l'id_utilisateur en base avant d'insérer les mesures, pour
garantir l'intégrité des relations.
13/21
3.4 - Modèle de données relationnel
Le modèle est centré sur l'utilisateur et l'ensemble de ses données de suivi. Les entités
principales sont les suivantes :
Les entités sont reliées entre elles par des clés primaires et étrangères, ce qui garantit
l'intégrité des données et formalise les cardinalités : un utilisateur possède plusieurs
mesures, plusieurs entrées de journal, plusieurs sessions, etc.
Ce schéma joue un rôle central dans le projet : c'est le contrat structurel partagé entre
les trois composants du système — l'ETL qui alimente la base, l'API qui lit et écrit les
données, et l'interface Next.js qui les affiche.
14/21
3.5 - Exposition via API
L'API traduit directement le modèle relationnel en ressources REST accessibles via des
routes claires :
/utilisateurs, /aliments, /exercices, /journal, /sessions, /mesures
Chaque ressource supporte les opérations HTTP standard (GET, POST, PUT, DELETE),
avec des paramètres de filtrage et de pagination. La documentation OpenAPI est
générée automatiquement et sert de référence pour les développeurs et les tests.
Authentification La gestion des identités passe par Supabase Auth et des tokens JWT.
On distingue deux niveaux d'accès :
Les utilisateurs finaux s'authentifient via inscription / connexion et obtiennent un
token JWT
Les accès techniques (pipeline ETL, administration) utilisent une clé de service
séparée
Cette séparation garantit que chaque composant accède uniquement à ce dont il a
besoin.
Rôle de l'API dans le système L'API est le point d'entrée unique pour tous les clients :
l'interface Next.js, les tests automatisés, et à terme l'application mobile. La base
de données reste le système de référence, mais personne n'y accède directement depuis
l'extérieur. Tout passe par l'API, ce qui centralise les règles d'accès et facilite les
évolutions futures.
04 BILAN DU PROJET,
DIFFICULTÉS &
PERSPECTIVES
4.1.2 - Base de données peuplée et validée :
La base PostgreSQL (hébergée via Supabase) a été alimentée avec des jeux représentatifs:
exercices, aliments, utilisateurs et mesures biométriques dérivées des sources retenues.
Le modèle relationnel (clés étrangères, entités métier) est respecté lors du chargement,
notamment lors du rattachement des mesures aux utilisateurs. La validation repose sur
des contrôles de schéma dans l’ETL (colonnes obligatoires) et, le cas échéant, sur des
tests automatisés ou des vérifications manuelles dans l’éditeur de tables.
L'objectif était de mettre en place une chaîne complète collecte → stockage →
exposition → visualisation dans le domaine de la santé connectée. Voici ce qu'on a livré
concrètement :
4.1.1 - Pipeline ETL fonctionnel :
Pipeline ETL fonctionnel Le pipeline est opérationnel et couvre l'ensemble du flux :
extraction depuis les sources (CSV, API, formats réutilisables), transformation
(nettoyage, mapping vers le schéma cible, validation) et chargement vers Supabase
(insertion par lots, upsert pour éviter les doublons). Un ordonnanceur permet de lancer
le pipeline automatiquement ou manuellement selon les besoins. Les logs confirment
que chaque source est traitée de façon séquentielle et que les erreurs sur une branche
n'bloquent pas les autres.
Figure 10 :Diagramme de cas d’utilisation général
4.1 - Résultats obtenus :
04-Bilan du projet,
difficultés & perspectives
16/21
17/21
4.1.3 - API REST opérationnelle :
Une API REST versionnée (/api/v1) expose les ressources principales du métier avec des
opérations de consultation et de gestion cohérentes avec le modèle de données. La
documentation OpenAPI (Swagger / ReDoc) est générée automatiquement, ce qui facilite
la prise en main et les tests. L’authentification (inscription, connexion, token JWT via
Supabase Auth) structure l’accès aux fonctionnalités sensibles. Un point de contrôle de
santé (health) permet de vérifier rapidement la disponibilité du service.
4.1.4 - Dashboard et indicateurs clés :
L'interface Next.js est accessible depuis un navigateur une fois connecté. La page
d'accueil affiche un résumé rapide : combien d'aliments, d'exercices et d'utilisateurs
sont en base, et si l'API fonctionne. Ensuite on a une page par entité pour consulter et
ajouter des données : journal alimentaire, sessions, mesures, etc. La page Analytics
montre quelques graphiques utiles, comme la répartition hommes/femmes, la
distribution des âges ou les aliments les plus caloriques. Tout ça sans jamais toucher
directement à la base, tout passe par l'API.
18/21
4.2 Difficultés rencontrées & Solutions apportées :
4.2.1 - Problèmes liés aux sources de données :
Les datasets Kaggle présentaient plusieurs problèmes : valeurs manquantes, colonnes
mal typées, formats de dates incohérents et absence d'identifiants uniques. Pour y
remédier, on a développé une chaîne de transformation robuste dans transform.py, avec
notamment la génération d'emails synthétiques uniques et une normalisation
systématique des types de données.
Lien entre mesures biométriques et utilisateurs Le dataset Gym Members ne faisait
aucun lien entre les données biométriques et les profils utilisateurs. On a résolu ça en
deux passes : on insère d'abord les utilisateurs en base, on récupère leurs UUIDs générés
par Supabase, puis on les utilise pour associer correctement les mesures biométriques.
Ce mapping email → UUID garantit la cohérence référentielle des données.
4.2.2 - Difficultés techniques :
Le principal problème technique a été la communication entre les conteneurs Docker et
Supabase tournant en local sur la machine hôte. Les conteneurs ne pouvaient pas
atteindre localhost depuis l'intérieur du réseau Docker. On a résolu ça en remplaçant
localhost par host.docker.internal dans les variables d'environnement, ce qui permet aux
conteneurs d'accéder aux services de la machine hôte sur Windows.
Installation du CLI Supabase Le CLI Supabase n'est pas supporté via npm sur Windows.
On a contourné le problème en passant par Scoop, un gestionnaire de paquets Windows,
ce qui a permis une installation propre sans conflit.
4.2.3 Gestion du travail en équipe :
Travailler à plusieurs sur le même dépôt a demandé une organisation rigoureuse. On a
adopté une convention de commits claire (feat:, fix:, refactor:) et on a réparti les
responsabilités par composant pour limiter les conflits Git. Des revues de code
régulières nous ont permis de garder une cohérence technique sur l'ensemble du projet.
19/21
4.3.2 - Intégration de modules d’intelligence artificielle :
L'évolution naturelle du projet serait d'ajouter des fonctionnalités intelligentes
directement exploitables par les utilisateurs de la plateforme :
Recommandation d'exercices et de plans nutritionnels personnalisés selon le profil
et les objectifs
Estimation des besoins nutritionnels à partir de l'historique et des mesures
biométriques
Détection d'anomalies sur les mesures (fréquence cardiaque, poids, sommeil…)
Assistant conversationnel branché sur les données agrégées et anonymisées de la
plateforme
Ces modules s'appuieraient sur l'API existante et des pipelines d'entraînement séparés
du flux transactionnel, pour ne pas impacter les performances du système en production.
Trois principes guideraient leur développement : respect de la vie privée, qualité des
données en entrée, et explicabilité des recommandations générées.
4.3.1 Améliorations techniques envisagées :
À moyen terme, plusieurs axes d'amélioration permettraient de renforcer la solution
pour un passage en production réel :
CI/CD : automatiser les tests et le déploiement à chaque push pour fiabiliser les
livraisons
Surveillance : mettre en place des logs centralisés et des alertes pour détecter
rapidement les anomalies
Tests : couvrir plus systématiquement l'API et le pipeline ETL avec des tests de nonrégression
Sécurité : appliquer strictement les politiques RLS (Row Level Security) de Supabase
et externaliser les secrets dans un gestionnaire dédié
Performances : ajouter des index SQL, affiner la pagination côté serveur et optimiser
le cache pour réduire la charge
Scalabilité : séparer les traitements batch (ETL planifié) des flux temps réel pour
mieux absorber la montée en volumétrie
4.3 Perspectives d’évolution :
05 CONCLUSION
05-Conclusion
Ce projet avait pour objectif de concevoir une plateforme
backend complète pour HealthAI Coach, capable de
collecter, structurer, stocker et exposer des données
hétérogènes, puis de les exploiter via une interface
d'administration et des indicateurs de suivi.
L'ensemble des livrables attendus a été mis en oeuvre de
façon cohérente : le pipeline ETL ingère et normalise les
données externes, le modèle relationnel PostgreSQL
garantit l'intégrité des entités métier, l'API FastAPI
centralise les accès, et l'interface Next.js permet la
visualisation et la gestion des données.
Sur le plan technique, ce projet nous a permis de mettre en
pratique des compétences concrètes : architecture
modulaire, nettoyage et validation des données,
intégration de services managés (Supabase,
authentification JWT), documentation API et
conteneurisation. Les difficultés rencontrées qualité
variable des sources, contraintes liées aux environnements
Docker, coordination en équipe ont été autant d'occasions
de renforcer la robustesse et la reproductibilité de la
solution.
La solution reste un prototype, avec les limites que ça
implique : volumétrie modérée, sécurité à renforcer pour un
passage en production, et fonctionnalités IA à venir.
Mais elle constitue une base technique solide et
maintenable, prête à évoluer vers une plateforme plus
complète intégrant des modules de recommandation
personnalisée et une montée en charge progressive.
21/21