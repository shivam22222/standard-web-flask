from datetime import datetime, timedelta
import requests

from sqlalchemy.sql import func
import rollbar

from standardweb import app, celery, db
from standardweb.lib import minecraft_uuid
from standardweb.models import AuditLog, Player, PlayerStats


def paged_query(query, limit=None):
    offset = 0
    if limit is None:
        limit = 100

    while True:
        rows = query.offset(offset).limit(limit).all()

        if not rows:
            return

        yield rows

        offset += limit


@celery.task()
def schedule_checks():
    # check latest username for players that have been offline for at least a day
    query = db.session.query(
        Player.uuid
    ).join(
        PlayerStats
    ).group_by(
        Player.uuid
    ).having(
        func.max(PlayerStats.last_seen) < datetime.utcnow() - timedelta(days=1)
    ).order_by(Player.id)

    rollbar.report_message('Checking %d uuids for username changes' % query.count(), level='info')

    i = 0
    # group uuid checks in groups of 100 every 100 seconds
    for rows in paged_query(query):
        player_uuids = [x.uuid for x in rows]

        check_uuids.apply_async(
            args=(player_uuids,),
            countdown=i * 100
        )

        i += 1


@celery.task()
def check_uuids(player_uuids):
    num_changed = 0

    for uuid in player_uuids:
        player = Player.query.filter_by(uuid=uuid).first()
        stats = PlayerStats.query.filter_by(player=player, server_id=app.config.get('MAIN_SERVER_ID'))

        if stats.last_seen > datetime.utcnow() - timedelta(days=1):
            # ignore players that have joined since the job started
            continue

        try:
            actual_username = minecraft_uuid.lookup_latest_username_by_uuid(uuid)
        except requests.RequestException as e:
            rollbar.report_message('Exception looking up uuid, skipping group', level='warning', extra_data={
                'num_changed': num_changed,
                'exception': unicode(e)
            })
            return

        if actual_username != player.username:
            player.set_username(actual_username)
            player.save(commit=False)

            num_changed += 1

    db.session.commit()

    rollbar.report_message('Finished checking uuid group', level='info', extra_data={
        'num_changed': num_changed
    })
