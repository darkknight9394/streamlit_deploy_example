import streamlit as st

def select_ticker():
    ticker = st.session_state.ticker_universe[0].upper()

    from streamlit_tags import st_tags
    keywords = st_tags(
        label='',## Enter Keywords:',
        text='Press enter ticker for lookup',
        value=[ticker],
        suggestions = st.session_state.ticker_universe,
        maxtags = 1,
        )
    if len(keywords) > 0:
        if keywords[0].upper() in st.session_state.ticker_universe:
            st.write(keywords[0])
            ticker = keywords[0].upper()
        else:
            st.write("PLEASE CHECK TICKER")
    else:
        st.write("KEYWORD LIST IS EMPTY")
    return ticker

def app():
    import pandas as pd
    import datetime
    import streamlit as st
    from utils.load_data import load_time_series_data_refintiv, load_SCTRSCORE_df, load_RSSCORE_df, load_MRSQUARE_df

    rs_score_df = load_RSSCORE_df()
    sctr_score_df = load_SCTRSCORE_df()
    mrsquare_score_df = load_MRSQUARE_df()

    ticker = select_ticker()
    df = load_time_series_data_refintiv(ticker)

    default_date = datetime.date(day=7,month=4,year=2022)
    selected_date = st.date_input("Select Date", default_date, min_value = df.iloc[0]['date'], max_value=df.iloc[-1]['date'])

    st.write('Selected date:', selected_date)

    import datetime
    dt = datetime.datetime(year=selected_date.year, month=selected_date.month,day=selected_date.day)

    # step 1 plot historical time series
    from deploy_pages.vcp_page import set_up_time_series_plot, clean_up_axis

    # note we subset datahere.
    # this is not fast enough (need to cache and speed it up
    df_in = df[(df['date'] >= dt-datetime.timedelta(days=500)) & (df['date'] <= dt)]
    df_in.reset_index(inplace=True)

    fig = set_up_time_series_plot(ticker, df_in)
    fig, clean_up_axis(fig, ticker, str(selected_date))
    st.plotly_chart(fig)

    st.write('---')
    # step 2 plot factors
    col1, col2, col3 = st.columns(3)
    selected_date_time_stamp = pd.to_datetime(dt)
    st.write("As of: "+ str(selected_date_time_stamp.date()))

    col1.metric("Relative Strength", round(rs_score_df.loc[selected_date_time_stamp][ticker],2))
    col2.metric("SCTR", round(sctr_score_df.loc[selected_date_time_stamp][ticker],2))
    col3.metric("Stock on the move", round(mrsquare_score_df.loc[selected_date_time_stamp][ticker],2))