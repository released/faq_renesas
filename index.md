
[return to index](https://released.github.io/)

<a id="article_top"></a>

# FAQ (Renesas)


* [How to get RH850 RLIN3 (UART) lowest error rate](#calculate_uart_baud_rate)

* [How to get RL78 slave PWM TDR/duty value](#calculate_RL_78_pwm_duty)


---

<a id="calculate_uart_baud_rate"></a>

# How to get the lowest error rate according to current UART baud rate

* __RH850 RLIN3 (UART) clock max speed__

![](img/RLIN3_clock_speed.jpg)

* __RH850 RLIN3 (UART) baud rate calculate formula__

![](img/RLIN3_uart_baud_rate_formula.jpg)


[back to top](#article_top)   

---

[download(python)](./python/RH850_uart_gui.pyw)

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


<a id="calculate_RL_78_pwm_duty"></a>

# How to get RL78 slave PWM TDR/duty value 

* __RL78 TDR formula__

![](img/RL78_PWM_0.jpg)


[download(python)](./python/RL78_pwm_gui.pyw)


* __use tab 1:manual input__

    * input pwm master TDR value (hex)
    * input pwm slave TDR value (hex) , to calculate duty
    * input pwm slave duty , to calculate slave TDR
    * select check box , to enable auto calculate master TDR

![](img/RL78_PWM_1.jpg)
    
![](img/RL78_PWM_2.jpg)
    
![](img/RL78_PWM_2_1.jpg)


* __use tab 2:calculate all TDR/duty value__

    * input pwm master TDR value (hex)

![](img/RL78_PWM_3.jpg)

[back to top](#article_top)   

---
