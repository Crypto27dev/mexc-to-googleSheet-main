import time
from mexc import *
import requests
import gspread
from google.oauth2.service_account import Credentials
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

positionsPeriodTime = os.environ.get('POSITIONS_PERIOD_TIME')
ordersPeriodTime = os.environ.get('ORDERS_PERIOD_TIME')
googleSheetURL = os.environ.get('GOOGLE_SHEET_URL')
googleCredentialJson = os.environ.get('GOOGLE_CREDENTIAL_JSON')
# print('credential is:', googleCredentialJson)

# Authorize by credentials
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    # 'resumrabbits0207-2ac2a2c0dfca.json',
    googleCredentialJson,
    scopes=scopes
)

gc = gspread.authorize(credentials)

sh = gc.open_by_url(googleSheetURL)

wks = sh.get_worksheet(2)

def set_positions_data_to_gsheet(old_position_num_rows):
    position_data = get_position_data()
    data_length = len(position_data)
    # print('position data is:', position_data)
    # column_value_list = wks.col_values(2)
    if old_position_num_rows <= data_length:
        total_string = []
        total_format = []
        for i in range(data_length):
            array_string = []
            tradingPair = position_data[i]['symbol']
            tmp_str = tradingPair.split("_")
            token = tmp_str[0]
            positionFlag = position_data[i]['positionType']
            openAvgPrice = position_data[i]['newOpenAvgPrice']
            oim = position_data[i]['oim']
            positionType = position_data[i]['positionType']
            fairPrice = get_fair_price(tradingPair)
            position = position_data[i]['holdVol']
            # Create strings
            if positionFlag == 1:
                tradingPair_string = str(tradingPair) + "\n" + "Long"
            elif positionFlag == 2:
                tradingPair_string = str(tradingPair) + "\n" + "Short"
            positionString = str(position_data[i]['holdVol']) + " " + token
            avgEntryPrice = str(position_data[i]['holdAvgPrice'])
            fairPriceString = str(get_fair_price(tradingPair))
            # print('fairPrice' + str(tradingPair), get_fair_price(tradingPair))
            estLiqPrice = str(position_data[i]['liquidatePrice'])
            marginRatio = "%.2f" % (position_data[i]['marginRatio']*100) + "%"
            margin = get_margin_string(tradingPair, oim, position_data[i]['openType'])
            unrealizedPNL, colorPositionFlag = get_unrealizedPNL_string(fairPrice, openAvgPrice, position, positionType, get_contract_value(tradingPair), oim)
            array_string = [tradingPair_string, positionString, avgEntryPrice, fairPriceString, estLiqPrice, marginRatio, margin, unrealizedPNL]
            total_string.append(array_string)            
            # Create formatting of cell
            if colorPositionFlag == "Green":
                total_format.append({
                    "range": 'I' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
            elif colorPositionFlag == "Red":
                total_format.append({
                    "range": 'I' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 1, "green": 0, "blue": 0}}}
                })
            # if positionType == 1:
            #     wks.update('B' + pos_start_num, str(tradingPair) + "\n" + "Long")
            # elif positionType == 2:
            #     wks.update('B' + pos_start_num, str(tradingPair) + "\n" + "Short")
            # wks.update('C' + pos_start_num, str(position) + " " + token)
            # wks.update('D' + pos_start_num, str(avgEntryPrice))
            # wks.update('E' + pos_start_num, str(fairPrice))
            # wks.update('F' + pos_start_num, str(estLiqPrice))
            # wks.update('G' + pos_start_num, "%.2f" % marginRatio + "%")
            # wks.update('H' + pos_start_num, margin)
            # wks.update('I' + pos_start_num, unrealizedPNL)        
        # Update the range("B4:I(3 + len(total_string))")
        print('open position length is:', old_position_num_rows)
        if old_position_num_rows >= 0 & len(total_string) > 0:
            wks.update('B4:I' + str(3 + len(total_string)), total_string)
        # print('total format is:', len(total_format))
        if len(total_format) > 0:
            wks.batch_format(total_format)
    elif old_position_num_rows > data_length:
        differ_rows = old_position_num_rows - data_length
        total_string = []
        total_format = []
        for i in range(data_length):
            array_string = []
            tradingPair = position_data[i]['symbol']
            tmp_str = tradingPair.split("_")
            token = tmp_str[0]
            positionFlag = position_data[i]['positionType']
            openAvgPrice = position_data[i]['newOpenAvgPrice']
            oim = position_data[i]['oim']
            positionType = position_data[i]['positionType']
            fairPriceInt = get_fair_price(tradingPair)
            positionInt = position_data[i]['holdVol']
            # Create strings
            if positionFlag == 1:
                tradingPair_string = str(tradingPair) + "\n" + "Long"
            elif positionFlag == 2:
                tradingPair_string = str(tradingPair) + "\n" + "Short"
            position = str(position_data[i]['holdVol']) + " " + token
            avgEntryPrice = str(position_data[i]['holdAvgPrice'])
            fairPrice = str(get_fair_price(tradingPair))
            # print('fairPrice' + str(tradingPair), get_fair_price(tradingPair))
            estLiqPrice = str(position_data[i]['liquidatePrice'])
            marginRatio = "%.2f" % (position_data[i]['marginRatio']*100) + "%"
            margin = get_margin_string(tradingPair, oim, position_data[i]['openType'])
            unrealizedPNL, colorPositionFlag = get_unrealizedPNL_string(fairPriceInt, openAvgPrice, positionInt, positionType, get_contract_value(tradingPair), oim)
            array_string = [tradingPair_string, position, avgEntryPrice, fairPrice, estLiqPrice, marginRatio, margin, unrealizedPNL]
            total_string.append(array_string)           
            # Create formatting of cell
            if colorPositionFlag == "Green":
                total_format.append({
                    "range": 'I' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
            elif colorPositionFlag == "Red":
                total_format.append({
                    "range": 'I' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 1, "green": 0, "blue": 0}}}
                })
        for i in range(differ_rows):
            array_string = ["", "", "", "", "", "", "", ""]
            total_string.append(array_string)       
        if old_position_num_rows >= 0 & len(total_string) > 0:
            wks.update('B4:I' + str(3 + len(total_string)), total_string)
        if len(total_format) > 0:
            wks.batch_format(total_format)

