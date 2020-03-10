Muria
=====

[![Build Status](https://travis-ci.com/xakiy/muria.svg?branch=develop)](https://travis-ci.org/xakiy/muria) [![codebeat badge](https://codebeat.co/badges/d67c212f-c32c-4498-b0d8-252fb1edd26c)](https://codebeat.co/projects/github-com-xakiy-muria-develop) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Falcon boilerplate for API development with pony ORM

Instalasi
---------
Duplikat reponya
```
$git clone https://github.com/xakiy/muria.git
```

Install package dependensinya
- silahkan buat environment, bisa dengan virtualenv, atau pyenv
```
$pip install -r requirements-dev.txt
```

Sebelum itu Anda akan perlu meng-export env MURIA_SETUP seperti:
 
```
$export MURIA_SETUP=/home/linux_user/config/muria.ini
```

Berkas konfigurasi tersebut bisa Anda siapkan dengan cara:
1. Copy file ```settings.ini```, di folder ```tests```, silahkan modifikasi sesuai kebutuhan
2. Lalu letakkan di folder yang Anda mau <del>beserta file ssl-nya</del>
4. Umpama Anda letakkan di ```/home/linux_user/.config/muria.ini```, maka export-nya seperti contoh peetama tadi.

Kemudian Anda bisa menjalankan servernya dengan perintah:
```
$gunicorn --reload muria.wsgi:app
```

Kontribusi
----------
Aplikasi masih dalam pengembangan intensif, bila Anda berminat untuk berkontribusi silahkan ajukan PR dan buatkan test untuk fitur baru yang Anda buat.
