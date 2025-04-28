from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    CookieJar,
    FormData
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from datetime import datetime
from colorama import *
import asyncio, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class ByteNova:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://bytenova.ai",
            "Referer": "https://bytenova.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://bytenova.ai/api"
        self.code = "SEL76HbfL" # U can change it with yours.
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}ByteNova AI - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
        
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address

            return address
        except Exception as e:
            return None
    
    def generate_signature(self, account: str):
        try:
            message = "You hereby confirm that you are the owner of this connected wallet. This is a safe and gasless transaction to verify your ownership. Signing this message will not give ByteNova permission to make transactions with your wallet."
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            return signature
        except Exception as e:
            return None
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def user_login(self, account: str, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet_login"
        data = FormData()
        data.add_field("wallet_signature", self.generate_signature(account))
        data.add_field("wallet", address)
        data.add_field("full_message", "")
        data.add_field("public_key", "")
        data.add_field("chain_type", "BNB")
        for attempt in range(retries):
            cookie_jar = CookieJar()
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(cookie_jar=cookie_jar, connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=self.headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
                        return result['data']['access_token'], cookies['user']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None, None
    
    async def user_verify(self, address: str, access_token: str, cookies: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/invite_verify"
        data = FormData()
        data.add_field("wallet", address)
        data.add_field("invite_code", self.code)
        headers = {
            **self.headers,
            "Authorization": access_token,
            "Cookie": f"user={cookies}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def user_credit(self, address: str, access_token: str, cookies: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/credit_refresh"
        data = FormData()
        data.add_field("wallet", address)
        headers = {
            **self.headers,
            "Authorization": access_token,
            "Cookie": f"user={cookies}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def task_lists(self, access_token: str, cookies: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/tweet_list"
        headers = {
            **self.headers,
            "Authorization": access_token,
            "Cookie": f"user={cookies}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['tweets']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def complete_tasks(self, address: str, access_token: str, cookies: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/tweet_refresh"
        data = FormData()
        data.add_field("task_id", task_id)
        data.add_field("wallet", address)
        headers = {
            **self.headers,
            "Authorization": access_token,
            "Cookie": f"user={cookies}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def process_get_access_token(self, account: str, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        access_token = None
        cookies = None
        while access_token is None or cookies is None:
            access_token, cookies = await self.user_login(account, address, proxy)
            if not access_token or not cookies:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                )
                proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                await asyncio.sleep(5)
                continue

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
            )
            return access_token, cookies

    async def process_accounts(self, account: str, address, use_proxy: bool):
        access_token, cookies = await self.process_get_access_token(account, address, use_proxy)
        if access_token and cookies:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            await self.user_verify(address, access_token, cookies, proxy)
            
            balance = await self.user_credit(address, access_token, cookies, proxy)
            if balance:
                bind_credit_twitter = balance.get("bind_credit_twitter", 0)
                follow_credit_twitter = balance.get("follow_credit_twitter", 0)
                bind_credit_discord = balance.get("bind_credit_discord", 0)
                follow_credit_discord = balance.get("follow_credit_discord", 0)
                tweet_credit = balance.get("tweet_credit", 0)
                checkin_credit = balance.get("checkin_credit", 0)
                invite_credit = balance.get("invite_credit", 0) 

                total_credits = bind_credit_twitter + follow_credit_twitter + bind_credit_discord + follow_credit_discord + tweet_credit + checkin_credit + invite_credit
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {total_credits} PTS {Style.RESET_ALL}"
                )

            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} N/A PTS {Style.RESET_ALL}"
                )

            task_list = await self.task_lists(access_token, cookies, proxy)
            if task_list:
                self.log(f"{Fore.CYAN + Style.BRIGHT}Task Lists:{Style.RESET_ALL}")
                for task in task_list:
                    if task:
                        task_id = task['task_id']
                        title = task['text']
                        is_done = task['is_done']

                        if is_done:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}Already Completed{Style.RESET_ALL}"
                            )
                            continue

                        complete = await self.complete_tasks(address, access_token, cookies, task_id, proxy)
                        if complete and complete.get("message") == "success":
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                            )
                        else:
                            message = "Unknown Error"
                            if complete.get("code") == 50001:
                                message = "Connect Your X Account First"

                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}Not Completed:{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} {message} {Style.RESET_ALL}"
                            )

            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Data Is None{Style.RESET_ALL}"
                )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)

                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        account = await self.process_accounts(account, address, use_proxy)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                
                delay = 12 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = ByteNova()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] ByteNova AI - BOT{Style.RESET_ALL}                                       "                              
        )