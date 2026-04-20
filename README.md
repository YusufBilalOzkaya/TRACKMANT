# 🎯 TRACKMANT: Universal Web Tracking & Notification System

<p align="center">
  <img src="https://img.shields.io/badge/English-Selected-green?style=for-the-badge" alt="English">
  <img src="https://img.shields.io/badge/Türkçe-Mevcut-red?style=for-the-badge" alt="Türkçe">
</p>

---
## 🌐 English

### 🎯 Overview
TRACKMANT is a professional tracking tool that automatically monitors data (price, stock, news, numerical values, etc.) on any web page, analyzes changes, and notifies you instantly via email.

### ✨ Features
- **🔍 Smart Tracking:** Monitor any element on a page with CSS Selector support.
- **📧 Instant Notifications:** Get emails when price changes or crosses your defined thresholds.
- **🖥️ Modern Dashboard:** Sleek, dark-themed, and user-friendly web interface.
- **🖱️ Visual Picker:** Choose elements simply by clicking, no coding required.
- **⏰ Scheduled Tasks:** Automatic checks at your defined intervals (e.g., every 2 minutes).

### 🛠️ Setup Guide

#### 1️⃣ Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

#### 2️⃣ Environment Configuration (.env)
1. Create a file named `.env` in the root directory.
2. Copy contents from `.env.example`.
3. Fill in your SMTP details (use "App Password" for Gmail).

#### 3️⃣ Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 🚀 Usage
- **Start Backend:** `cd backend && python main.py`
- **Start Frontend:** `cd frontend && npm run dev`
- **Use Picker:** `cd picker && python picker.py` to visually select CSS elements.

---

## 🇹🇷 Türkçe

### 🎯 Genel Bakış
TRACKMANT; herhangi bir web sayfasındaki veriyi (fiyat, stok, haber, sayısal değerler vb.) otomatik olarak takip eden, değişimleri analiz eden ve sizi anında e-posta ile bilgilendiren profesyonel bir izleme aracıdır.

### ✨ Özellikler
- **🔍 Akıllı İzleme:** CSS Selector desteği ile sayfanın herhangi bir noktasındaki veriyi takip edin.
- **📧 Anlık Bildirim:** Değişim olduğunda veya belirlediğiniz limitlerin altına/üstüne inildiğinde e-posta alın.
- **🖥️ Modern Dashboard:** Şık, koyu temalı ve kullanımı kolay web arayüzü.
- **🖱️ Visual Picker:** Kod yazmadan, sadece tıklayarak takip etmek istediğiniz öğeyi seçin.
- **⏰ Zamanlanmış Görevler:** Belirlediğiniz aralıklarla otomatik kontrol.

### 🛠️ Kurulum Rehberi

#### 1️⃣ Backend Kurulumu
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
playwright install
```

#### 2️⃣ Yapılandırma (.env)
1. Kök dizinde `.env` dosyası oluşturun.
2. `.env.example` içeriğini kopyalayın.
3. Bilgilerinizi doldurun (Gmail için "Uygulama Şifresi" kullanın).

#### 3️⃣ Frontend Kurulumu
```bash
cd frontend
npm install
npm run dev
```

### 🚀 Çalıştırma
- **Backend:** `cd backend && python main.py`
- **Frontend:** `cd frontend && npm run dev`
- **Picker:** `cd picker && python picker.py`

---
<p align="center">TRACKMANT — Track the data, catch the opportunity.</p>
