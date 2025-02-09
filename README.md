# Document Classification Application

This repository contains a document classification application built with an Angular frontend and a FastAPI backend. It allows users to upload documents, classify them, and view previously uploaded documents.

## Setup and Run Instructions

### Prerequisites

* Node.js and npm (or yarn) installed (if you want to run the frontend independently).
* Python 3.9 or higher (if you want to run the backend independently).

### Running Frontend Independently (Recommended For Development)

1. Navigate to the frontend directory:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Start the development server:

    ```bash
    ng serve
    ```

4. Access the application:

    Open your web browser and go to `http://localhost:4200`.  
    Note: You'll need to have the backend running separately for the frontend to function correctly.

### Running Backend Independently ( Recommended For Development)

1. Navigate to the backend directory:

    ```bash
    cd backend
    ```

2. Create a virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Start the FastAPI server:

    ```bash
    uvicorn main:app --reload
    ```

## API Documentation

If you are running the application locally, you can access the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## Architectural Decisions and Features

* **Frontend:** Angular was chosen for the frontend due to its component-based architecture, which allows for fast UI development and also future growth. It also simplies data binding across the model and view and has built-in HTTP requests for easy API integration.
* **Backend:** FastAPI and Python have key benefits including ease of use, automatic API documentation generation and access to many ML libraries. The backend code is split to modular files to promote singular responsibility and easy testing and debugging.
* **Database:** SQLite was used for simplicity in this example since it can run without a server. For production, a more robust database like PostgreSQL is recommended.
* **Model:** `facebook/bart-large-mnli` was chosen for zero-shot classification due to its performance with limited resources, but newer, cloud-based models would be recommended for production.
* **Testing** Unit tests were implemented for the backend to test basic programmatic flow and functionality.

## Future Improvements

* **Database:** Migrate to a production-ready database like PostgreSQL.
* **Explore Different Classification Models:** Explore newer models with higher confidence scores.
* **Previous File Download:** Allow the user to download previously categorised files from the UI.
* **Multiple File Upload:** Users should be able to upload multiple files at once and view all results.
* **Testing:** Add integration testing, as well as UAT/behavioural tests for the frontend.
* **Deployment:** Implement a proper deployment pipeline for production environments.

## ML Considerations

After testing various models, I chose to use the facebook/bart-large-mnli model. I compared to the valhalla/distilbart-mnli-12-3 model, which I first considered due to being less resource intensive on a local environment, but realised it was giving very poor confidence scores. I then experimented with newer models including roberta-large and allenai/led-base-16384, but these did not improve the score and were considerably slower. In a production environment, I would recommend a cloud-based, newer model trained specifically for classification to provide better results.

Chunking was implemented to manage large files.

Low confidence scores are now highlighted in RAG colours for the user's benefit. Low confidence scores could also be managed by categorising those files as 'Other'. I would also recommend falling back (potentially) to a rule-based system in extreme examples.

## Demo

You can download a demo video of the application [here](./media/application-demo.mp4).

To run the demo locally, follow the "Setup and Run Instructions" above.
