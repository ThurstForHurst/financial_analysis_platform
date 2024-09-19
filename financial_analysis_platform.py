import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


security = st.sidebar.text_input("Stock Ticker", value="AAPL")
start_date = st.sidebar.date_input("Data Start Date", min_value=None, max_value=dt.date.today(), value=dt.date(2010, 1, 1))
end_date = st.sidebar.date_input("Data Start Date", min_value=None, value=dt.date.today())


security_data = yf.download(security, start_date, end_date)
security_info = yf.Ticker(security).info


def main():
    df, vol_df = create_df(security_data)
    daily_return = str(round((df.iloc[-1, -1] - df.iloc[-2, -1])/df.iloc[-1, -1]*100, 2))


    ## Creating the Title and the Company about info

    st.title(security_info["longName"])


    ## Displaying the latest price point and changing the colour based on whether it increased or         ## decreased in value.

    st.header("Price: " + str(df.iloc[-1, -1]))
    if float(daily_return) > 0:
        st.markdown(f"<p>Change: <span style='color: green;'>{daily_return}%</span></p>", unsafe_allow_html=True)
    elif float(daily_return) < 0:
        st.markdown(f"<p>Change: <span style='color: red;'>{daily_return}%</span></p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p>Change: {daily_return}%</p>", unsafe_allow_html=True)


    ## Generating buttons that will affect the price chart and volume chart.

    days_7, month_1, months_6, years_1, selection = st.columns([1, 1, 1, 1, 1], vertical_alignment="center")


    with days_7: 
        if st.button("7-days"):
            df = df.iloc[-7:, :]
            vol_df = vol_df.iloc[-7:, :]

    with month_1: 
        if st.button("30-days"):
            df = df.iloc[-30:, :]
            vol_df = vol_df.iloc[-30:, :]

    with months_6: 
        if st.button("6-months"):
            df = df.iloc[-131:, :]
            vol_df = vol_df.iloc[-131:, :]

    with years_1: 
        if st.button("1-year"):
            df = df.iloc[-250:, :]
            vol_df = vol_df.iloc[-250:, :]
            
    with selection:
        if st.button("Selection"):
            df, vol_df = create_df(security_data)


    give_df(df, vol_df)


    ## Creating a section for fundamentals information
    st.subheader("About")
    try:
        st.write(security_info["longBusinessSummary"])
    except:
        st.empty()

    st.markdown(f"""
        <br>
        <style>
            .table2 {{
                display: flex;
                flex-direction: column;
                border: solid 1px gray;
            }}
                
            .record {{
                display: flex;
                width: 100%;
                justify-content: center;
            }}

            .contact-name,
            .contact-data {{
                border: solid 1px lightgray;
                flex: 1;
            }}
                
            .contact-data {{
                display: flex;
                justify-content: center;
            }}
                
            .contact-name {{
                padding-left: 5px;
            }}
        </style>        
        
        <div class="table2">
            <div class="record">
                <div class="contact-name">Industry</div>
                <div class="contact-data">{get_info("industry", security_info)}</div>
            </div>
            <div class="record">
                <div class="contact-name">Sector</div>
                <div class="contact-data">{get_info("sector", security_info)}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    

    st.header("Fundamentals:")
    st.markdown(f"""
        <style>
            p {{
                margin: 0;
            }}
                
            h6 {{
                padding: 0;
                margin: 0;
            }}
                
            h3 {{
                padding-bottom: 10px;
                padding-top: 10px;
            }}

            .table1 {{
                display: flex;
                flex-direction: column;
                width: 70%;
                border: solid 1px gray;
            }}

            .record {{
                display: flex;
                flex: 2 3;
            }}
                
            .title-record {{
                display: flex;
                align-items: center;
                justify-content: center;
            }}
                
            .fundamental-name {{
                flex: 1;
                display: flex;

                align-items: center;
                justify-content: left;

                padding: 2vh 1vh 2vh 1vh;
            }}
                
            .fundamental-data {{
                flex: 2;
                display: flex;

                align-items: center;
                justify-content: center;
                padding: 2vh 1vh 2vh 1vh;
            }}
                
            .fundamental-name,
            .fundamental-data {{
                border: solid 1px lightgrey;
            }}
        </style>
                
        <div class='table1'>
            <div class='record title-record'><h3>Profitability</h3></div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>EPS</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{'$'}{get_info("trailingEps", security_info)}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Gross Margin</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{str(round(get_info("grossMargins", security_info)*100)) + "%" if get_info("grossMargins", security_info) is not None else 'Unavailable'}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Operating Margin</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("operatingMargins", security_info)*100)}%</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Return on Assets</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("returnOnAssets", security_info)*100, 2)}%</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Return on Equity</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>${round(get_info("returnOnEquity", security_info), 2)}</p>
                </div>
            </div>
            <div class='record title-record'><h3>Valuation</h3></div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Trailing P/E Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(df.iloc[-1, -1]/get_info("trailingEps", security_info), 2)}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Trailing P/S Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("priceToSalesTrailing12Months", security_info), 2)}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>P/B Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("priceToBook", security_info), 2)}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>PEG Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("pegRatio", security_info), 2)}</p>
                </div>
            </div>
            <div class='record title-record'><h3>Dividends</h3></div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>DPS</h6>
                </div>
                <div class='fundamental-data'>
                    <p>${get_info("dividendRate", security_info):.2f}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Dividend Yield</h6>
                </div>
                <div class='fundamental-data'>
                    <p>{round(get_info("dividendYield", security_info)*100, 2)}%</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Payout Ratio</h6>
                </div>
                <div class='fundamental-data'>
                    <p>{round(to_percent(get_info("payoutRatio", security_info)), 2)}%</p>
                </div>
            </div>
        </div>
        <br>
    """, unsafe_allow_html=True)



    ## This section explores risk metrics and provides key insights for strategic decision making

    # The first part of this risk section shows different Variance at Risk 

    st.header("Risk Insights")
    give_hist(df, 90)
    give_hist(df, 95)
    give_hist(df, 99)

    give_var_chart(df)
    give_vol_chart(df)

    # The secon part of the risk section shows the different risk fundamentals values and balance sheet information

    st.subheader("Risk Metrics")
    st.markdown(f"""
        <style>
            p {{
                margin: 0;
            }}
                
            h6 {{
                padding: 0;
                margin: 0;
            }}
                
            h3 {{
                padding-bottom: 10px;
                padding-top: 10px;
            }}

            .table1 {{
                display: flex;
                flex-direction: column;
                width: 70%;
                border: solid 1px gray;
            }}

            .record {{
                display: flex;
                flex: 2 3;
            }}
                
            .title-record {{
                display: flex;
                align-items: center;
                justify-content: center;
            }}
                
            .fundamental-name {{
                flex: 1;
                display: flex;

                align-items: center;
                justify-content: left;

                padding: 2vh 1vh 2vh 1vh;
            }}
                
            .fundamental-data {{
                flex: 2;
                display: flex;

                align-items: center;
                justify-content: center;
                padding: 2vh 1vh 2vh 1vh;
            }}
                
            .fundamental-name,
            .fundamental-data {{
                border: solid 1px lightgrey;
            }}
        </style>
                
        <div class='table1'>
            <div class='record title-record'><h3>Risk Metrics</h3></div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Company Beta</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("beta", security_info), 2)}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Debt to Equity Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("debtToEquity", security_info), 2) if get_info("debtToEquity", security_info) is not None else 'Unavailable'}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Quick Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("quickRatio", security_info), 2) if get_info("quickRatio", security_info) is not None else 'Unavailable'}</p>
                </div>
            </div>
            <div class='record'>
                <div class='fundamental-name'>
                    <h6>Current Ratio</h6>
                </div>
                 <div class='fundamental-data'>
                    <p>{round(get_info("currentRatio", security_info), 2) if get_info("currentRatio", security_info) is not None else 'Unavailable'}</p>
                </div>
            </div>
        </div>
        <br>

    """, unsafe_allow_html=True)

    st.subheader("Balance Sheet Information")
    st.write(pd.DataFrame(yf.Ticker(security).balance_sheet).iloc[1:, :4])
    st.empty()


    ## This section will display the contact information for the chosen stock

    st.header("Contact Information")
    st.markdown(f"""
        <style>
            .table2 {{
                display: flex;
                flex-direction: column;
                border: solid 1px gray;
            }}
                
            .record {{
                display: flex;
                width: 100%;
                justify-content: center;
            }}

            .contact-name,
            .contact-data {{
                border: solid 1px lightgray;
                flex: 1;
            }}
                
            .contact-data {{
                display: flex;
                justify-content: center;
            }}
                
            .contact-name {{
                padding-left: 5px;
            }}
        </style>        
        
        <div class="table2">
            <div class="record">
                <div class="contact-name">Address</div>
                <div class="contact-data">{get_info("address1", security_info)}, {get_info("city", security_info)}</div>
            </div>
            <div class="record">
                <div class="contact-name">State</div>
                <div class="contact-data">{get_info("state", security_info)}, {get_info("zip", security_info)}</div>
            </div>
            <div class="record">
                <div class="contact-name">Country</div>
                <div class="contact-data">{get_info("country", security_info)}</div>
            </div>
            <div class="record">
                <div class="contact-name">Phone</div>
                <div class="contact-data">{get_info("phone", security_info)}</div>
            </div>
            <div class="record">
                <div class="contact-name">Website</div>
                <div class="contact-data"><a href="{get_info("website", security_info)}" target="blank_">{get_info("website", security_info)}</a></div>
            </div>
        </div>
    """, unsafe_allow_html=True)





def create_df(data):
    df = pd.DataFrame(data
                      .Close
                      .round(2))
    
    vol_df = pd.DataFrame(data
                          .Volume)
    
    return df, vol_df

def give_df(df, vol_df):
    df_min = df.min()[-1]
    df_max = df.max()[-1]

    fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    ax.plot(df)
    ax.set_ylim([df_min-5, df_max+2])
    ax.grid(True, which='both', axis='y', linestyle='-', linewidth=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('gray')
    ax.spines['left'].set_visible(False)

    ax.xaxis.label.set_color('gray')
    ax.yaxis.label.set_color('gray')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='gray')  

    plt.xticks(rotation=45)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %y'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())


    ax.set_ylabel('Price (USD)')


    ax2.bar(vol_df.index, vol_df["Volume"], color="#4683B7")
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')
    ax2.grid(True, which='both', axis='y', linestyle='-', linewidth=0.4)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))
    ax2.set_ylim([0, vol_df["Volume"].max() * 1.1])

    st.pyplot(fig)


def give_hist(df, risk):
    df_local = df.copy()

    df_local["returns"] = df.pct_change()

    cutoff = np.percentile(df_local["returns"].dropna(), 100-risk)

    fig, ax = plt.subplots(figsize=(10, 6))
    counts, bins, patches = ax.hist(df_local['returns'], bins=200, edgecolor='black', alpha=0.7)

    # Change color of bins below the percentile
    for count, bin_start, bin_end, patch in zip(counts, bins[:-1], bins[1:], patches):
        if bin_end < cutoff:
            patch.set_facecolor('red')
        elif bin_start < cutoff:
            patch.set_facecolor('red')
        else:
            patch.set_facecolor('blue')
    
    ax.set_title('Histogram of Returns')
    ax.set_xlabel('Return')
    ax.set_ylabel('Frequency')
    ax.grid(True, linestyle='-', linewidth=0.2, color='lightgray')

    st.subheader(f"Value at Risk for the {risk}% level")
    st.write(f"At a VaR level of {risk}%, there is a {100-risk}% chance of making a {round(cutoff * 100, 2)}% loss")
    st.pyplot(fig)


def give_vol_chart(df):
    df_local = df.copy()
    df_local["returns"] = df.pct_change()
    df_local = df_local.dropna(subset=["returns"])

    df_local['rolling_volatility'] = df_local['returns'].rolling(window=30).std()
    df_local["mean_volatility"] = df_local['rolling_volatility'].mean()

    st.markdown(f"""
        <style>
            .chart-heading {{
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
        </style>
                    
        <div class="chart-heading"><h4>30-Day Rolling Volatility of Returns</h4></div>
    """, unsafe_allow_html=True)

    st.line_chart(df_local.drop(columns=["Close", "returns"]), color=["#000000", "#E4080A"], x_label="Time", y_label="Volatility")


def give_var_chart(df):
    df_local = df.copy()
    df_local["returns"] = df.pct_change()
    df_local = df_local.dropna(subset=["returns"])
    df_local["mean_return"] = df_local['returns'].mean()

    st.markdown(f"""
        <style>
            .chart-heading {{
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
        </style>
                    
        <div class="chart-heading"><h4>Variance of Returns</h4></div>
    """, unsafe_allow_html=True)
    st.line_chart(df_local.drop("Close", axis=1), color=["#000000", "#E4080A"], x_label="Time", y_label="Variance")


def get_info(item, object):
    try:
        return object.get(item)
    except:
        return "Unavailable"
    

def to_percent(number):
    return number*100

if __name__ == "__main__":
    main()
