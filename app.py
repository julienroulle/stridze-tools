from sqladmin import Admin, ModelView
from starlette.applications import Starlette

from stridze.db import engine
from stridze.db.models import Activity, Lap, Record, User

app = Starlette(debug=True)
admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"

    column_list = [User.id, User.first_name, User.last_name, User.email]


admin.add_view(UserAdmin)


class ActivityAdmin(ModelView, model=Activity):
    column_list = [
        Activity.id,
        Activity.activity_type,
        Activity.start_time,
        Activity.distance,
        Activity.duration,
        Activity.user,
    ]


admin.add_view(ActivityAdmin)


class LapAdmin(ModelView, model=Lap):
    column_list = [
        Lap.id,
        Lap.timestamp,
        Lap.total_elapsed_time,
        Lap.total_distance,
        Lap.activity,
    ]


admin.add_view(LapAdmin)


class RecordAdmin(ModelView, model=Record):
    column_list = [
        Record.id,
        Record.timestamp,
        Record.distance,
        Record.lap,
        Record.activity,
    ]


admin.add_view(RecordAdmin)
