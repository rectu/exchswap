# exch.cx automated swaps

a poorly put together chat-gpt fuled python program to  snipe xmr reserves in exch.chat

note this bot isn't written in rust and only uses foundry to send eth, its slow & non competeive.




## 

- watches for pool updates, needs to meet minimum xmr threshold
- attempts to create an order
- sends eth to from_addr using foundry ( eth rust repo idk i forgot already google it )
- telegram logging
