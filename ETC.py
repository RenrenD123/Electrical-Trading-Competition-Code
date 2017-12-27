
#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json
import time

#TCP_IP = "10.0.121.179"
#order_id = 0
#position = 0

def connect():
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect(("test-exch-ADCTRADING", 25000))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())


# support function 1am
def buy(order_id, sym, price, size):
    return {"type": "add", "order_id": order_id, "symbol": sym, "dir": "BUY", "price": price, "size": size}

def sell(order_id, sym, price, size):
    return {"type": "add", "order_id": order_id, "symbol": sym, "dir": "SELL", "price": price, "size": size}

def convert(order_id, sym, direction, size):
    return {"type": "convert", "order_id": order_id, "symbol":sym, "dir": direction, "size": size}

def cancel(order_id):
    return {"type": "cancel",  "order_id": order_id}

def buyprice(message,sym):
    ret = []
    if (message.get('symbol') == sym):
        if (message.get('buy') != None):
            size_of_buy = len(message.get('buy'))
            for i in range(size_of_buy):
                ret.append(message.get('buy')[i][0])
    return ret

def buysize(message,sym):
    ret = []
    if (message.get('symbol') == sym):
        if (message.get('buy') != None):
            size_of_buy = len(message.get('buy'))
            for i in range(size_of_buy):
                ret.append(message.get('buy')[i][1])
    return ret

def sellprice(message,sym):
    ret = []
    if (message.get('symbol') == sym):
        if (message.get('sell') != None):
            size_of_sell = len(message.get('sell'))
            for i in range(size_of_sell):
                ret.append(message.get('sell')[i][0])
    return ret

def sellsize(message,sym):
    ret = []
    if (message.get('symbol') == sym):
        if (message.get('sell') != None):
            size_of_sell = len(message.get('buy'))
            for i in range(size_of_sell):
                ret.append(message.get('sell')[i][0])
    return ret


def main():
    exchange = connect()
    write(exchange, {"type":"hello","team": "ADCTRADING"})
    hello_from_exchange = read(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
 #   trading:
 #   buy:
    order_id = 0
    position = 0
    while(1):
        message = read(exchange)
#pair 1S < 2B
        if (message.get('symbol') == 'VALBZ' or message.get('symbol') == 'VALE'and position > -30000):
            print("message replied: ", message, file = sys.stderr)
            if (message.get('symbol') == 'VALE'):
                VALE_buy = len(buyprice(message,'VALE'))
                VALE_sell = len(sellprice(message,'VALE'))
            if (message.get('symbol') == 'VALBZ'):
                VALBZ_buy = len(buyprice(message,'VALBZ'))
                VALBZ_sell = len(sellprice(message,'VALBZ'))

                if (VALE_buy != 0 or VALBZ_sell != 0):
                    for i in range(VALBZ_sell):
                        for j in range(VALE_buy):
                            if (sellprice(message,'VALBZ')[i] < buyprice(message,'VALE')[j]):
                                if (sellprice(message,'VALBZ')[i]*sellsize(message,'VALBZ')[i] + 10 < buyprice(message,'VALE')[j]*buysize(message,'VALE')[j]):
                                    write(exchange, buy(order_id,'VALBZ',sellprice(message,'VALBZ')[i],sellsize(message,'VALBZ')[i]))
                                    convert(order_id,'VALBZ',"SELL",sellsize(message,'VALBZ')[i])
                                    order_id += 1
                                    write(exchange, sell(order_id,'VALE',buyprice(message,'VALE')[j],buyprice(message,'VALE')[j]))
                                    order_id += 1
                                if (sellprice(message,'VALBZ')[i]*sellsize(message,'VALBZ')[i] < buyprice(message,'VALE')[j]*buysize(message,'VALE')[j]) + 10:
                                    write(exchange, sell(order_id,'VALE',buyprice(message,'VALE')[j],buysize(message,'VALE')[j]))
                                    convert(order_id,'VALE',"BUY",sellsize(message,'VALE')[j])
                                    order_id += 1
                                    write(exchange, buy(order_id,'VALBZ',sellprice(message,'VALBZ')[i],sellprice(message,'VALBZ')[i]))
                                    order_id += 1
                if (VALBZ_buy != 0 and VALE_sell != 0):
                    for i in range(VALBZ_buy):
                        for j in range(VALE_sell):
                            if (buyprice(message,'VALBZ')[i] > sellprice(message,'VALE')[j]):
                                if (buyprice(message,'VALBZ')[i]*buysize(message,'VALBZ')[i] > sellprice(message,'VALE')[j]*sellsize(message,'VALE')[j]) + 10:
                                    write(exchange, buy(order_id,'VALE',sellprice(message,'VALE')[j],sellsize(message,'VALE')[j]))
                                    convert(order_id,'VALBZ',"BUY",buysize(message,'VALE')[j])
                                    order_id += 1
                                    write(exchange, sell(order_id,'VALBZ',buyprice(message,'VALBZ')[i],buyprice(message,'VALBZ')[i]))
                                    order_id += 1
                                if (buyprice(message,'VALBZ')[i]*buysize(message,'VALBZ')[i] + 10 > sellprice(message,'VALE')[j]*sellsize(message,'VALE')[j]):
                                    write(exchange, sell(order_id,'VALBZ',buyprice(message,'VALBZ')[i],buysize(message,'VALBZ')[i]))
                                    convert(order_id,'VALBZ',"SELL",buysize(message,'VALBZ')[i])
                                    order_id += 1
                                    write(exchange, buy(order_id,'VALE',sellprice(message,'VALE')[j],sellprice(message,'VALE')[j]))
                                    order_id += 1
                

#BOND
        if (message.get('symbol') == "BOND" and position >  -30000) :
            #print("message replied: ", message, file=sys.stderr)
            if (message.get('sell') != None and message.get('buy') != None):
                size_of_sell = len(message.get('sell'))
                size_of_buy = len(message.get('buy'))

                for i in range(size_of_sell):
                   
                    if (message.get('sell')[i][0] < 1000):
                        write(exchange, buy(order_id,"BOND",message.get('sell')[i][0],message.get('sell')[i][1]))                  
                        order_id += 1
                        position -= message.get('sell')[i][0] * message.get('sell')[i][1]
                for j in range(size_of_buy):
                    if (message.get('buy')[j][0] >= 1000):
                        write(exchange, sell(order_id,"BOND",message.get('buy')[j][0],message.get('buy')[j][1]))                  
                        order_id += 1
                        position += message.get('buy')[j][0] * message.get('buy')[j][1]



        time.sleep

if __name__ == "__main__":
    print("HERE")
    main()