
# BookMyTigger - Alert Tracker 

## Overview 

This is a trigger management system for cryptocurrencies/stocks/commodities, built using Django, PostgreSQL, and several additional technologies. It allows users to create triggers for trackable entities' prices, receive alerts via email, and view price charts live.

## Running the Project 

### Prerequisites 
 
- **Docker** 
-  **Docker Compose** 

### Steps to Run the Project 
 
1. **Clone the Repository** 

```bash
git clone <https://github.com/subh-chaturvedi/BookMyTrigger>
cd <BookMyTrigger>
```
 
2. **Build and Start Docker Containers** 

```bash
docker-compose up --build
```

This command builds the Docker images and starts the containers for your Django application, Redis, RabbitMQ, and PostgreSQL.
 
3. **Run Migrations** 
After the containers are up, you need to apply the database migrations:


```bash
docker-compose exec web python manage.py migrate
```
 
4. **Create a Superuser (Optional)** 
To access the Django admin interface, create a superuser:


```bash
docker-compose exec web python manage.py createsuperuser
```
 
5. **Access the Application**  
  - **Django Application** : `http://localhost:8000`
 
  - **RabbitMQ Management Interface** : `http://localhost:15672` (username: `guest`, password: `guest`)

## Technologies Used 
 
- **Django** : Web framework for building the application.
 
- **PostgreSQL** : Database for storing user data and triggers.
 
- **Binance WebSocket API** : For real-time price updates.
 
- **Celery** : For handling asynchronous tasks.
 
- **RabbitMQ** : Message broker for Celery.
 
- **TradingView** : For embeddable financial charts.
 
- **Redis** : Caching layer for API responses.

## System Architecture 

*Picture here.* 
 
1. **Django Application** :
  - Handles user authentication using JWT, trigger management, and API endpoints.

  - Uses Django REST framework for building API endpoints.
 
2. **PostgreSQL** :
  - Stores user information, triggers, and other persistent data.
 
3. **Binance WebSocket** :
  - Streams real-time cryptocurrency prices to the Django application.

  - Listens for price updates and triggers alerts when conditions are met.
 
4. **Celery** :
  - Manages asynchronous tasks such as sending email notifications.

  - Workers execute tasks from the queue and store results in Redis.
 
5. **RabbitMQ** :
  - Acts as the message broker for Celery.

  - Manages task queues and ensures reliable delivery of tasks to Celery workers.
 
6. **Redis** :
  - Configured as the Result Backend for celery.

  - Also used for caching API responses to reduce database load and improve performance.

  - Stores task results for quick access and real-time monitoring of task statuses.
 
7. **Frontend Interface** :
  - Allows users to log in, view, create, and delete triggers.

  - Displays a BTC price chart using TradingView or Matplotlib-generated images.


## API Endpoints 


## Overview 

This API provides endpoints for managing user accounts, setting and deleting alerts, and retrieving alert information. It includes endpoints for user authentication, alert management, and fetching alert statuses with pagination and filtering.

## Authentication 
All endpoints except those for registration and login require authentication via JWT (JSON Web Token). Include the token in the `Authorization` header as `Bearer <jwt-token>`.
## Endpoints 

### User Management 
1. **Register User**  
- **Endpoint** : `POST /api/register/`
 
- **Description** : Registers a new user in the system.
 
- **Request Body** :

```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```
 
- **Response** : 
  - **Status Code** : `201 Created`
 
  - **Body** :

```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```
 
- **Errors** : 
  - `400 Bad Request`: Validation errors or missing required fields.
2. **Login User**  
- **Endpoint** : `POST /api/login/`
 
- **Description** : Authenticates a user and returns a JWT for subsequent requests.
 
- **Request Body** :

```json
{
  "username": "string",
  "password": "string"
}
```
 
- **Response** : 
  - **Status Code** : `200 OK`
 
  - **Body** :

```json
{
  "access": "jwt-token",
  "refresh": "refresh-token"
}
```
 
- **Errors** : 
  - `401 Unauthorized`: Invalid credentials.

### Alert Management 
1. **Create Alert Trigger**  
- **Endpoint** : `POST /api/alerts/create/`
 
- **Description** : Creates a new alert trigger for the authenticated user.
 
- **Headers** : 
  - `Authorization: Bearer <jwt-token>`
 
- **Request Body** :

```json
{
  "trigger_value": "integer"
}
```
 
- **Response** : 
  - **Status Code** : `201 Created`
 
  - **Body** :

```json
{
  "id": 1,
  "trigger_value": 50000,
  "status": "created"
}
```
 
- **Errors** : 
  - `400 Bad Request`: Invalid trigger value or other validation errors.
 
  - `401 Unauthorized`: Invalid or missing JWT token.
 2. **Delete Alert Trigger**  
- **Endpoint** : `DELETE /api/alerts/delete/{id}/`
 
- **Description** : Deletes an existing alert trigger for the authenticated user.
 
- **Headers** : 
  - `Authorization: Bearer <jwt-token>`
 
- **URL Parameters** : 
  - `id`: ID of the alert trigger to delete.
 
- **Response** : 
  - **Status Code** : `200 OK`
 
  - **Body** :

```json
{
  "message": "Alert deleted successfully"
}
```
 
- **Errors** : 
  - `404 Not Found`: Alert trigger with the specified ID does not exist.
 
  - `401 Unauthorized`: Invalid or missing JWT token.
3. **Fetch Alerts**  
- **Endpoint** : `GET /api/alerts/`
 
- **Description** : Retrieves all alert triggers for the authenticated user with optional filtering and pagination.
 
- **Headers** : 
  - `Authorization: Bearer <jwt-token>`
 
- **Query Parameters** : 
  - `status` (optional): Filter alerts by status (e.g., `created`, `triggered`).
 
  - `page` (optional): Page number for pagination (default is 1).
 
  - `page_size` (optional): Number of alerts per page (default is 10).
 
- **Response** : 
  - **Status Code** : `200 OK`
 
  - **Body** :

```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "trigger_value": 50000,
      "status": "triggered"
    }
  ]
}
```
 
- **Errors** : 
  - `401 Unauthorized`: Invalid or missing JWT token.

## Alerts Notification System 

Currently, I have only added functionality to track BTC prices.

The system monitors Bitcoin (BTC) price in real-time using Binance WebSocket. Alerts are generated when the price crosses user-defined trigger values. Alerts are then printed to the command line and sent via email.

### Real-Time Price Monitoring 
 
1. **WebSocket Connection** : Establishes a connection to the Binance WebSocket API to receive real-time BTC price updates.
 
2. **Trigger Comparison** : Compares incoming price updates with stored user triggers.
 
3. **Alert Generation** : 
  - **Console Output** : Prints alerts to the terminal when price triggers are met.
 
  - **Email Notification** : Sends email notifications to users using Celery and RabbitMQ.

### Email Notification System 

*email image*
 
1. **Celery Worker** : Handles background tasks, such as sending email notifications, asynchronously.
 
2. **RabbitMQ** : Acts as the message broker for Celery tasks.
 
3. **Email Sending** : 
  - The `send_email` task is enqueued by Celery when a price trigger is activated.

  - Emails are sent using the SMTP backend configured in Django settings.
  
## Frontend 

### User Interface 

*another image*
 
- **Triggers Management** : Users can view, create, and delete triggers through the front-end.
 
- **BTC Price Chart** : Displays real-time BTC price data using TradingView widgets.

