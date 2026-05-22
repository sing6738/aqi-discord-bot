import requests
import schedule
import time
import datetime

WEBHOOK_URL = "your_discord_webhook"
IQAIR_TOKEN = "your_Apiiqair"
LAT, LON    = 16.4322, 103.5058

def fetch_aqi() -> dict:
    url  = f"http://api.airvisual.com/v2/nearest_city?lat={LAT}&lon={LON}&key={IQAIR_TOKEN}"
    data = requests.get(url, timeout=10).json()
    if data.get("status") != "success":
        raise ValueError(f"API error: {data.get('data', 'Unknown error')}")
    d = data["data"]["current"]["pollution"]
    return {
        "aqi":  d["aqius"],
        "pm25": "N/A",  # แพ็กเกจฟรีของ IQAir ไม่ได้ให้ค่าความเข้มข้น PM2.5 โดยตรง ให้มาแค่ AQI
    }

def running_advice(aqi: int) -> tuple:
    if aqi <= 50:
        return "ดี", "วิ่งได้เลย เหมาะมากๆ", "🟢", 0x2ECC71
    elif aqi <= 100:
        return "ปานกลาง", "วิ่งได้ แต่ถ้าแพ้ฝุ่นให้ระวัง", "🟡", 0xF1C40F
    elif aqi <= 150:
        return "ไม่ดีต่อกลุ่มเสี่ยง", "ไม่แนะนำถ้าเป็นโรคระบบหายใจ", "🟠", 0xE67E22
    elif aqi <= 200:
        return "ไม่ดี", "ไม่ควรวิ่งกลางแจ้ง ใส่หน้ากากถ้าออกนอกบ้าน", "🔴", 0xE74C3C
    else:
        return "อันตราย", "ห้ามวิ่งกลางแจ้งเด็ดขาด", "🟣", 0x9B59B6

def send_report():
    try:
        data  = fetch_aqi()
        level, advice, emoji, color = running_advice(data["aqi"])
        now   = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        embed = {
            "title": f"{emoji} รายงานคุณภาพอากาศ — กาฬสินธุ์",
            "description": f"**วิ่งดีไหมวันนี้?**\n🏃‍♂️ {advice}",
            "color": color,
            "fields": [
                {"name": "💨 ค่า AQI (US)", "value": f"**{data['aqi']}**", "inline": True},
                {"name": "📊 ระดับ", "value": f"**{level}**", "inline": True}
            ],
            "footer": {"text": f"อัปเดตข้อมูลเมื่อ: {now}"}
        }

        r = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        print(f"[{now}] ส่งสำเร็จ AQI={data['aqi']} status={r.status_code}")

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

schedule.every().day.at("07:00").do(send_report)

print("Bot เริ่มทำงานแล้ว กำลังทดสอบส่งครั้งแรก...")
send_report()

while True:
    schedule.run_pending()
    time.sleep(30)