
[return to index](https://released.github.io/)

<a id="article_top"></a>

# FAQ (Renesas)


* [How to get RLIN3 (UART) lowest error rate](#calculate_uart_baud_rate)


---

<a id="calculate_uart_baud_rate"></a>

# How to get the lowest error rate according to current UART baud rate

* __RLIN3 (UART) clock max speed__

![](img/RLIN3_clock_speed.jpg)

* __RLIN3 (UART) baud rate calculate formula__

![](img/RLIN3_uart_baud_rate_formula.jpg)


[back to top](#article_top)   

---

[download(python)](python/RH850_uart_gui.pyw)

* __use tab 3:Best Match Finder, to get best match__

    * input target baud rate 
    * input target error rate
    * tool will try to find best match , base on freq : 
        * 8MHz,16MHz,20MHz,24MHz,40MHz,80MHz,96MHz,120MHz

![](img/RLIN3_UART_tab03.jpg)

* __use tab 2:Manual Calculate, to calculate error rate__

    * input target Base Frequency 
    * input target LPRS/BRP0/NSPB 
    * input target baud rate 

![](img/RLIN3_UART_tab02.jpg)


* __use tab 1:Auto Calculate, to calculate error rate__

    * input target Base Frequency 
    * input target baud rate 
    * input target display result 

below is error rate result , when Base Frequency:40MHz
![](img/RLIN3_UART_tab01_40MHz.jpg)

below is error rate result , when Base Frequency:24MHz
![](img/RLIN3_UART_tab01_24MHz.jpg)

below is error rate result , when Base Frequency:16MHz
![](img/RLIN3_UART_tab01_16MHz.jpg)

[back to top](#article_top)   

---



