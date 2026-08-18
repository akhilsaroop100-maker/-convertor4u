# Upload Convertor4U to GitHub

1. Sign in to GitHub and create a new repository named `convertor4u`.
2. Keep the repository private if you prefer. Do not add a README, `.gitignore`, or license during creation because they are already included here.
3. Open the new empty repository and choose **uploading an existing file**.
4. Open this unzipped package folder and drag all its contents into the GitHub upload area. Upload the contents, not the outer folder or ZIP file.
5. Enter `Initial Convertor4U website` as the commit message and choose **Commit changes**.
6. Confirm that `manage.py`, `requirements.txt`, `render.yaml`, `config`, `converters`, `static`, and `templates` appear at the top level of the repository.

Never upload a `.env` file, `db.sqlite3`, a virtual-environment folder, passwords, or API keys. The included `.env.example` contains placeholders only and is safe to upload.

After the GitHub upload, connect this repository to Render using its Blueprint option. Render will read `render.yaml` and create the web service, PostgreSQL database, and scheduled currency refresh service.
