# Smart Home w wersji Rasberry Pi
Moja praca inżynierska tworzona z myślą o wygodnym zarządzaniu modułami. Zarządzanie domem przez jedno środowisko.

##### Uruchomienie backendu
W katalogu `backend` należy uruchomić plik `install.py` poleceniem `sudo python3 install.py`. Pobierze on niezbędne moduły oraz utworzy plik konfiguracyjny `settings.json`. Uruchomienie środowiska odbywa się przez komendę `sudo python3 main.py`. Na start utworzona zostanie baza danych z użytkownikiem domyślnym admin admin.

##### Uruchomienie frontendu
Przed uruchomieniem Vue należy wprowadzić w pliku `axios.js` ścieżkę bazową do serwera Flask.
W katalogu `frontend` należy wykonać polecenie `sudo npm i`, uzupełni to brakujące biblioteki. Uruchomienie nastąpi po wpisaniu komendy `sudo npm run serve`.

##### Rozwój projektu
Zmiany można śledzić na moim profilu `Yamiko7x` w sewisie GitHub. Link: https://github.com/Yamiko7x