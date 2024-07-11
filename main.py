from aiohttp import web
from datetime import datetime
from aiohttp.web_request import Request
from aiohttp.web_response import Response

# Define route table to store endpoints
routes = web.RouteTableDef()

# Decorator allows this function to run when get request is sent to endpoint by a client
@routes.get('/time')
async def time(request: Request) -> Response:
    today = datetime.today()

    # Store results in dict to be sent as JSON
    result = {
        'month' : today.month,
        'day'   : today.day,
        'time'  : str(today.time())
    }

    # returns formatted result with a 200 status code and json content type
    return web.json_response(result)

# Creates out web application
app = web.Application()

# Registers our route with the app
app.add_routes(routes)

web.run_app(app)
