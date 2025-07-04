# ImgFlow Telegram Bot 🤖🖼️

ImgFlow is a smart and multilingual Telegram bot that allows users to search and download high-quality images directly from Telegram using the Pexels API. It is designed to be user-friendly, fast, and fully manageable through an integrated admin panel.

---

## 🌟 Key Features

✅ **Multilingual Interface**
Supports three languages for a better user experience:

* 🇺🇿 Uzbek
* 🇷🇺 Russian
* 🇬🇧 English

✅ **Unlimited Image Search**
Users can search for any keyword and receive high-quality images instantly, with the option to request multiple images at once.

✅ **Admin Control Panel**
Admin has full control over the bot, including the ability to:

* View logs and download them as `.txt`
* View and download user lists
* Ban or unban users
* Broadcast text, images, videos, audio, or documents to all users
* Clear logs and user files to manage storage
* Monitor real-time statistics of users and banned accounts

✅ **User Management & Security**

* Automatically registers new users into a `users.txt` file
* Bans and blocks unwanted users from using the bot
* Keeps full logs for transparency and accountability

✅ **Media Broadcasting**
Admins can send:

* Text messages
* Photos
* Videos
* Voice messages
* Documents

… to all users with a single command or file.

---

## 🚀 Installation Guide

### Requirements

* Python 3.9 or higher
* Telegram Bot Token
* Pexels API Key (Get it free from [https://www.pexels.com/api/](https://www.pexels.com/api/))

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/ImgFlow.git
cd ImgFlow
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Tokens

* Put your Telegram bot token in `token.txt` or directly into the code (`TOKEN` variable).
* Put your Pexels API key inside the `PEXELS_API_KEY` variable.

### 5️⃣ Run the Bot

```bash
python main.py
```

---

## 📜 Command List (Admin Only)

| Command                       | Description                                                     |
| ----------------------------- | --------------------------------------------------------------- |
| `/getlogs`                    | 📄 Download `log.txt` (bot activity logs).                      |
| `/getusers`                   | 👥 Download `users.txt` and see total user count.               |
| `/clearlogs`                  | 🧹 Clear logs (`log.txt`).                                      |
| `/clearusers`                 | 🧹 Clear all user registrations (`users.txt`).                  |
| `/stats`                      | 📊 Show statistics: total users, banned users, recent activity. |
| `/ban <user_id>`              | 🛘 Ban a user (blocks bot access).                              |
| `/unban <user_id>`            | ✅ Unban a previously banned user.                               |
| `/broadcast <text>`           | 📢 Send a text message to **all users**.                        |
| *(Send any media to the bot)* | 📤 Sends images, videos, audio, or files to all users.          |

---

## 📂 File Structure Overview

| File Name          | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| `main.py`          | Main Python file containing the bot's logic                  |
| `requirements.txt` | Required Python packages (`python-telegram-bot`, `requests`) |
| `token.txt`        | Telegram bot token (keep it secret!)                         |
| `users.txt`        | Automatically generated user list                            |
| `log.txt`          | Automatically generated logs                                 |
| `banned.txt`       | List of banned user IDs                                      |
| `queries.txt`      | Saved user queries                                           |
| `venv/`            | Python virtual environment folder                            |

---

## 🛡 Security & Privacy Notes

* **NEVER** share your `token.txt` or API key publicly.
* Do not hardcode sensitive keys in public repositories.
* Make sure logs do not contain sensitive private information before sharing.

---

## 📊 Statistics Example

Running `/stats` will return something like:

```
👥 Total users: 125
🛘 Banned users: 3
📄 Total searches: 567
```

---

## 🔗 Useful Links

* Pexels API: [https://www.pexels.com/api/](https://www.pexels.com/api/)
* Telegram BotFather: [https://t.me/BotFather](https://t.me/BotFather)
* Telegram Python Library: [https://github.com/python-telegram-bot/python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

---

## 🤝 Contributions & Feedback

Pull requests, issues, and suggestions are welcome!

Feel free to:

* 🌟 Star this repository
* 📝 Fork it and customize
* 🚀 Deploy your own version

---

## 📢 Bot Link

👉 Try the bot: [@imgcncbot](https://t.me/imgcncbot)

---

### Developed by **cncdev7** with ❤️
