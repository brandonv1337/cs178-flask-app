# Music Artist Management System

**CS178: Cloud and Database Systems - Project 1**

**Author:** Brandon Valadez

---
What your project does and what databases it uses
Technologies used
How to run it (setup instructions)
Screenshots of your working project
A description of how your SQL and DynamoDB databases are integrated
Your database schema (tables, keys, relationships)
A description of the CRUD operations you implemented
Any interesting challenges or insights
Citation of any AI tools used
## Overview

A web application for managing music artists and their track information. Users can add, update, delete, and view artists along with their associated tracks from a MySQL database. The application also stores artist preferences in DynamoDB for non-relational data persistence.

---

## Technologies Used

- **Flask** - Python web framework
- **AWS EC2** - hosts the running Flask application
- **AWS RDS (MySQL)** - relational database for storing artist, album, and track information
- **AWS DynamoDB** - non-relational database for storing artist genre preferences
- **GitHub Actions** - auto-deploys code from GitHub to EC2 on push

---

## Project Structure

```
cs178-flask-app/
    flaskapp.py
    dbCode.py
    creds.py
    templates/
        home.html
        add_user.html
        delete_user.html
        update_user.html
        display_users.html
        display_preferences.html
    .github/workflows/
        deploy.yml
    .gitignore
    README.md
```

---

## How to Run Locally

1. Clone the repository
2. Install dependencies: `pip3 install flask pymysql boto3`
3. Set up your credentials (see Credential Setup below)
4. Run the app: `python3 flaskapp.py`
5. Open your browser and go to `http://127.0.0.1:8080`

---

## How to Access in the Cloud

The app is deployed on an AWS EC2 instance. To view the live version:

```
http://[your-ec2-public-ip]:8080
```

---

## Credential Setup

This project requires a `creds.py` file that is not included in this repository for security reasons.

Create a file called `creds.py` in the project root with the following format:

```python
host = "your-rds-endpoint"
user = "admin"
password = "your-password"
db = "your-database-name"
```

---

## Database Design

### SQL (MySQL on RDS)

The project uses a music database with the following schema:

- **Artist** - stores artist information; primary key is `ArtistId`
- **Album** - stores album information; foreign key links to `Artist.ArtistId`
- **Track** - stores track information; foreign key links to `Album.AlbumId`

The JOIN query used in this project joins Artist, Album, and Track tables to display artist names with their associated track names and prices.

### DynamoDB

- **Table name:** `ArtistPreferences`
- **Partition key:** `ArtistName`
- **Used for:** Storing artist genre preferences as non-relational data

---

## CRUD Operations

| Operation | Route      | Description    |
| --------- | ---------- | -------------- |
| Create    | `/add-user` | Adds a new artist to MySQL and stores their genre preference in DynamoDB |
| Read      | `/display-users` | Displays artists and their tracks using a SQL JOIN query |
| Read      | `/display-preferences` | Displays all artist preferences from DynamoDB |
| Update    | `/update-user` | Updates artist name in MySQL and genre preference in DynamoDB |
| Delete    | `/delete-user` | Deletes artist from MySQL and removes preference from DynamoDB |

---

## Challenges and Insights

The most challenging aspect was integrating DynamoDB alongside MySQL, requiring different connection patterns and error handling for each database type. The project demonstrated the trade-offs between relational and non-relational databases, with MySQL providing structured querying through JOINs and DynamoDB offering flexible schema-less storage for preferences.
