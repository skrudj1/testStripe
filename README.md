testStripe

django 4.2 + stripe checkout. товары item, заказ order на несколько штук, discount/tax если надо. валюта у item usd или eur, ключи в env две пары STRIPE_*_USD и STRIPE_*_EUR (можно одинаковые с одного stripe аккаунта).

запуск

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

дальше в .env свои sk_test pk_test из stripe dashboard test mode. потом migrate и runserver.

python manage.py migrate
python manage.py runserver

корень http://127.0.0.1:8000/ выдает json со ссылками. админка /admin/ товар /item/1/ и тд по id.

суперюзер для проверки делал логин asd пароль asd (createsuperuser). на render после деплоя база пустая — там в shell опять createsuperuser, можно те же креды. пароль потом поменять если репо публичный.

ручки

/buy/<id>/ session_id json
/item/<id>/ страница с buy
/buy/order/<id>/ и /order/<id>/ для заказа

curl http://127.0.0.1:8000/item/1

.env в git не коммитим

docker: docker compose up --build

render: render.com web service + docker из корня, env из .env.example, SQLITE_PATH=/app/data/db.sqlite3. хосты для stripe — см. код (RENDER_EXTERNAL_HOSTNAME подхватывается). если free без shell: BOOTSTRAP_ADMIN_USER=asd BOOTSTRAP_ADMIN_PASSWORD=asd в environment, деплой, логин в админку, потом эти две переменные удали.

папки: stripe_demo настройки, items логика, templates/items html.

