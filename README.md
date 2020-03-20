Muria
=====

[![Build Status](https://travis-ci.com/xakiy/muria.svg?branch=master)](https://travis-ci.org/xakiy/muria) [![codebeat badge](https://codebeat.co/badges/d67c212f-c32c-4498-b0d8-252fb1edd26c)](https://codebeat.co/projects/github-com-xakiy-muria-develop) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Falcon boilerplate for API development with pony ORM

Fitur
-----
Via (built-in) modified middlewares
* Strict HTTPS (based on https://github.com/falconry/falcon-require-https)
* CORS (based on https://github.com/lwcolton/falcon-cors)
* Authentication with JWT (based on https://github.com/loanzen/falcon-auth)
* Authorization with RBAC (Depends on JWT Auth, based on https://github.com/falconry/falcon-policy)
* Basic 12 factor configuration

Fitur Lain
----------
* Database storage(Postgres, MySQL/MariaDB, SQLite) using Pony ORM
* Simple memcache support
* Heroku deployment ready

Instalasi
---------
Silahkan duplikat repo ini dari
```
$git clone https://github.com/xakiy/muria.git
```

Install `paket-paket` pendukungnya.
Dianjurkan membuat python environment terlebih dahulu, baik dengan virtualenv,
atau pyenv.
```
$pip install -r requirements-dev.txt
```

Aplikasi ini diatur melalui sebuah `file` konfigurasi yang bisa Anda contek dari
`tests/settings.ini`, ubah dan sesuaikan menurut kebutuhan. Caranya, pilih salah
satu `section`, yaitu bagian yang ada dalam kurung kotak, seperti `[TEST],
[POSGRESQL] atau [MYSQL]`, atau Anda bisa membuat `section` yang baru.

Atur paramater-parameter yang Anda butuhkan dan letakkan di bawah `section` yang
akan Anda gunakan. Seperti, bila Anda memiliki parameter berbeda untuk
`cache_provider` bisa Anda letakkan ke bawah `section` yang baru tersebut,
begitu juga untuk parameter-parameter lainnya.

Simpan `file` konfigurasi tersebut di tempat yang Anda kehendaki,
dan export `file path`-nya ke dalam variabel `MURIA_CONFIG`,
dan `section`-nya ke dalam variabel `MURIA_MODE`, seperti:
```
$export MURIA_CONFIG=/home/user/api.konfigurasi.ini
$export MURIA_MODE=MYSQL  # sesuaikan dengan section yang Anda buat tadi
```

Terakhir Anda bisa menjalankannya dengan perintah:
```
$gunicorn --reload muria.wsgi:app
```

Kontribusi
----------
Aplikasi masih dalam pengembangan intensif, bila Anda berminat untuk
berkontribusi silahkan ajukan PR dan siapkan test terkait PR Anda.
Terima kasih.

