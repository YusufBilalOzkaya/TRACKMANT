# 🚀 GitHub Actions Setup Guide

Bu rehber, TRACKMANT sistemini GitHub Actions'da kurulumunu adım adım anlatır.

## 🔐 Güvenlik Notu

**Kimse senin mailini göremez!** İşte neden:

### 1️⃣ GitHub Secrets (Tamamen Gizli)
- Sadece **repository admin'leri** görebilir
- Çalışan logs'larda **asla gösterilmez**
- Şifreli olarak depolanır

### 2️⃣ .env Dosyası
- `.gitignore`'da ekliydi: ✅
- **Local bilgisayarında** kalır
- GitHub'a yüklenmez

### 3️⃣ Workflow Logs
- Actions sekmesinde görüntülenebilir
- **Secrets otomatik maskelenir** (çıktı: `***`)
- Repository private ise, sadece collaborators görebilir

---

## 📋 Kurulum Adımları

### Adım 1: GitHub'a Git Push Yap

```bash
git add .github/
git commit -m "feat: Add GitHub Actions CI/CD pipeline"
git push origin main
```

### Adım 2: GitHub Repository'de Secrets Ekle

#### Tarayıcıdan:

1. GitHub'da reponuza gidin
2. **Settings** → **Secrets and variables** → **Actions** seçin
3. **New repository secret** butonuna tıklayın

#### Eklenecek Secrets:

| Secret Name | Değer | Örnek |
|-------------|-------|--------|
| `SMTP_USER` | Gmail/Outlook e-posta | `senin-email@gmail.com` |
| `SMTP_PASS` | App Password (Gmail için) | `abcd efgh ijkl mnop` |
| `SMTP_SERVER` | SMTP sunucusu (opsiyonel) | `smtp.gmail.com` |
| `SMTP_PORT` | Port numarası (opsiyonel) | `587` |

### Adım 3: Gmail App Password Oluştur (Gmail kullanıyorsanız)

1. https://myaccount.google.com/ → **Security** seç
2. **2-Step Verification** aktif et (yoksa git, yap)
3. "App passwords" bul ve oluştur
4. **Mail** → **Windows Computer** seç (veya device'ın)
5. 16 karakterlik password'u kopyala
6. Bu password'u `SMTP_PASS` secret'ına yapıştır

### Adım 4: Secrets Kontrol Et

```bash
# Yerel bilgisayarında, .env dosyası oluştur (commit etme!)
cat > backend/.env << EOF
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=senin-email@gmail.com
SMTP_PASS=senin-app-password-16chars
CHECK_INTERVAL_MINUTES=2
EOF

# Test et
cd backend && python main.py
```

---

## 🔄 Workflow'lar Nelerdir?

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
- Her push/PR'da çalışır
- Backend ve frontend'i test eder
- Syntax hataları bulur

**Neler yapar?**
- ✅ Python bağımlılıklarını yükler
- ✅ Playwright'ı kurur  
- ✅ Frontend build'ini yapar
- ✅ .env'nin .gitignore'da olduğunu kontrol eder

### 2. **Deploy Pipeline** (`.github/workflows/deploy.yml`)
- Manuel çalıştırırsın (`workflow_dispatch`)
- Release yayınlandığında otomatik çalışır

**Neler yapar?**
- ✅ Secrets'ı yükler (gizli yapıyla)
- ✅ SMTP credentials'ı doğrular
- ✅ Deployment'a hazır kontrol eder

---

## 📊 Actions Sekmesinde Yapılanları Görmek

1. GitHub'da reponuza gidin
2. **Actions** sekmesine tıklayın
3. Çalışan/tamamlanan job'ları göreceksiniz

**Logs'larda neler göreceksiniz?**
```
✓ Backend dependencies validated
✓ Frontend build successful
✓ Credentials loaded from GitHub Secrets
✓ Ready for deployment
```

**Secrets RAT gösterilmeyecektir: `SMTP_PASS: ***`**

---

## 🔒 Güvenlik İpuçları

### ✅ Yapılması Gerekenler:
- [ ] secrets'ları regular olarak değiştir
- [ ] email hesabında 2FA aç
- [ ] Gmail App Password yerine normal password kullanma
- [ ] Repository'yi private tut (başkaları görmemiş olsun)

### ❌ Yapılmaması Gerekenler:
- Hiçbir zaman .env'yi commit etme (`.gitignore` kontrol et)
- Credentials'ı code'da hardcode etme
- Secret'ları repository description'ında yazmayma
- Shared email account kullanmayma (ayrı email aç)

---

## 🚨 Sorun Giderme

### "Workflow başlamıyor"
```bash
# .github/workflows/ klasörünün var mı kontrol et
ls -la .github/workflows/

# Eğer yok, oluştur ve push yap:
git add .github/
git commit -m "Add GitHub Actions workflows"
git push
```

### "SMTP authentication failed"
- [ ] Gmail 2FA'nı aç
- [ ] App Password'ü (normal password değil) kullan
- [ ] GitHub Secrets'ta doğru girdiğini kontrol et (boşluk yok mu?)

### "Secrets not found"
- [ ] Repository Settings → Secrets sekmesine git
- [ ] Secrets'ı doğru isimleriyle ekle (`SMTP_USER`, `SMTP_PASS` vs.)
- [ ] Repository'ye push yaptıktan sonra wait et (1-2 dakika)

---

## 📧 Ayrı Email Açma (Önerilir)

Eğer production email'ini GitHub'daki workflow'lardan ayırmak istersen:

1. Yeni Gmail hesabı aç: `trackmant-alerts@gmail.com`
2. 2FA aktif et
3. App Password oluştur
4. GitHub Secrets'ta `SMTP_USER` olarak bunu kullan
5. Emails şundan gelecek: `TRACKMANT <trackmant-alerts@gmail.com>`

**Avantajları:**
- ✓ Production email'i workflow'lardan izole et
- ✓ Alert emails'ı ayrı klasörde toplayabilirsin
- ✓ Eğer hacklerse, sadece alert hesabı etkilenir
- ✓ Team'deki herkes aynı credentials kullanabilir

---

## 🎯 Sonra Ne?

Workflow'lar kurulduktan sonra:

1. Backend ve frontend otomatik test edilecek
2. Deploy workflow'ı manual çalıştırabileceksin
3. Logs'tan hataları görebileceksin
4. Production'da confidence'la deploy edebileceksin

**Test için:**
```bash
# Bir değişiklik yap ve push et:
echo "# Test" >> README.md
git add README.md
git commit -m "test: trigger CI"
git push

# GitHub → Actions sekmesine git ve workflow'u izle
```

---

## 📚 Kaynaklar

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [managing-secrets-for-your-organization](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
