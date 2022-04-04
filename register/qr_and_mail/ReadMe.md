# Technobank: Mail Sending

## summary

For each participant we are doing following:
- read it from `spisak.xlsx`
- generate "id" as base64 encoded participant's email
- generate QR code that contains URL with the "id"
- send it to the participant via email as attachment

## how to

```
python -u main.py
```