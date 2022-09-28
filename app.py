import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
import time
import altair as alt
from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima
from statsmodels.tsa.statespace.exponential_smoothing import ExponentialSmoothing

mapping={
"Dollar":"INR=X",
"Euro":"EURINR=X", 
"Bitcoin":"BTC-INR",
"Ethereum":"ETH-INR", 
"Infosys":"INFY.NS",
"TATA Steel":"TATASTEEL.NS",
"ICICI Bank":"ICICIBANK.NS",
"State Bank of India":"SBIN.NS",
"Reliance Industries limited":"RELIANCE.NS"
}

mapping2={ 
"Infosys":"INFY.NS",
"TATA Steel":"TATASTEEL.NS",
"ICICI Bank":"ICICIBANK.NS",
"State Bank of India":"SBIN.NS",
"Reliance Industries limited":"RELIANCE.NS"
}

mapping3={
"Dollar":"INR=X",
"Euro":"EURINR=X", 
"Infosys":"INFY.NS",
"TATA Steel":"TATASTEEL.NS",
"ICICI Bank":"ICICIBANK.NS",
"State Bank of India":"SBIN.NS",
"Reliance Industries limited":"RELIANCE.NS"
}

times={
"3 Months":90,
"6 Months":180,
"1 Year":365
}

st.set_page_config(
	page_icon="chart_with_upwards_trend",
    page_title="Investment Dashboard",
    layout="wide",
)

header=st.container()
st.write("""---""")
UpperBlock=st.container()
st.write("""---""")
MiddleBlock=st.container()
st.write("""---""")
LowerBlock=st.container()
st.write("""---""")
footer=st.container()





with header:
	col1,col2=st.columns([1,4],gap="large")

	with col1:
		st.image("Objects/LOGO1.png",use_column_width=True)

	with col2:
		st.title("Investment Dashboard - Beta Version")
		st.write("Prototype of an Indian Investment Dashboard.")





with UpperBlock:

	col1, col2=st.columns([8,3],gap="large")
	with col1:
		st.subheader("1-Year Historical performance of a stock")
		display1=st.selectbox("Select a stock to plot:",mapping.keys())

		placeholderRASO=st.empty()


	with col2:
		st.subheader("Global Indicators/₹")      
		placeholder1=st.empty()
		placeholder2=st.empty()
		placeholder3=st.empty()
		placeholder4=st.empty()
		st.write("""---""")
		st.write("*"+"Getting updated every ~10 seconds.")





with MiddleBlock:
	st.subheader("Forecasted performance of a stock")
	col1,col2,col3=st.columns([1,1,1],gap="large")
	
	with col1:
		stock=st.selectbox("Select a stock for prediction:",mapping3.keys())


	prediction_data=yf.download(tickers=mapping[stock],period="max")
	prediction_data=prediction_data['Close']
	prediction_data=prediction_data.dropna()
	
	div=int(len(prediction_data)*0.95)
	train=prediction_data[:div]
	test=prediction_data[div:]
	
	model_auto=auto_arima(train,start_p=2,start_q=2,test="adf",m=1,max_p=6,max_q=6,trace=True,suppress_warnings=True)

	model=ARIMA(train,order=model_auto.get_params().get("order"))
	model=model.fit()

	st.write("p, d, and q of the used ARIMA model are: "+str(model_auto.get_params().get("order")))
	st.write("Displaying the forcasted closing values range for the next month:")

	s=div
	e=len(train)+len(test)-1

	smoothing=ExponentialSmoothing(endog=train)
	smoothing=smoothing.fit()
	preds=smoothing.get_forecast(steps=len(test)+30)
	predictions=preds.summary_frame(alpha=0.03)
	#st.table(predictions)
	
	test=test.reset_index()
	train=train.reset_index()
	prediction_data=prediction_data.reset_index()
	current_date=test['Date'][len(test)-1]

	for i in range(30):
		current_date=current_date+timedelta(days=1)
		new_row={'Date':current_date,'Close':np.nan}
		test=test.append(new_row,ignore_index=True)

	predictions=predictions.reset_index()
	predictions['Date']=test['Date']
	
	mnn=predictions['mean_ci_lower'][len(predictions)-1]-0.3
	mxx=predictions['mean_ci_upper'][len(predictions)-1]+0.3

	cc1=alt.Chart(predictions).mark_line(color='yellow').encode(x='Date',y='mean_ci_upper')
	cc2=alt.Chart(predictions).mark_line(color='yellow').encode(x='Date',y='mean_ci_lower')
	cc3=alt.Chart(prediction_data[-1000:]).mark_line(color='cyan').encode(x='Date',y=alt.Y('Close',title='Close/₹',scale=alt.Scale(domain=[mnn,mxx])))
	cc4=alt.Chart(predictions).mark_area(color='grey').encode(x='Date',y='mean_ci_upper',y2='mean_ci_lower')

	st.altair_chart((cc4+cc1+cc2+cc3).properties(height=500).interactive(),use_container_width=True)





