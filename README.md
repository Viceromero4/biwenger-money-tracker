# Biwenger Money Tracker

Full-stack application for tracking and reconstructing participant balances in private Biwenger leagues.

The project was created to solve a real limitation I encountered while playing Biwenger: although the platform shows transfers and economic activity in the league feed, it does not directly show how much money the other participants currently have available.

Biwenger Money Tracker processes those economic events and reconstructs each participant's balance automatically.

## The Problem

Before developing this application, I tracked league balances manually using an Excel spreadsheet.

Every purchase, sale, bonus or other economic movement had to be entered manually. Excel formulas then calculated the estimated balance of each participant.

Although the system worked, it had several limitations:

- Movements had to be entered manually.
- Maintaining several leagues was difficult.
- Human errors could cause incorrect balances.
- It was difficult to inspect the complete history of a participant.
- The solution was not scalable or easily reusable.

The goal of this project was to transform that spreadsheet-based workflow into a real full-stack application.

## The Solution

Biwenger Money Tracker synchronizes the economic activity of a private Biwenger league and converts the events into normalized movements stored in a PostgreSQL database.

The balance of every participant can then be reconstructed using:

```text
Current balance = Initial balance + Sum of economic movements
```

The application supports multiple leagues independently, each with its own participants, movements, synchronization state and balances.

## Main Features

- Multiple Biwenger league support
- Automatic participant synchronization
- Automatic economic movement synchronization
- Exact participant balance reconstruction
- Incremental synchronization
- Duplicate movement prevention
- League selector
- Participant balance dashboard
- Complete movement history
- Individual participant detail pages
- Manual synchronization from the frontend
- Exact currency values without rounding

## Supported Economic Events

The synchronization system currently handles the main economic operations that can affect a participant's balance.

### Market purchases

When a participant buys a player from the market, the purchase price is deducted from their balance.

### Market sales

When a participant sells a player to the market, the sale amount is added to their balance.

### Bonuses

Manual or automatic bonuses are added to the corresponding participant.

### Round payments

Biwenger payments associated with completed rounds are imported automatically.

The system also handles later corrections to a round payment without duplicating the original movement.

### Clause increases

Money spent increasing a player's release clause is registered as an economic movement.

### Clause transfers

When a player is acquired from another participant through a release clause, the operation affects both participants:

```text
Seller  + transfer amount
Buyer   - transfer amount
```

### Loans

Loans between participants generate economic movements for both sides.

```text
Owner      + loan amount
Borrower   - loan amount
```

### Loan returns

Biwenger generates a separate `loanReturn` event when a refundable loan ends.

The application processes this event and reverses the corresponding economic operation:

```text
Borrower   + refund
Owner      - refund
```

### Adjustments

Adjustments can be registered when a balance needs to be corrected manually.

## Synchronization

One of the main challenges of the project was making synchronization safe to execute multiple times.

Each imported movement receives an `external_key` generated from information from the original Biwenger event.

This allows the application to identify movements that have already been imported and prevents duplicate economic operations.

The application also stores a synchronization timestamp for each league.

This makes it possible to perform incremental synchronizations instead of processing the entire league history every time.

## Round Payment Corrections

Some Biwenger events can be modified after their initial publication.

For example, a round can initially generate a payment and later receive a correction because postponed matches have been completed.

Instead of treating both events as independent payments, the application identifies that they belong to the same logical round payment and updates the existing movement.

This prevents the participant from receiving the same round payment twice.

## Architecture

The project follows a separated frontend/backend architecture.

```text
Biwenger
    |
    v
Biwenger Client
    |
    v
Event Parser
    |
    v
Synchronization Service
    |
    v
PostgreSQL
    |
    v
FastAPI REST API
    |
    v
React Frontend
```

### Backend

The backend is responsible for:

- Communicating with Biwenger
- Parsing external events
- Applying economic rules
- Synchronizing participants
- Preventing duplicate movements
- Storing data
- Calculating balances
- Exposing the REST API

### Frontend

The frontend consumes the FastAPI API and provides the user interface for:

