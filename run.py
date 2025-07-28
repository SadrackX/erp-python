# -*- coding: utf-8 -*-
from app import create_app
import threading
from app.services.tasks import iniciar_agendador

t = threading.Thread(target=iniciar_agendador)
t.daemon = True
t.start()

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
    