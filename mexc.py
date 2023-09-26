import os
from dotenv import load_dotenv
load_dotenv()
mexc_apikey=os.environ.get('MEXC_APIKEY')
mexc_secretkey=os.environ.get('MEXC_SECRET_KEY')
# from contract_v1_python_demo import *
from pymexc import futures

# initialize HTTP client
futures_client = futures.HTTP(api_key = mexc_apikey, api_secret = mexc_secretkey)

# ******** Open Position *********
def get_position_data():
    res=futures_client.open_positions()
    position_data=res['data']
    return position_data

# print('position_data', get_position_data())

def get_fair_price(symbol):
    res=futures_client.fair_price(symbol)
    fair_price=res['data']['fairPrice']
    return fair_price

# print('fair_price is:', get_fair_price('SUI_USDT'))

def get_contract_value(symbol):
    res=futures_client.detail(symbol)
    contract_value=res['data']['contractSize']
    return contract_value

# print('contract_value is:', get_contract_value('SUI_USDT'))

def get_margin_string(symbol, oim, openType):
    USDTString = "%.4f" % oim
    USDString = "%.2f" % oim
    # res=futures_client.detail(symbol)
    # positionType=res['data']['positionOpenType']
    if openType==1:
        total_string = USDTString + " USDT\n" + "≈ " + USDString + " USD\n" + "(" + "Isolated" + ")"
        return total_string
    elif openType==2:
        total_string = USDTString + " USDT\n" + "≈ " + USDString + " USD\n" + "(" + "Cross" + ")"
        return total_string
    # elif openType==3:
    #     total_string = USDTString + " USDT\n" + "≈ " + USDString + " USD\n" + "(" + "Both" + ")"
    #     return total_string
 
def get_unrealizedPNL_string(fairPrice, avgEntryPrice, position, positionType, contract_value, margin):
    colorFlag = ""
    if positionType == 1:
        unrealizedPNL=(fairPrice - avgEntryPrice) * position * contract_value
    elif positionType == 2:
        unrealizedPNL=(avgEntryPrice - fairPrice) * position * contract_value
    if unrealizedPNL > 0:
        colorFlag = "Green"
    elif unrealizedPNL < 0:
        colorFlag = "Red"
    percent=(unrealizedPNL/margin)*100
    percent_string="%.2f" % percent
    USDT_string = "%.4f" % unrealizedPNL
    USD_string = "%.2f" % unrealizedPNL
    total_string = USDT_string + " USDT\n" + percent_string + "%\n" + "≈ " + USD_string + " USD"
    return total_string, colorFlag



# ******** Open Order *********
def get_orders_data():
    res=futures_client.open_orders('')
    if res['success'] == True:
        orders_data=res['data']
        return orders_data

def get_direction_string(side):
    colorFlag = ""
    if side == 1:
        colorFlag = "Green"
        return "Buy Long", colorFlag
    elif side == 2:
        colorFlag = "Red"
        return "Sell Short", colorFlag
    elif side == 3:
        colorFlag = "Green"
        return "Buy Short", colorFlag
    elif side == 4:
        colorFlag = "Red"
        return "Sell Long", colorFlag

def get_leverage_string(leverage, openType):
    if openType == 1:
        return str(leverage) + "X"
    if openType == 2:
        return "Cross" + str(leverage) + "X"

def get_amount_string(amount, unit):
    return str(amount) + " " + unit

def get_filled_amount_string(filledAmount, unit):
    return str(filledAmount) + " " + unit

def get_status_string(state):
    if state == 1:
        return "Uniform"
    elif state == 2:
        return "Incomplete"
    elif state == 3:
        return "Completed"
    elif state == 4:
        return "Cancelled"
    elif state == 5:
        return "Invalid"

def get_margin_used_string(margin, usdt):
    return "%.4f" % margin + " " + usdt

# ******** End Orders **********