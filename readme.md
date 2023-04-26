You can sign up for capsolver here, this is what we use to solve the hcaptcha challenge: https://dashboard.capsolver.com/passport/register?inviteCode=hnpifE3ejpcE

## Usage example:

To find unused usernames:

```python
from krunkerwebsocketAPI import KrunkerWebSocket
import asyncio

async def main():
    usernames_to_check = ['sfkjadhsfalskas123', '.Floow', 'Sidney']
    capsolver_api_key = os.environ.get('CAPSOLVER_API_KEY')
    kws = KrunkerWebSocket(capsolver_api_key) # Optional but highly reccomended, otherwise you will need to solve the captcha in browser intermittently
    await kws.start()
    for username in usernames_to_check:
        response = await kws.request_profile(username)
        if not response:
            print(username, 'is available!')

if __name__ == '__main__': # Just some asyncio boilerplate
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
```

output:
`'sfkjadhsfalskas123 is available!'`