with LowerBlock:
	st.subheader("Buy-Sell-Hold Signals")
	col1,col2,col3=st.columns([1,1,1],gap="large")
	with col1:
		signal=st.selectbox("Select a stock:",mapping2.keys())
	
	signals=yf.download(tickers=mapping[signal],period='1y')
	signals=signals.dropna()

	
	macd = ta.macd(signals['Close'])
	signals = pd.concat([signals, macd], axis=1).reindex(signals.index)


	def MACD_Strategy(df, risk):
		MACD_Buy=[]
		MACD_Sell=[]
		position=False

		for i in range(0, len(df)):
			
			if df['MACD_12_26_9'][i] > df['MACDs_12_26_9'][i] :
				MACD_Sell.append(np.nan)
				if position ==False:
					MACD_Buy.append(df['Adj Close'][i])
					position=True
				else:
					MACD_Buy.append(np.nan)

			elif df['MACD_12_26_9'][i] < df['MACDs_12_26_9'][i] :
				MACD_Buy.append(np.nan)
				if position == True:
					MACD_Sell.append(df['Adj Close'][i])
					position=False
				else:
					MACD_Sell.append(np.nan)

			elif position == True and df['Adj Close'][i] < MACD_Buy[-1] * (1 - risk):
				MACD_Sell.append(df["Adj Close"][i])
				MACD_Buy.append(np.nan)
				position = False

			elif position == True and df['Adj Close'][i] < df['Adj Close'][i - 1] * (1 - risk):
				MACD_Sell.append(df["Adj Close"][i])
				MACD_Buy.append(np.nan)
				position = False

			else:
				MACD_Buy.append(np.nan)
				MACD_Sell.append(np.nan)

		signals['MACD_Buy_Signal_price'] = MACD_Buy
		signals['MACD_Sell_Signal_price'] = MACD_Sell


	MACD_strategy = MACD_Strategy(signals,0.025)

	signals=signals.reset_index()

	mn=signals['Close'].min()
	mx=signals['Close'].max()

	chart21=alt.Chart(signals).mark_line().encode(x='Date',y=alt.Y('Close',title='Close/₹',scale=alt.Scale(domain=[mn,mx])))
	chart22=alt.Chart(signals).mark_point(shape='triangle', color='green',size=300,filled=True).encode(x='Date',y='MACD_Buy_Signal_price')
	chart23=alt.Chart(signals).mark_point(shape='triangle-down', color='red',size=300,filled=True).encode(x='Date',y='MACD_Sell_Signal_price')

	chart2=alt.layer(chart21,chart22,chart23).properties(height=500).interactive()
	
	st.altair_chart(chart2,use_container_width=True)





with footer:
	st.write("AMBILIO Technology")





for seconds in range(1000):

	
	with UpperBlock:

		with col1:

			df = yf.download(tickers=mapping[display1], period="1y", interval='1d')
			df=df.Close
			df=df.reset_index()

			chart1=alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color="blue")).encode(x=alt.X(df.columns[0],title='Date'), 
				y=alt.Y('Close',title='Close/₹',scale=alt.Scale(domain=(df['Close'].min()-(0.001*df['Close'].min()),
					df['Close'].max()+(0.001*df['Close'].max()))))).properties(height=500).interactive()

			placeholderRASO.altair_chart(chart1,use_container_width=True)
		
		with col2:
			end=datetime.now()
			start=end-timedelta(hours=end.hour,minutes=end.minute,seconds=end.second)

			try:
				sub_data_1=yf.download(tickers="INR=X", start=start, end=end, interval = "1m")
				dol_close=sub_data_1['Close'][-1]
				dol_diff=dol_close-sub_data_1['Open'][0]
				placeholder1.metric("United States Dollar",str('1$ = '+'{:.2f}'.format(dol_close)+' ₹'),str('{:.5f}'.format(dol_diff)+' ₹'))
			except:
				placeholder1.metric("United States Dollar",str(""),str(""))

			try:	
				sub_data_2=yf.download(tickers="EURINR=X", start=start, end=end, interval = "1m")
				eur_close=sub_data_2['Close'][-1]
				eur_diff=eur_close-sub_data_2['Open'][0]
				placeholder2.metric("EURO",str('1€ = '+'{:.2f}'.format(eur_close)+' ₹'),str('{:.5f}'.format(eur_diff))+' ₹')
			except:
				placeholder2.metric("EURO",str(""),str(""))

			try:
				sub_data_3=yf.download(tickers="BTC-INR", start=start, end=end, interval = "1m")
				btc_close=sub_data_3['Close'][-1]
				btc_diff=btc_close-sub_data_3['Open'][0]
				placeholder3.metric("Bitcoin",str('1₿ = '+'{:.2f}'.format(btc_close)+' ₹'),str('{:.5f}'.format(btc_diff))+' ₹')
			except:
				placeholder3.metric("Bitcoin",str(""),str(""))

			try:
				sub_data_4=yf.download(tickers="ETH-INR", start=start, end=end, interval = "1m")
				eth_close=sub_data_4['Close'][-1]
				eth_diff=eth_close-sub_data_4['Open'][0]
				placeholder4.metric("Ethereum",str('1Ξ = '+'{:.2f}'.format(eth_close)+' ₹'),str('{:.5f}'.format(eth_diff))+' ₹')
			except:
				placeholder4.metric("Ethereum",str(""),str(""))


		time.sleep(3)

