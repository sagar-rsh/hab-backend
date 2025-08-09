# HAB-Backend (User Service)

**Backend service for user authentication, subscription management, and access control in the Harmful Algal Bloom (HAB) Detection System.**

This service is built using **Python FastAPI** and acts as the **user-facing API gateway** to an external HAB prediction microservice.  
It handles authentication, subscription tier enforcement, request forwarding, and administrative functions.

---

## 📌 Features

- **User Authentication & Management**
  - Secure registration with password hashing
  - Login with JWT-based session tokens
  - Storage of user and subscription data in Google Cloud Firestore

- **Tiered Subscription System**
  - Free, Tier 1, and Tier 2 plans
  - API call limits enforced per tier
  - Premium features (image-based HAB detection) for Tier 1 & Tier 2

- **Prediction Request Proxy**
  - Validates user tier and call limits
  - Forwards authorized requests to the external prediction microservice
  - Supports:
    - Geospatial data predictions (all tiers)
    - Image-based predictions (Tier 1 & Tier 2 only)

- **Subscription Upgrade Workflow**
  - Users can submit upgrade requests via a financial aid form
  - Upgrade requests stored in Firestore for admin review
  - Admin approval updates user tier and access limits

- **Administrative Endpoints**
  - View all users, subscriptions, and pending upgrades
  - Approve or reject tier upgrade requests

---

## 🏗️ Architecture

The application is structured as follows:

```
app/
├── auth/                 # Authentication & authorization logic
├── models/               # Pydantic models for request/response validation
├── routers/              # Route handlers (auth, subscriptions, predictions, admin)
├── services/             # Business logic (e.g., prediction forwarding, tier enforcement)
├── database/             # Firestore integration
├── utils/                # Helper functions (JWT creation, password hashing, etc.)
└── main.py               # FastAPI entry point
```

---

## 🔄 Application Flow

1. **Registration & Login**
   - Register: create user & subscription records in Firestore (free tier, 0 calls used)
   - Login: verify credentials, issue JWT

2. **Authenticated Requests**
   - JWT is required in the `Authorization` header
   - Token validation is performed on every protected route

3. **Making a Prediction**
   - Check subscription tier & call usage
   - Forward request to prediction backend with API key
   - Increment usage count in Firestore
   - Return prediction result to user

4. **Subscription Upgrades**
   - User submits upgrade request (financial aid form)
   - Request stored in Firestore as `pending`

5. **Admin Review**
   - Admin views pending requests
   - Approve: tier is updated in Firestore
   - Reject: status updated, no tier change

---

## 🛠️ Technology Stack

- **FastAPI** – High-performance Python web framework
- **Google Cloud Firestore** – NoSQL database for users, subscriptions, and upgrades
- **JWT (JSON Web Token)** – Secure authentication
- **Passlib / bcrypt** – Password hashing
- **HTTPX / Requests** – Forwarding to external prediction API

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- Google Cloud account with Firestore enabled
- API key for external prediction service

### Clone Repository
```bash
git clone https://github.com/sagar-rsh/hab-backend.git
cd hab-backend
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the root directory:

```env
FIRESTORE_PROJECT_ID=your_project_id
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
PREDICTION_API_URL=https://example.com/predict
PREDICTION_API_KEY=your_prediction_api_key
```

### Run the Server
```bash
uvicorn app.main:app --reload
```
Access API docs at:  
**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

---

## 🔑 Example API Endpoints

| Method | Endpoint                     | Description                                         | Auth Required |
|--------|-------------------------------|-----------------------------------------------------|---------------|
| POST   | `/auth/register`              | Register a new user                                 | No            |
| POST   | `/auth/login`                 | Authenticate user & return JWT                      | No            |
| GET    | `/subscriptions/me`           | Get current subscription details                    | Yes           |
| POST   | `/predict/map`                | Make prediction from geospatial data                | Yes           |
| POST   | `/predict/image`              | Make image-based prediction (premium)               | Yes           |
| POST   | `/subscriptions/upgrade`      | Request subscription upgrade                        | Yes           |
| GET    | `/admin/users`                 | List all users (admin only)                         | Yes           |
| GET    | `/admin/upgrades`              | List pending upgrade requests (admin only)          | Yes           |
| PATCH  | `/admin/upgrades/{request_id}` | Approve or reject subscription upgrade request      | Yes           |

---

## 🧩 Related Repositories

- **Frontend:** [DV821/hab-frontend](https://github.com/DV821/hab-frontend)
- **Prediction Backend:** [danieli1245/Harmful-Algal-Bloom-Detection-System](https://github.com/danieli1245/Harmful-Algal-Bloom-Detection-System)
