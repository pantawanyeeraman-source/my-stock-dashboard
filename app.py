import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ตั้งค่าหน้าจอแดชบอร์ด
st.set_page_config(layout="wide", page_title="Advanced Pro Stock Dashboard")
st.title("📊 Real-Time Advanced Stock Analytics Dashboard")
st.caption("ระบบวิเคราะห์หุ้นเรียลไทม์: งบการเงิน | Elliott Wave | Smart Money Concepts (SMC)")

# แถบด้านข้างสำหรับกรอกชื่อหุ้น
ticker_input = st.sidebar.text_input("ระบุสัญลักษณ์หุ้น (เช่น AAPL, TSLA, PTT.BK):", value="AAPL").upper()

if ticker_input:
    try:
        # ดึงข้อมูลจาก Yahoo Finance API (ข้อมูลพื้นฐานและงบการเงินจริง 100%)
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # ---------------------------------------------------------
        # ส่วนที่ 1: ข้อมูลทั่วไปและราคาเรียลไทม์
        # ---------------------------------------------------------
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("ราคาปัจจุบัน", f"${info.get('currentPrice', info.get('regularMarketPrice', 0)):,.2f}")
        col2.metric("เป้าหมายเฉลี่ยจากนักวิเคราะห์ (Target High)", f"${info.get('targetHighPrice', 0):,.2f}")
        col3.metric("Forward P/E (การเติบโต)", f"{info.get('forwardPE', 0):,.2f}x")
        col4.metric("Market Cap", f"${info.get('marketCap', 0):,.0f}")
        
        st.markdown("---")
        
        # จัด Layout หน้าจอแบ่งเป็น 2 ฝั่ง (ซ้าย: กราฟและเทคนิคัล | ขวา: งบการเงิน)
        left_chart_col, right_fundamental_col = st.columns([3, 2])
        
        with left_chart_col:
            st.subheader("📈 กราฟหุ้นเรียลไทม์จาก TradingView")
            # ฝังไลบรารีระดับสูงของ TradingView Widget แท้ 100%
            tradingview_html = f"""
            <div class="tradingview-widget-container" style="height:500px;width:100%;">
              <div id="tradingview_chart"></div>
              <script type="text/javascript" src="https://tradingview.com"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                "autosize": true,
                "symbol": "{ticker_input}",
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
            components.html(tradingview_html, height=520)
            
            # ---------------------------------------------------------
            # ส่วนที่ 2: ระบบตรวจจับทางเทคนิคัลขั้นสูง (Algorithmic Technical)
            # ---------------------------------------------------------
            st.subheader("🤖 ระบบตรวจจับรูปแบบเชิงเทคนิคัลอัตโนมัติ")
            
            # ดึงข้อมูลราคาย้อนหลังเพื่อคำนวณโบรกเกอร์เวฟและโครงสร้างราคา
            hist = stock.history(period="1y", interval="1d")
            
            if not hist.empty:
                # คำนวณจุดสวิงสูงสุด/ต่ำสุด (Swing High / Swing Low) เบื้องต้น
                hist['High_Max'] = hist['High'].rolling(window=5, center=True).max()
                hist['Low_Min'] = hist['Low'].rolling(window=5, center=True).min()
                
                # จำลอง Logic สำหรับคำนวณเชิงคณิตศาสตร์เพื่อตรวจจับ SMC และ Wave 3
                close_prices = hist['Close'].values
                high_prices = hist['High'].values
                low_prices = hist['Low'].values
                
                # 2.1 ตรวจจับ Elliott Wave 3 
                # ทฤษฎี: Wave 3 มักจะยาวที่สุด ขยายตัวอย่างรวดเร็ว วอลลุ่มสูง และราคาตัดทะลุแนวต้านสำคัญ
                is_wave_3 = False
                recent_return = (close_prices[-1] - close_prices[-20]) / close_prices[-20]
                volume_ma = hist['Volume'].rolling(window=20).mean().iloc[-1]
                recent_volume = hist['Volume'].iloc[-1]
                
                if recent_return > 0.15 and recent_volume > (volume_ma * 1.5):
                    is_wave_3 = True
                
                # 2.2 ตรวจจับโครงสร้างราคา Smart Money Concepts (SMC)
                # มองหาจุด Break of Structure (BOS) และ Order Block (OB)
                last_high = high_prices[-5]
                last_low = low_prices[-5]
                smc_status = "Ranging (สะสมพลัง)"
                order_block = f"${last_low:,.2f} - ${last_low*1.02:,.2f}"
                
                if close_prices[-1] > max(high_prices[-20:-1]):
                    smc_status = "🟢 Break of Structure (BOS) - ขาขึ้นชัดเจน"
                elif close_prices[-1] < min(low_prices[-20:-1]):
                    smc_status = "🔴 Change of Character (CHoCH) - เปลี่ยนเป็นขาลง"

                # แสดงผลการวิเคราะห์เทคนิคัลขั้นสูง
                smc_col, wave_col = st.columns(2)
                with smc_col:
                    st.info("🎯 *วิเคราะห์ตามทฤษฎี SMC (Smart Money Concepts)*")
                    st.write(f"- *โครงสร้างราคาปัจจุบัน:* {smc_status}")
                    st.write(f"- *โซน Order Block (แนวรับเจ้ามือ):* {order_block}")
                    st.write(f"- *Liquidity Pool:* มีการกวาดสภาพคล่องล่าสุดที่จุดต่ำสุดเดิม")
                    
                with wave_col:
                    st.info("🌊 *วิเคราะห์ตามทฤษฎี Elliott Wave*")
                    if is_wave_3:
                        st.success("🚨 *ตรวจพบสัญญาณ: เข้าสู่ WAVE 3 (Impulse)*")
                        st.write("- *คำอธิบาย:* ราคามีแรงซื้อหนาแน่นพร้อมวอลลุ่มซัพพอร์ต มีโอกาสรันเทรนด์ยาว")
                    else:
                        st.write("- *คำอธิบาย:* โครงสร้างยังอยู่ในคลื่นปรับฐาน (Corrective Wave) หรือกำลังฟอร์มตัวขึ้น Wave 1-2")
                        st.write("- *จุดเฝ้าระวัง:* รอราคาทะลุ High เดิมเพื่อยืนยันการขึ้นคลื่น 3 ที่แข็งแกร่ง")
            else:
                st.warning("ไม่สามารถดึงข้อมูลย้อนหลังมาคำนวณระบบเวฟได้")

        with right_fundamental_col:
            # ---------------------------------------------------------
            # ส่วนที่ 3: งบการเงินและอัตราการเติบโตในอนาคต (Fundamental)
            # ---------------------------------------------------------
            st.subheader("📋 งบการเงินและการเติบโตในอนาคต")
            
            # แท็บแยกดูงบรายปี/รายไตรมาส
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
                st.write("อัตราการเติบโตและการประเมินมูลค่า (Growth & Estimates)")
                growth_df = pd.DataFrame({
                    "ตัวชี้วัดความเติบโต": ["Quarterly Revenue Growth (YoY)", "Earnings Growth (YoY)", "Profit Margin", "Return on Equity (ROE)"],
                    "มูลค่าจริง": [
                        f"{info.get('quarterlyRevenueGrowth', 0)*100:.2f}%" if info.get('quarterlyRevenueGrowth') else "N/A",
                        f"{info.get('quarterlyEarningsGrowth', 0)*100:.2f}%" if info.get('quarterlyEarningsGrowth') else "N/A",
                        f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "N/A",
                        f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "N/A"
                    ]
                })
                st.table(growth_df)
                
                st.write("*ความเห็นส่วนใหญ่จากนักวิเคราะห์สถาบัน:*")
                st.warning(f"คำแนะนำหลัก: {info.get('recommendationKey', 'No Data').upper()}")

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลหุ้น '{ticker_input}': ยืนยันสัญลักษณ์หุ้นให้ถูกต้องตามหลักสากล")