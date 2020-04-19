from data.db_session import global_init, create_session
from data.__all_models import Privilege, Server

global_init('db/db.sqlite')
session = create_session()

admin = Privilege(name='admin', admin=1, playable=1)
player = Privilege(name='user')
banned = Privilege(name='banned', admin=0, playable=0)
session.add(admin)
session.add(player)
session.add(banned)
session.commit()

"""session.add(Server(ip='127.0.0.1:2000'))
session.commit()"""