Muria
=====

[![Build Status](https://travis-ci.com/xakiy/muria.svg?branch=master)](https://travis-ci.org/xakiy/muria) [![codebeat badge](https://codebeat.co/badges/d67c212f-c32c-4498-b0d8-252fb1edd26c)](https://codebeat.co/projects/github-com-xakiy-muria-develop) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Falcon boilerplate for API development with pony ORM

Instalasi
---------
Silahkan duplikat repo ini
```
$git clone https://github.com/xakiy/muria.git
```

Install package dependensinya
- silahkan buat python environment bila belum ada, bisa dengan virtualenv, atau pyenv
```
$pip install -r requirements-dev.txt
```
Siapkan `file` konfigurasi baru yang bisa Anda contek dari `tests/settings.ini`,
ubah dan sesuaikan menurut kebutuhan. Caranya, pilih salah satu `section`, yaitu
bagian yang ada dalam kurung kotak, seperti `[TEST], [POSGRESQL] atau [MYSQL]`,
atau Anda bisa membuat `section` yang baru.

Atur paramater-parameter yang Anda butuhkan dan letakkan di bawah `section` yang
akan Anda gunakan. Seperti, bila Anda memiliki parameter berbeda untuk `cache_provider`
bisa Anda pindahkan ke bawah `section` yang baru Anda buat, begitu juga untuk parameter-
parameter lainnya.

Bila sudah selesai, simpan `file` konfigurasi tersebut di tempat yang Anda kehendaki.

Setelah itu, export lokasi `file` konfigurasi tadi ke dalam variabel
`MURIA_CONFIG`, dan `section`-nya ke dalam variabel `MURIA_MODE`, seperti:
```
$export MURIA_CONFIG=/home/user/api.konfigurasi.ini
$export MURIA_MODE=MYSQL  # sesuaikan dengan section yang Anda buat tadi
```

Kemudian Anda bisa menjalankan aplikasinya dengan perintah:
```
$gunicorn --reload muria.wsgi:app
```

Kontribusi
----------
Aplikasi masih dalam pengembangan intensif, bila Anda berminat untuk berkontribusi silahkan ajukan PR dan siapkan test terkait PR Anda.
