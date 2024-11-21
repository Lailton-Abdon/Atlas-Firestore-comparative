# atlas-firestore-comparative

This repository contains the codes developed for a Computer Science course completion article at UNIPÊ, with the goal of comparing the performance of the Firebase Firestore and MongoDB Atlas DBMS.

## Requirements

Python 3.10+

### Dependencies

firebase-admin  
pymongo  
requests  
datetime

## Usage

1. Clone this repository.  
2. Switch to one of the branches (`firebase-firestore` or `mongodb-atlas`).  
3. Install the dependencies:

        pip install firebase-admin pymongo requests

4. Configure the databases:

- **Firebase Firestore**: Add the Firebase credentials JSON file to the root directory of the project.  
- **MongoDB Atlas**: Insert the MongoDB Atlas connection string into the code.

5. Run the script:

        python main.py

## Functionalities

Inserts, reads, updates, and deletes data in Firebase Firestore and MongoDB Atlas.

### Exploratory functionalities:

- **MongoDB Atlas**: Counts the number of projects by area and adds the result to a new field in the database.  
- **Firebase Firestore**: Counts the number of participants who are or have been involved in projects within a specific time period and inserts an additional field with the result into the database.

## Project Structure

This repository is divided into two branches: `firebase-firestore`, containing the code developed for tests in Firebase Firestore, and `mongodb-atlas`, which contains the code developed for tests in MongoDB Atlas.

The codes are structured simply.
