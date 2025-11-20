import datetime
import pyotp
import asyncio

class OTP:
    def __init__(self, otp_seed):
        self.generator = pyotp.TOTP(otp_seed)
        print("OTP generator initialized successfully.")

    async def get_code(self):
        time_remaining = self.generator.interval - datetime.datetime.now().timestamp() % self.generator.interval
        print(f"Time remaining for current OTP code: {int(time_remaining)} seconds")

        if time_remaining < 5:
            print("Less than 5 seconds remaining for current OTP code. Waiting for new code...")
            time_to_wait = time_remaining + 2

            await asyncio.sleep(time_to_wait)
            
        return self.generator.now()