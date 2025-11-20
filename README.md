# Cerby Token Retrieval CLI

This CLI tool automates the process of obtaining a Cerby user's bearer token. The token can be used for development tasks against Cerby's internal API.

## Features

- Cerby Local authentication via username, password, and optional OTP seed.
- Okta authentication flow through SAML with username and password, and optional OTP seed.
- Generates its own OTPs; ideal for non-interactive flows.

## Requirements

- Local or Okta credentials for a Cerby user.
- OTP seed if MFA is enabled. (TOTP only).

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/cerby-token-retrieval.git
cd cerby-token-retrieval
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Install the necessary browsers.

```bash
playwright install
```

## Configuration

The tool uses a `config.yaml` file for configuration. Use the example.config.yaml file to set your configuration. - Keep your `config.yaml` secure.

OR

Set environment variables.

## Usage

After configuring `config.yaml`, run:

```bash
python cerby_token_retrieval.py
```

The tool will output your bearer token, which you can use for authenticated API requests.

## Notes
