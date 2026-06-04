import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import requests

# ตั้งค่าหน้าจอแดชบอร์ด
st.set_page_config(layout="wide", page_title="Advanced Pro Stock Dashboard")
st.title("📊 Real-Time Advanced Stock Analytics Dashboard")
st.caption("ระบบวิเคราะห์หุ้นเรียลไทม์: งบการเงิน | Elliott Wave | Smart Money Concepts (SMC)")

st.markdown("---")

# ปรับปรุง: ย้ายช่องค้นหามาไว้ตรงกลางด้านบนสุด เพื่อให้ไอแพดและมือถือใช้งานง่าย
col_search1, col_search2 = st.columns([3, 1])
with col_search1:
    ticker_input = st.text_input("พิมพ์ชื่อหุ้นที่คุณต้องการค้นหา (เช่น AAPL, TSLA, NVDA หรือหุ้นไทย เช่น PTT.BK):", value="AAPL")
with col_search2:
    st.write(" ") 
    st.write(" ")
    search_button = st.button("🔍 กดเพื่อค้นหา/อัปเดตข้อมูล")

# แปลงชื่อหุ้นเป็นพิมพ์ใหญ่
ticker_input = ticker_input.upper().strip()

if ticker_input:
    try:
        # แก้ปัญหาโดนบล็อก: สร้าง Session พิเศษหลอกระบบว่าเป็นเบราว์เซอร์จริงเพื่อไม่ให้ Cloud โดนบล็อกข้อมูล
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'})
        
        # ดึงข้อมูลจาก yfinance API ผ่าน Session พิเศษ
        stock = yf.Ticker(ticker_input, session=session)
        info = stock.info
        
        # ส่วนที่ 1: ข้อมูลทั่วไปและราคาเรียลไทม์
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("ราคาปัจจุบัน", f"${info.get('currentPrice', info.get('regularMarketPrice', 0)):,.2f}")
        col2.metric("เป้าหมายเฉลี่ยจากนักวิเคราะห์ (Target High)", f"${info.get('targetHighPrice', 0):,.2f}")
        col3.metric("Forward P/E (การเติบโต)", f"{info.get('forwardPE', 0):,.2f}x")
        col4.metric("Market Cap", f"${info.get('marketCap', 0):,.0f}")
        
        st.markdown("---")
        
        # จัด Layout หน้าจอแบ่งเป็น 2 ฝั่ง 
        left_chart_col, right_fundamental_col = st.columns(2)
        
        with left_chart_col:
            st.subheader("📈 กราฟหุ้นเรียลไทม์จาก TradingView")
            
            # แปลงรหัสให้ TradingView เข้าใจได้แม่นยำขึ้น
            tv_symbol = ticker_input
            if ".BK" in tv_symbol:
                tv_symbol = "SET:" + tv_symbol.replace(".BK", "")
            elif tv_symbol in ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL"]:
                tv_symbol = "NASDAQ:" + tv_symbol
            else:
                tv_symbol = "NYSE:" + tv_symbol

            tradingview_html = f"""
            <div class="tradingview-widget-container" style="height:450px;width:100%;">
              <div id="tradingview_chart"></div>
              <script type="text/javascript" src="https://tradingview.com"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "th",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_chart"
              }});
              </script>
            </div>
            """
            components.html(tradingview_html, height=470)
            
            # ส่วนที่ 2: ระบบตรวจจับทางเทคนิคัลขั้นสูง 
            st.subheader("🤖 ระบบตรวจจับรูปแบบเชิงเทคนิคัลอัตโนมัติ")
            hist = stock.history(period="1y", interval="1d")
            
            if not hist.empty:
                close_prices = hist['Close'].values
                high_prices = hist['High'].values
                low_prices = hist['Low'].values
                
                is_wave_3 = False
                recent_return = (close_prices[-1] - close_prices[-20]) / close_prices[-20] if len(close_prices) > 20 else 0
                volume_ma = hist['Volume'].rolling(window=20).mean().iloc[-1] if len(hist) > 20 else 1
                recent_volume = hist['Volume'].iloc[-1]
                
                if recent_return > 0.15 and recent_volume > (volume_ma * 1.5):
                    is_wave_3 = True
                
                last_low = low_prices[-5] if len(low_prices) > 5 else 0
                smc_status = "Ranging (สะสมพลัง)"
                order_block = f"${last_low:,.2f} - ${last_low*1.02:,.2f}"
                
                if len(close_prices) > 20:
                    if close_prices[-1] > max(high_prices[-20:-1]):
                        smc_status = "🟢 Break of Structure (BOS) - ขาขึ้น"
                    elif close_prices[-1] < min(low_prices[-20:-1]):
                        smc_status = "🔴 Change of Character (CHoCH) - ขาลง"

                smc_col, wave_col = st.columns(2)
                with smc_col:
                    st.info("🎯 *วิเคราะห์ทฤษฎี SMC*")
                    st.write(f"- *โครงสร้างราคา:* {smc_status}")
                    st.write(f"- *โซน Order Block:* {order_block}")
                    
                with wave_col:
                    st.info("🌊 *วิเคราะห์ Elliott Wave*")
                    if is_wave_3:
                        st.success("🚨 *สัญญาณ: เข้าสู่ WAVE 3*")
                    else:
                        st.write("- *คำอธิบาย:* อยู่ในคลื่นปรับฐาน หรือสะสมพลังขึ้นเวฟใหม่")
            else:
                st.warning("ไม่สามารถดึงข้อมูลย้อนหลังมาคำนวณระบบเวฟได้")

        with right_fundamental_col:
            # ส่วนที่ 3: งบการเงินและอัตราการเติบโตในอนาคต 
            st.subheader("📋 งบการเงินและการเติบโตในอนาคต")
            tab1, tab2, tab3 = st.tabs(["งบกำไรขาดทุน", "งบดุล", "การคาดการณ์อนาคต"])
            
            with tab1:
                st.write("*งบกำไรขาดทุนย้อนหลัง (Income Statement)*")
                if stock.financials is not None and not stock.financials.empty:
                    st.dataframe(stock.financials.iloc[:8, :4], use_container_width=True)
                else:
                    st.write("ไม่พบข้อมูล")
                    
            with tab2:
                st.write("*งบดุล (Balance Sheet)*")
                if stock.balance_sheet is not None and not stock.balance_sheet.empty:
                    st.dataframe(stock.balance_sheet.iloc[:8, :4], use_container_width=True)
                else:
                    st.write("ไม่พบข้อมูล")
                    
            with tab3:
                st.write("*อัตราการเติบโตและการประเมินมูลค่า (Growth)*")
                growth_df = pd.DataFrame({
                    "ตัวชี้วัดความเติบโต": ["Quarterly Revenue Growth", "Earnings Growth", "Profit Margin", "Return on Equity (ROE)"],
                    "มูลค่าจริง": [
                        f"{info.get('quarterlyRevenueGrowth', 0)*100:.2f}%" if info.get('quarterlyRevenueGrowth') else "N/A",
                        f"{info.get('quarterlyEarningsGrowth', 0)*100:.2f}%" if info.get('quarterlyEarningsGrowth') else "N/A",
                        f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "N/A",
                        f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "N/A"
                    ]
                })
                st.table(growth_df)
                st.warning(f"คำแนะนำหลัก: {info.get('recommendationKey', 'No Data').upper()}")

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลหุ้น '{ticker_input}'")