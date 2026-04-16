# Raspberry Pi — Capteurs Lumière & Son

Lit les capteurs de lumière (A1) et de son (A0) via un GrovePi et publie les mesures sur un broker MQTT.

---

## Flasher le Raspberry Pi

Une image préconfigurée est fournie : `buster_new_firmware_raspbian_for_robots.img`

Avec **Raspberry Pi Imager** : choisir "image personnalisée" et sélectionner le `.img`.

Avec `dd` :
```bash
sudo dd if=buster_new_firmware_raspbian_for_robots.img of=/dev/sdX bs=4M status=progress
```
> Remplacer `/dev/sdX` par le bon périphérique (vérifier avec `lsblk`).

---

## Déploiement

1. Copier `light_and_sound.py` sur le Pi et ajuster l'IP du broker si besoin (`BROKER = "..."`)
2. Installer le service systemd :
```bash
sudo cp light_and_sound.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now light_and_sound
```

---

## Fonctionnement du code

- **`get_Value()`** — effectue 5 lectures sur chaque capteur et fait la moyenne. La lumière est convertie en lux (0–1000), le son en décibels (`20 × log10`).
- **`check_alert()`** — encode une alerte directement dans la valeur via le bit de parité : impair = alerte active (son ≥ 55 dB, lumière ≥ 700 lux).
- **`main()`** — connecte au broker MQTT avec l'adresse MAC comme identifiant, puis publie en boucle sur le topic `device/LS` au format JSON (MAC, timestamp UTC, LIGHT, SOUND).
