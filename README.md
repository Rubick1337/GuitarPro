# GuitarPro

GuitarPro is split into two independent Python applications:

- **`server/`** – a FastAPI backend that exposes authentication and profile endpoints secured by JWT tokens.
- **`client/`** – a Kivy desktop client that authenticates against the backend and displays profile data using modularised UI components.

## Architecture

```
GuitarPro/
├── server/
│   ├── auth.py          # JWT helpers (hashing, token generation/validation)
│   ├── main.py          # FastAPI application with auth + profile endpoints
│   ├── schemas.py       # Pydantic request/response models
│   ├── storage.py       # In-memory user repository
│   └── requirements.txt # Backend dependencies
├── client/
│   ├── app.py           # Kivy entry point and screen manager
│   ├── state.py         # Shared application state
│   ├── components/
│   │   ├── home.py      # Home screen (profile display + logout)
│   │   ├── login.py     # Login screen + form widgets
│   │   └── messages.py  # Reusable message list widget
│   ├── services/
│   │   └── api.py       # REST client that talks to the FastAPI server
│   └── requirements.txt # Client dependencies
└── README.md
```

The backend uses FastAPI with OAuth2 password flow and JWTs (PyJWT) to protect private endpoints. Users are stored in memory for demonstration purposes; replace `UserRepository` with your database layer for production.

The Kivy client is split into small, reusable components:

- `LoginScreen` manages authentication and token storage.
- `HomeScreen` renders user information and supports logout/refresh actions.
- `MessageList` is a simple widget for surfacing server/client feedback.

Shared state lives in `client/state.py`, while HTTP calls are delegated to `client/services/api.py`.

## Installation

> All commands assume Python 3.11+ and that you are working in a virtual environment.

### 1. Backend (FastAPI)

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn server.main:app --reload
```

The API will be available at <http://127.0.0.1:8000>. You can register/login via the `/auth/register` and `/auth/login` endpoints and fetch profile data from `/profile` using the returned JWT access token.

### 2. Client (Kivy)

In a second terminal:

```bash
cd client
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m client.app
```

The client will prompt for credentials. Use the same username/password that you registered through the backend. Once authenticated, the token is stored in shared state and used to load the profile screen.

## Environment Variables

For quick experimentation the JWT secret is hard-coded. Override it in production by exporting `GUITARPRO_SECRET_KEY` and updating `server/main.py` to read from `os.environ`.

## Development Tips

- Run `uvicorn server.main:app --reload` during development for automatic backend reloads.
- Use tools like [HTTPie](https://httpie.io/) or [curl](https://curl.se/) to inspect API responses.
- Kivy supports `.kv` language files if you prefer declarative UI definitions; current components are pure Python for brevity.
