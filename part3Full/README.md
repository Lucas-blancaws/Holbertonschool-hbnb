# HBnB Project – Enhanced Backend (Part 3)

This third stage of the HBnB project focuses on making the application functional, secure, and persistent by improving the backend.
We introduce authentication, role management, and a real database to replace the temporary in-memory storage from previous parts.

The overall objective is to move from a prototype to a reliable web application, ready for real deployment.


## Project Objectives:

__Authentication__ → Secure login using JWT tokens
__Authorization__ → Access restrictions based on the user role (is_admin)
__Database__ → Transition from in-memory storage → SQLite (development) → MySQL (production)
__ORM__ → Database management using SQLAlchemy
__CRUD__ → All entities are stored and retrieved persistently
__Relationships__ → Definition of the links between Users ↔ Places ↔ Reviews ↔ Amenities
__Documentation__ → Creation of a visual schema using Mermaid.js


## Security and User Management:

__Flask-Bcrypt__: Password hashing (no plain-text passwords are ever stored)

__Flask-JWT-Extended__: Token-based session management

__Role Control__: Certain endpoints are restricted to administrator users

Passwords are never returned in API responses


## Project Architecture:

<img width="527" height="469" alt="architecture projet" src="https://github.com/user-attachments/assets/ce1961f5-be63-4148-bf68-029aac914bbc" />

In the file persistence/repository.py, the storage layer is no longer an in-memory repository: it has been replaced by an actual database implementation.


## Database & ORM:

SQLAlchemy manages tables, relations, and queries.

SQLite is used during development (simple and portable).

The project is ready to switch to MySQL in production.


Main Relationships:

A User can own several Places and write several Reviews

A Place is linked to one User and receives several Reviews

A Review connects a user to a place

An Amenity can belong to several places via an association table


## ER Diagram (Mermaid.js):

The ER diagram shows the structure of the database used in the HBnB application.
It represents the main tables and their relationships, making it easy to understand how the data is organized.


__What the diagram shows__:

User: A user can create multiple Places and write multiple Reviews.

Place: A place belongs to a specific user, can receive multiple reviews, and can offer several Amenities.

Review: Connects a user to a place (a user leaves a review about a place).

Amenity: A feature or service (e.g., Wi-Fi, parking, pool) that can be associated with multiple places.

Place_Amenity: An association table that enables the many-to-many relationship between Place and Amenity.


__Why it is useful__:

It helps visualize how data is linked.

It simplifies the creation and understanding of database models in the code.

It provides a solid foundation for writing correct and consistent queries.

<img width="636" height="707" alt="Diagramme Task 10" src="https://github.com/user-attachments/assets/6c83a312-3dd1-426a-a664-2640ec134b7e" />


## Installation & Execution:

__Install dependencies__:

python3 -m pip install -r requirements.txt


__Run the server__:

python3 run.py

It is recommended to use a virtual environment (venv).

## Tests:

(To be completed when final validation and test integration are done.)

## Authors:

- Lucas Blancportier

- Grégory Sala