- Selecting a league
- Viewing participant balances
- Synchronizing league data
- Viewing economic movements
- Inspecting the movement history of individual participants

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic

### Frontend

- React
- Vite
- JavaScript
- CSS
- React Router

### Development Tools

- Git
- GitHub
- Visual Studio Code
- pgAdmin
- PowerShell

## Project Structure

```text
biwenger-money-tracker/
|
|-- backend/
|   |-- alembic/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- integrations/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |
|   |-- scripts/
|   |-- .env.example
|   `-- requirements.txt
|
|-- frontend/
|   |-- public/
|   `-- src/
|       |-- components/
|       |-- context/
|       |-- pages/
|       |-- services/
|       `-- utils/
|
`-- README.md
```

## Database

PostgreSQL is used as the main relational database.

Alembic manages database schema migrations.

The main domain concepts include:

- Leagues
- Seasons
- Participants
- League participants
- Movements

Economic movements are stored independently instead of storing only the resulting balance.

This means participant balances can always be reconstructed from their initial balance and movement history.

## API

The backend exposes a REST API using FastAPI.

The main resources include:

```text
/leagues
/participants
/movements
/balances
/dashboard
/transfers
```

The API also provides functionality for synchronizing a league with Biwenger.

FastAPI automatically provides interactive API documentation while the backend is running.

## Environment Variables

Sensitive information is not stored in the repository.

Create a local `.env` file inside the backend using `.env.example` as a template.

Example:

```env
DATABASE_URL=postgresql+psycopg://biwenger_app:CHANGE_ME@localhost:5432/biwenger_tracker

BIWENGER_LEAGUE_ID=YOUR_LEAGUE_ID
BIWENGER_USER_ID=YOUR_USER_ID
BIWENGER_TOKEN=YOUR_BIWENGER_TOKEN
```

The real `.env` file is excluded from Git.

## Running the Project Locally

### Backend

Move to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment and install the dependencies:

```bash
pip install -r requirements.txt
```

Configure the `.env` file and apply the database migrations:

```bash
alembic upgrade head
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

### Frontend

Move to the frontend directory:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

## Validation

The application has been tested using multiple real private Biwenger leagues.

The balances reconstructed from the imported economic movements were compared against the balances displayed directly by Biwenger.

The final calculated balances matched the real balances after processing the supported economic operations.

This validation was particularly useful for detecting special cases such as:

- Corrected round payments
- Transfers between participants
- Release clauses
- Loans
- Refundable loan returns

## Technical Challenges

Some of the most interesting technical challenges during development were:

- Understanding undocumented Biwenger event structures
- Converting external events into a consistent internal movement model
- Handling operations involving two participants
- Preventing duplicate imports
- Supporting incremental synchronization
- Processing corrected events
- Resolving player identifiers into readable player names
- Maintaining independent synchronization states for multiple leagues

Rather than assuming how undocumented events worked, real event data was inspected and used to define the corresponding economic rules.

## Project Status

The core version of Biwenger Money Tracker is complete and functional.

The current version supports multiple leagues, automatic synchronization and the economic operations required to reconstruct participant balances accurately.

## Possible Future Improvements

The project can be extended with features such as:

- Automatic scheduled synchronization
- Balance evolution charts
- Advanced movement filters
- Participant spending statistics
- League statistics
- Authentication
- Production deployment
- Improved responsive design
- Automated testing

## Motivation

This project was developed both to solve a real problem and as a full-stack development learning project.

It allowed me to work with a real use case involving external data, undocumented event structures, database modelling and synchronization instead of building a predefined tutorial application.

The project helped me strengthen my knowledge of:

- Python backend development
- FastAPI
- REST API design
- PostgreSQL
- SQLAlchemy
- Database migrations with Alembic
- React
- External API integration
- Data parsing
- Synchronization strategies
- Git and GitHub
- Full-stack application architecture

## Disclaimer

This is an independent personal project created for educational and portfolio purposes.

It is not affiliated with, endorsed by, or officially connected to Biwenger.
