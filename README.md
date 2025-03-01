# RAG for personal Google Drive data
<div align="center">
  <!-- Backend -->
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" />

</div>

This repository demonstrates Retrieval Augmented Generation (RAG) using data retrieved from Google Drive.

## Getting Started

Follow these steps to set up and run the demonstration:

**1. Environment Setup:**

   * **Create a Conda environment (recommended):**
      ```bash
      conda create -n rag-gdrive python=3.9  # Or your preferred Python version
      conda activate rag-gdrive
      ```
   * **Install dependencies:**
      ```bash
      pip install -r requirements.txt
      ```

**2. Google API Configuration:**

   * **Enable the Google Drive API:**
      * Go to the Google Cloud Console: [console.cloud.google.com](console.cloud.google.com)
      * Create or select a project.
      * Search for and enable the "Google Drive API".
   * **Create Service Account Credentials:**
      * In the Google Cloud Console, navigate to "IAM & Admin" -> "Service Accounts".
      * Create a new service account.
      * Grant the service account appropriate roles (e.g., "Viewer" for read-only access to Google Drive).
      * Create a JSON key file (credentials.json) for the service account and download it.
      * **Place `credentials.json`:**
      * Place the `credentials.json` file in the same directory as `main.py` (or adjust the code to point to the correct path).

**3. Running the Application:**

   * **Execute the main script:**
      ```bash
      python main.py
      ```

**Repository Contents:**

* `main.py`: The main Python script that implements the RAG pipeline.
* `requirements.txt`: A list of Python dependencies.
* `credentials.json`: (You will create this) The Google Drive API credentials.
* (Potentially) other supporting files for data processing or model handling.

**Notes:**

* Replace `env_name` with your desired Conda environment name.
* Ensure that the Google Drive files you intend to use are accessible by the service account.
* Adjust the python version in the conda create command if needed.
* Consider adding a .gitignore file to prevent commiting the credentials.json file.
* Add clear instructions on how to structure the google drive files that are to be used.