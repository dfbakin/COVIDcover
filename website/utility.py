from data.db_session import global_init, create_session
from data.__all_models import Privilege, User

global_init('db/db.sqlite')
session = create_session()
admin = Privilege(id=1, name='admin', admin=1)
user = Privilege(id=2, name='user')
banned = Privilege(id=3, name='banned', playable=0)
session.add(admin)
session.add(user)
session.add(banned)
session.commit()

adm_user = User(email='admin@admin.com', privilege=1, username='Admin')
adm_user.set_password('__admin__')
session.add(adm_user)
session.commit()
