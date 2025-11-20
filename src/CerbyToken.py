import os
import yaml
from playwright.async_api import async_playwright
from src.OtpGenerator import OTP

OKTA_USERNAME_SELECTOR = 'input[name="identifier"]'
OKTA_PASSWORD_SELECTOR = 'input[class="password-with-toggle"]'
OKTA_OTP_SELECTOR = 'input[name="credentials.passcode"]'
OKTA_SUBMIT_BUTTON_SELECTOR = 'input[type="submit"]'

CERBY_USERNAME_SELECTOR = 'input[name="username"]:visible'
CERBY_PASSWORD_SELECTOR = 'input[name="password"]:visible'
CERBY_OTP_SELECTOR = 'input[name="authentication_code"]:visible'
CERBY_OTP_SUBMIT_BUTTON_SELECTOR = 'button[id="signInButton"]:visible'
CERBY_SUBMIT_BUTTON_SELECTOR = 'input[name="signInSubmitButton"]:visible'

class CerbyTokenRetriever:
    def __init__(self):
        print("---------------------------------")
        print("Starting Cerby Token Retriever...")
        print("---------------------------------")
        print("\n")

        # Load configuration
        self.config_path = "config.yaml"
        self.config = self._load_config()

        # Set Values from Config
        self.login_url = f"https://{self.config.get('WORKSPACE_DOMAIN')}.cerby.com/login"
        self.workspace = self.config.get("WORKSPACE_DOMAIN", "cerby")

        self.login_type = self.config.get("LOGIN_TYPE", "okta")
        self.username = self.config.get("USERNAME")
        self.password = self.config.get("PASSWORD")
        self.headless_state = self.config.get("HEADLESS", True)
        self.mfa_enabled = self.config.get("MFA_ENABLED", False)

        # If MFA is enabled in the config, initialize the OTP generator
        if self.mfa_enabled:
            print("MFA is enabled. Initializing OTP generator.")
            self.otp_generator = OTP(otp_seed=self.config.get("TOTP_SEED"))

    def _load_config(self):
        if os.path.exists(self.config_path):
            return yaml.safe_load(open(self.config_path))
        else:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found.")

    async def handle_okta_login(self, page, username, password):
        print(f"Navigating to: {self.login_url}")
        await page.goto(self.login_url)
        await page.wait_for_timeout(20000)
        
        # Fill in username and go to next page
        print("Filling in the username...")
        await page.fill(OKTA_USERNAME_SELECTOR, username, timeout=10000)
        await page.click(OKTA_SUBMIT_BUTTON_SELECTOR, timeout=10000)

        # Fill in Password
        print("Filling in the password...")
        await page.fill(OKTA_PASSWORD_SELECTOR, password, timeout=10000)
        await page.click(OKTA_SUBMIT_BUTTON_SELECTOR, timeout=10000)
        await page.wait_for_timeout(5000)

        if self.mfa_enabled:
            # Fill in OTP
            code = await self.otp_generator.get_code()
            print(f"Generated OTP code: {code}")
            otp_input = page.locator(OKTA_OTP_SELECTOR)
            await otp_input.wait_for(state="visible", timeout=15000)
            await otp_input.fill(code, timeout=10000)
            
            # Instead of clicking the button, submit via Enter key
            await page.keyboard.press("Enter")

    async def handle_local_login(self, page, username, password):
        # Navigate to Cerby login page
        print(f"Navigating to: {self.login_url}")
        await page.goto(self.login_url)
        await page.wait_for_timeout(20000)

        # Fill in username and password
        print("Filling in the username...")
        await page.click(CERBY_USERNAME_SELECTOR, timeout=10000)
        await page.fill(CERBY_USERNAME_SELECTOR, username, timeout=10000)

        print("Filling in the password...")
        await page.click(CERBY_PASSWORD_SELECTOR, timeout=10000)
        await page.fill(CERBY_PASSWORD_SELECTOR, password, timeout=10000)

        await page.click(CERBY_SUBMIT_BUTTON_SELECTOR, timeout=10000)

        if self.mfa_enabled:
            # Fill in OTP
            code = await self.otp_generator.get_code()
            print(f"Generated OTP code: {code}")
            await page.fill(CERBY_OTP_SELECTOR, code, timeout=10000)
            await page.click(CERBY_OTP_SUBMIT_BUTTON_SELECTOR, timeout=10000)

        
    async def get_bearer_token(self, page):
        # Wait for the page to finish loading
        await page.wait_for_timeout(10000)

        # Retrieve the bearer token from local storage
        token = await page.evaluate("() => window.localStorage.getItem('access_token')")

        # Return the bearer token
        return token
    
    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.config.get("HEADLESS", True),
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-features=VizDisplayCompositor",
                ],)
            context = await browser.new_context()
            page = await context.new_page()

            if self.login_type == "okta":
                    print("Using Okta login flow.")
                    await self.handle_okta_login(page, self.username, self.password)
            elif self.login_type == "local":
                    print("Using local Cerby login flow.")
                    await self.handle_local_login(page, self.username, self.password)
            
            bearer_token = await self.get_bearer_token(page)
            print(f"Retrieved Bearer Token: {bearer_token}")
            #await browser.close()