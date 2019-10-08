Muria
=====

Falcon boilerplate for API development

Instalasi
---------
Duplikat reponya
```
$git clone https://github.com/xakiy/muria.git
```

Install package dependensinya
- kalau perlu buat environment, bisa dengan virtualenv, atau pyenv
```
$pip install -r requirement-devel.txt
```

Sebelum itu Anda akan perlu meng-export env MURIA_SETUP seperti:
 
```
$export MURIA_SETUP=/home/linux_user/config/muria.ini
```

Dan Anda bisa menyiapkannya dengan cara:
1. Copy file ```settings.ini```, di folder ```tests```, silahkan modifikasi sesuai kebutuhan
2. <del>Bila perlu jangan lupa buat file ssl-nya</del>
3. Lalu letakkan di folder yang Anda mau <del>beserta file ssl-nya</del>
4. Umpama Anda letakkan di ```/home/linux_user/.config/muria.ini```, maka export-nya seperti contoh di awal tadi.

Kemudian Anda bisa menjalankan servernya dengan perintah:
```
$gunicorn --reload muria.wsgi:app
```

Kontribusi
----------
Aplikasi masih dalam pengembangan intensif, bila Anda berminat untuk berkontribusi silahkan ajukan PR.
