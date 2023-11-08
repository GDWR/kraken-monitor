#!/usr/bin/env python

import logging
import json
import sys

import asyncio
import websockets
import statsd

stats = statsd.StatsClient("graphite", 8125)

logger = logging.getLogger()
logger.setLevel(logging.INFO) # set logger level
logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

kraken_uri = "wss://ws.kraken.com"


async def main():
    logger.info("Starting")

    logger.info("Connecting to websocket at %s", kraken_uri)

    async with websockets.connect(kraken_uri) as websocket:

        data = {
            "event": "subscribe",
            "pair": [
                "SOL/USD",
                "ETH/USD",
                "AVX/USD",
                "BTC/USD",
            ],
            "subscription": {
                "name": "ticker"
            }
        }
        await websocket.send(json.dumps(data))

        while True:
            match json.loads(await websocket.recv()):
                case {"event": "heartbeat"}:
                    logger.debug("Recieved heartbeat event")
                case {"event": "systemStatus", "status": status, "version": version, "connectionID": connection_id}:
                    logger.info("Recieved systemStatus event; status=%s version=%s connectionID=%s", status, version, connection_id)
                case {'event': 'subscriptionStatus', 'channelID': channel_id, 'channelName': channel_name, 'pair': pair, 'status': status, 'subscription': subscription}:
                    logger.info("Recieved subscriptionStatus event; channelID=%s channelName=%s pair=%s status=%s subscription=%s", channel_id, channel_name, pair, status, subscription)
                case [channel_id, data, "ticker", pair]:
                    logger.info("Recieved ticker for %s [%s]", channel_id, pair)

                    ask = data["a"][0]
                    stats.gauge(f'{pair}.ask', float(ask))
                    logger.info("Ask for %s [%s]: %s", channel_id, pair, ask)

                    buy = data["b"][0]
                    stats.gauge(f'{pair}.buy', float(buy))
                    logger.info("Buy for %s [%s]: %s", channel_id, pair, buy)

                case msg:
                    logger.warning("Unhandled message %s", msg)

if __name__ == "__main__":
    asyncio.run(main())