def set_orders_data_to_gsheet(old_order_num_rows):
    orders_data = get_orders_data()
    data_length = len(orders_data)
    # print('orders data is: ', orders_data)
    if old_order_num_rows <= data_length:
        total_string = []
        total_format = []
        for i in range(data_length):
            arrayString = []
            sencondsTime = orders_data[i]['createTime']/1000
            date = datetime.datetime.fromtimestamp(sencondsTime)
            tradingPair = orders_data[i]['symbol']
            tmp_str = tradingPair.split("_")
            token = tmp_str[0]            
            # Create strings
            formated_date = date.strftime("%Y-%m-%d %H:%M:%S")
            tradingPairString = str(tradingPair)
            direction, colorOrderFlag = get_direction_string(orders_data[i]['side'])
            leverage = get_leverage_string(orders_data[i]['leverage'], orders_data[i]['openType'])
            amount = get_amount_string(orders_data[i]['vol'], token)
            orderPrice = "%.4f" % orders_data[i]['price']
            filledAmount = get_filled_amount_string(orders_data[i]['dealVol'], token)
            filledPrice = "%.4f" % orders_data[i]['dealAvgPrice']
            marginUsed = get_margin_used_string(orders_data[i]['orderMargin'], tmp_str[1])
            status = get_status_string(orders_data[i]['state'])
            arrayString = [formated_date, tradingPairString, direction, leverage, amount, orderPrice, filledAmount, filledPrice, marginUsed, status]
            total_string.append(arrayString)
            if colorOrderFlag == "Green":
                total_format.append({
                    "range": 'M' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
                total_format.append({
                    "range": 'N' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
                # wks.format('M' + pos_num_row, {'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}})
            elif colorOrderFlag == "Red":
                total_format.append({
                    "range": 'M' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
                total_format.append({
                    "range": 'N' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
        if old_order_num_rows > 0 & len(total_string) > 0:
            wks.update('K4:T' + str(3 + len(total_string)), total_string)
        if len(total_format) > 0:
            wks.batch_format(total_format)
    elif old_order_num_rows > data_length:
        differ_rows = old_order_num_rows - data_length
        total_string = []
        total_format = []
        for i in range(data_length):
            arrayString = []
            sencondsTime = orders_data[i]['createTime']/1000
            date = datetime.datetime.fromtimestamp(sencondsTime)
            tradingPair = orders_data[i]['symbol']
            tmp_str = tradingPair.split("_")
            token = tmp_str[0]
            # Create strings
            formated_date = date.strftime("%Y-%m-%d %H:%M:%S")
            tradingPairString = str(tradingPair)
            direction, colorOrderFlag = get_direction_string(orders_data[i]['side'])
            leverage = get_leverage_string(orders_data[i]['leverage'], orders_data[i]['openType'])
            amount = get_amount_string(orders_data[i]['vol'], token)
            orderPrice = "%.4f" % orders_data[i]['price']
            filledAmount = get_filled_amount_string(orders_data[i]['dealVol'], token)
            filledPrice = "%.4f" % orders_data[i]['dealAvgPrice']
            marginUsed = get_margin_used_string(orders_data[i]['orderMargin'], tmp_str[1])
            status = get_status_string(orders_data[i]['state'])
            arrayString = [formated_date, tradingPairString, direction, leverage, amount, orderPrice, filledAmount, filledPrice, marginUsed, status]
            total_string.append(arrayString)
            if colorOrderFlag == "Green":
                total_format.append({
                    "range": 'M' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
                total_format.append({
                    "range": 'N' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
                # wks.format('M' + pos_num_row, {'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}})
            elif colorOrderFlag == "Red":
                total_format.append({
                    "range": 'M' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
                total_format.append({
                    "range": 'N' + str(4+i),
                    "format":{'textFormat': {'foregroundColor': {"red": 0, "green": 50, "blue": 0}}}
                })
        # Update the range("B4:I(3 + len(total_string))")
        wks.update('K4:T' + str(3 + len(total_string)), total_string)
        wks.batch_format(total_format)
        for i in range(differ_rows):
            arrayString = ["", "", "", "", "", "", "", "" ,"", ""]
            total_string.append(arrayString)
        # Update the range("B4:I(3 + len(total_string))")
        if old_order_num_rows > 0 & len(total_string) > 0:
            wks.update('K4:T' + str(3 + len(total_string)), total_string)
        if len(total_format) > 0:
            wks.batch_format(total_format)

def start_positions():
    column_value_list1 = wks.col_values(2)
    old_position_num_rows = len(column_value_list1) - 3
    get_infura_value()
    print('Start the updating of Open Positons.')
    set_positions_data_to_gsheet(old_position_num_rows)
    print('Ended.\n')

def start_orders():
    column_value_list2 = wks.col_values(11)
    old_order_num_rows = len(column_value_list2) - 3
    print('Start the updating of Open Orders.')
    set_orders_data_to_gsheet(old_order_num_rows)
    print('Ended.')

def start_period(pTime1, pTime2):
    i = 0
    while True:
        if(i % pTime1 == 0):
            start_orders()
        if(i % pTime2 == 0):
            start_positions()
        time.sleep(1)
        i = i + 1

start_period(ordersPeriodTime, positionsPeriodTime)

# def get_date():
#     sencondsTime = 1695480590023/1000
#     date = datetime.datetime.fromtimestamp(sencondsTime)
#     formated_date = date.strftime("%Y-%m-%d %H:%M:%S")
#     print(formated_date)
# get_date()