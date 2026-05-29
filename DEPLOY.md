# Деплой через systemd

Замена запуска через Docker на системный сервис `systemd`.
Порт: `9000` (uvicorn). Рабочая директория: `/root/docs-api`. Пользователь: `root`.

## Установка

```bash
# 1. Скопировать код в /root/docs-api (main.py, config.py, s3_client.py,
#    requirements.txt, contract_template.docx, .env)

# 2. Создать виртуальное окружение и поставить зависимости
cd /root/docs-api
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# 3. Установить и запустить сервис
cp docs-api.service /etc/systemd/system/docs-api.service
systemctl daemon-reload
systemctl enable --now docs-api
```

## Управление

```bash
systemctl status docs-api      # статус
systemctl restart docs-api     # перезапуск (после обновления кода)
systemctl stop docs-api        # остановить
journalctl -u docs-api -f      # логи в реальном времени
```
