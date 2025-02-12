import requests
import schedule
import time

# ========== 1. 配置部分，需根据自己的情况修改 ==========

# 你的 wechatbot-webhook 服务地址和 token
WEBHOOK_BASE_URL = "http://localhost:3001"
WEBHOOK_TOKEN = ""

# 发送消息的微信群名称（与你微信里的群名相同）
GROUP_NAME = "qwer"

# 2. 构造最终的 API 接口
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}/webhook/msg/v2?token={WEBHOOK_TOKEN}"


# ========== 2. 获取最新币圈消息函数 ==========

def fetch_crypto_news():
    """
    从CoinGecko获取最新的币圈动态(status_updates)，并返回文本内容。
    注意：此接口返回的内容质量一般，如果需要更专业的新闻源，可替换为其他API或爬虫。
    """
    url = "https://api.coingecko.com/api/v3/status_updates"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        # CoinGecko会返回一个列表，status_updates是动态列表
        updates = data.get("status_updates", [])

        if not updates:
            return "目前没有最新的币圈资讯或无法获取。"

        # 可以根据喜好取前几条；这里简单示例取 3 条动态
        top_updates = updates[:3]

        # 将这几条动态转成简单文本（项目名称 + 标题）
        # 例如： "Bitcoin - Some update"
        msg_list = []
        for item in top_updates:
            project_name = item["project"]["name"]
            title = item["title"]
            msg_list.append(f"【{project_name}】{title}")

        # 拼接成多行字符串
        content = "\n".join(msg_list)
        return f"=== 今日币圈快讯（来自CoinGecko）===\n{content}"

    except Exception as e:
        return f"获取最新币圈消息出错: {e}"


# ========== 3. 调用 webhook 接口发送消息到微信群 ==========

def send_news_to_wechat():
    """
    1) 先获取最新币圈资讯
    2) 再通过 webhook 接口发送到指定微信群
    """
    news_content = fetch_crypto_news()

    # webhook payload 结构
    payload = {
        "to": GROUP_NAME,
        "isRoom": True,     # True 表示发送到群
        "data": {
            "content": news_content
        }
    }

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 发送成功 -> {GROUP_NAME}")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 发送失败 -> {resp.text}")
    except Exception as e:
        print(f"发送失败，出现异常: {e}")


if __name__ == "__main__":
    # 手动测试一次
    send_news_to_wechat()

    # 然后再启动定时任务
    schedule.every().day.at("09:00").do(send_news_to_wechat)
    while True:
        schedule.run_pending()
        time.sleep(1)
